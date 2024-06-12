
# samplesheet-check-backend

Project is the samplesheet check for the UMCCR backend and infrastructure.

The project contains the `app.py` which is the main function of the app and directories:

- *src* -  the lambdas source code lives
- *stacks* - the stack for which the code is structured at AWS


# Setting up

It is recommended to create a virtual environment for the app.

To do so please follow the instructions below.

Change your directory to the root of this readme file.  

Create a virtual environment for the app.

```sh
virtualenv .venv --python=python3.11
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```sh
source .venv/bin/activate
```

Install all dependencies

```sh
make install
```

# Stack Deployment

**Prerequisite**

- A valid SSL Certificate in `us-east-1` region at ACM for all the domain name needed. See [here](app.py#L33) (`alias_domain_name` on the props variable) on what domain needs to be included, determined based on which account is deployed.
- SSM Parameter for the certificate ARN created above with the name of `/sscheck/api/ssl_certificate_arn`

_Deploying the _stack without _the _prerequisite__ above may_ result in a stack rollback_

There are 2 stacks in this application:
- *SSCheckBackEndCdkPipeline/SampleSheetCheckBackEndStage/SampleSheetCheckBackEnd* - Contains the applications stack
- *SSCheckBackEndCdkPipeline* - Contains the pipeline for the stack to run and self-update

To deploy the application stack, you will need to deploy the `pipeline` stack. The pipeline stack will take care of the application stack.

Deploy pipeline stack

```sh
cdk deploy SSCheckBackEndCdkPipeline --profile=${AWS_PROFILE}
```

## Starting API locally

Prerequisite:
```
sam --version
SAM CLI, version 1.100.

cdk --version
2.114.1 (build 02bbb1d)
```

The local start could configure the domain name for the metadata lookup. Currently, it is pointing to `localhost:8000`
where the data-portal-api operates locally, but alternatively, you could change and point to the remote domain name
(e.g. `api.portal.dev.umccr.org` or `api.portal.prod.umccr.org`). This can be done on the `local-start-env-var.json`
file located at the root of the directory. The appropriate bearer token when calling this local endpoint to make use of
the remote metadata endpoint.

To start simply use the makefile to start a local api running in `localhost:8001`. Run:
```make start```

You could call this endpoint with the following command.
```curl
curl --location 'http://127.0.0.1:8001/' \
--header 'Authorization: Bearer ${TOKEN}' \
--form 'file=@"/the/samplesheet/path"' \
--form 'logLevel="ERROR"'
```

You could import this to [Postman](https://www.postman.com/) and take advantage of the UI to select the appropriate SampleSheet file.


## Deploying sscheck_backend_stack from local

You can deploy the cdk with the following command

```
$ cdk deploy SSCheckBackEndCdkPipeline/SampleSheetCheckBackEndStage/SampleSheetCheckBackEnd --profile=${AWS_PROFILE}
```

## Syncing Google Sheet to Lab Metadata

This is done every 24 hours (overnight), however, if one needs to update the lab metadata on demand, the following code may be of assistance.  

Ensure you're logged in to the right AWS account and then run the following code: 

```bash
aws lambda invoke \
  --function-name data-portal-api-prod-labmetadata_scheduled_update_processor \
  --output json \
  output.json
```