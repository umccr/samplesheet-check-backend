
# samplesheet-check-backend

Project is the samplesheet check for the UMCCR backend and infrastructure.

The project contains the `app.py` that is the main function of the app and directories:

- *lambdas* -  the lambdas source code lives
  - *functions* - the logic for the main function
  - *layers* - dependencies for the function code to run
- *stacks* - the stack for which the code is structured at AWS


# Setting up

It is recomended to create a virtual environment for the app.

To do so please follow the instruction below.

Change your directory to the root of this readme file.  

Create a virtual environment for the app.
```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you might try this:

```
% .venv\Scripts\activate.bat
```
Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

# Stack Deployment

**Prerequisite**
- A valid SSL Certificate in `us-east-1` region at ACM for all the domain name needed. See [here](app.py#L35) (`alias_domain_name` on the props variable) on what domain need to be included, determined based on which account is deployed.
- SSM Parameter for the certificate ARN created above with the name of `/sscheck/api/ssl_certificate_arn`

_Deploying the stack without prerequisite above may result in a stack rollback_

There are 2 stacks in this application:
- *data_portal_status_page* - Contains the applications stack
- *pipeline* - Contains the pipeline for the stack to run and self update


To deploy the application stack, you will need to deploy the `pipeline` stack. The pipeline stack will take care of the `sscheck_backend_stack` stack deployment.


Deploy pipeline stack
```
$ cdk deploy SSCheckBackEndCdkPipeline --profile=${AWS_PROFILE}
```

## Deploying sscheck_backend_stack from local

Before deploy the project layers **must** be compiled and zipped with the following command.

### Lambda layer requirement
This stack deploys Lambda layers to provide runtime code to the Lambda function. Consequently, the Lambda layers must be built prior to stack deployment. This is done by running `build_lambda_layers.sh` on each Lambda layer directory in `lambda/layers/`. Run the following command to meet the lambda layer requirements. [Docker is required]

```bash
for dir in $(find ./lambdas/layers/ -maxdepth 1 -mindepth 1 -type d); do
  ./build_lambda_layers.sh ${dir};
done
```
### Deploying the cdk

After successfully build, you can deploy the cdk with the following command

```
$ cdk deploy SSCheckBackEndCdkPipeline/SampleSheetCheckBackEndStage/SampleSheetCheckBackEnd --profile=${AWS_PROFILE}
```

## Syncing Google Sheet to Lab Metadata

This is done every 24 hours (overnight), however if one needs to update the lab metadata on demand, the following code may be of assistance.  

Ensure you're logged in to the right AWS account and then run the following code: 

```bash
aws lambda invoke \
  --function-name data-portal-api-prod-labmetadata_scheduled_update_processor \
  --output json \
  output.json
```

## Testing locally

This tutorial goes through running the samplesheet check functions locally.

This allows a user to debug the code on a failing or passing samplesheet.  

### Step 1: Create the conda env

Create a conda env / virtual env that you can deploy your requirements to

```bash
conda create --yes \
  --name samplesheet-check-backend \
  --channel conda-forge \
  pip \
  python==3.8
```

Install requirements into conda env / virtual env. 

```bash
conda activate samplesheet-check-backend

pip install -r lambdas/layers/requirements.txt
```

Set the PYTHONPATH env var to the layers directory so that the `umccr_utils` are
found.

```bash
mkdir -p "${CONDA_PREFIX}/etc/conda/activate.d"
echo '#!/usr/bin/env bash' > "${CONDA_PREFIX}/etc/conda/activate.d/umccr_utils.sh"
echo "export PYTHONPATH=\"${PWD}/lambdas/layers/:\$PYTHONPATH\"" >> "${CONDA_PREFIX}/etc/conda/activate.d/umccr_utils.sh"
```

Re-activate the conda env.  

```bash
conda deactivate
conda activate samplesheet-check-backend
```

### Step 2: Creating a testing script

In order to test our samplesheet, we need to run two separate functions in the samplesheet_check.py script: 
* `run_sample_sheet_content_check` which ensures that:
  * the samplesheet header has the right settings entered
  * none of the indexes clash within each lane set in the samplesheet. 
* `run_sample_sheet_check_with_metadata` which ensures that:
  * if the library id has a topup suffix, ensure the original sample already exists.
  * the assay and type in the labmetadata are set as expected.  :construction: # Not yet implemented
  * the override cycles in the metadata are consistent with the number of non-N bases in the indexes.
  * for each sample, the override cycles all suggest the same number of cycles for each read.  

An example shell script testing the samplesheet `samplesheet.csv` is shown below:

This script expects the user to have set the following environment variables:
  * `PORTAL_TOKEN` (can be obtained from the data.umccr.org home page)
  * `data_portal_domain_name` set to `api.data.prod.umccr.org` or `api.data.dev.umccr.org`

```bash
#!/usr/bin/env bash

: ' 
This script has three sections
1. Setup 
  - check the portal token env var 
  - check the samplesheet exists
  - check samplesheet_check.py exists
2. Call the run_sample_sheet_content_check function
3. Call the run_sample_sheet_check_with_metadata function
'

# Set to fail
set -euo pipefail

### USER ####

SAMPLESHEET_FILE="SampleSheet.csv" 

#############


## GLOBALS ##

SAMPLESHEET_CHECK_SCRIPT="lambdas/functions/samplesheet_check.py"
CONDA_ENV_NAME="samplesheet-check-backend"

#############


### SETUP ###

if [[ -z "${PORTAL_TOKEN-}" ]]; then
  echo "Error: Could not get the env var 'PORTAL_TOKEN'. Exiting" 1>&2
  exit 1
fi

if [[ -z "${data_portal_domain_name-}" ]]; then
  echo "Error: Could not get the env var 'data_portal_domain_name'. Exiting" 1>&2
  exit 1
fi

if [[ ! -f "${SAMPLESHEET_FILE}" ]]; then
  echo "Error: Could not find the file '${SAMPLESHEET_FILE}'" 1>&2
  exit 1
fi

if [[ ! -f "${SAMPLESHEET_CHECK_SCRIPT}" ]]; then
  echo "Error: Could not find the file '${SAMPLESHEET_CHECK_SCRIPT}'" 1>&2
  exit 1
fi

#############


### TESTS ###

python_file="$(mktemp)"

cat << EOF > "${python_file}"
#!/usr/bin/env python3

# Imports
from lambdas.functions.samplesheet_check import run_sample_sheet_content_check
from lambdas.functions.samplesheet_check import run_sample_sheet_check_with_metadata
from umccr_utils.samplesheet import SampleSheet

# Get auth header for portal
auth_header = "Bearer ${PORTAL_TOKEN}"

# Get samplesheet
sample_sheet_path = "${SAMPLESHEET_FILE}"
sample_sheet = SampleSheet(sample_sheet_path)

# Check 1
run_sample_sheet_content_check(sample_sheet)

# Check 2
async def set_and_check_metadata(sample_sheet, auth_header):
    # Set metadata
    loop = asyncio.get_running_loop()
    error = await asyncio.gather(
        sample_sheet.set_metadata_df_from_api(auth_header, loop),
    )
    
    # run metadta check
    run_sample_sheet_check_with_metadata(sample_sheet)
    
loop = asyncio.new_event_loop()
set_and_check_metadata(sample_sheet, auth_header):
loop.close()

    


EOF

echo "Running samplesheet '${SAMPLESHEET_FILE}' through check script '${SAMPLESHEET_CHECK_SCRIPT}'" 1>&2
conda run \
  --name "${CONDA_ENV_NAME}" \
  python3 "${python_file}"
  
echo "Test complete!" 1>&2
rm "${python_file}"

#############
```

## Testing through API

This goes through running the samplesheet check against the API.

This tests the deployed version of the samplesheet check, rather than the local file content.

You can use the curl binary to make a POST request to the API.  

This script expects the user to have the following environment variables:
  * `PORTAL_TOKEN` (can be obtained from the data.umccr.org home page)

```bash
API_URL="https://api.sscheck.prod.umccr.org"  # Dev URL: https://api.sscheck.dev.umccr.org
SAMPLESHEET_FILE="SampleSheet.csv"

curl \
  --location \
  --request POST \
  --header "Authorization: Bearer ${PORTAL_TOKEN}" \
  --form "logLevel=ERROR" \
  --form "file=@${SAMPLESHEET_FILE}" \
  "${API_URL}"
```

