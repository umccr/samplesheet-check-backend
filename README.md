
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