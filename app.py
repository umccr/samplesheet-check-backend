#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

# Import cdk pipeline stack
from stacks.pipeline_stack import PipelineStack
from stacks.predeployment_stack import PredeploymentStack

# Account environment and region
account_id = os.environ.get('CDK_DEFAULT_ACCOUNT')
aws_region = os.environ.get('CDK_DEFAULT_REGION')

# Determine account stage (Identify if it is running on prod or dev)
if account_id == "472057503814":  # Account number used for production environment
    app_stage = "prod"
else:
    app_stage = "dev"


props = {
    "pipeline_name": {
        "dev": "sscheck-backend",
        "prod": "sscheck-backend"
    },
    "pipeline_artifact_bucket_name" :{
        "dev": "sscheck-backend-artifact-dev",
        "prod": "sscheck-backend-artifact-prod"
    },
    "repository_source": "umccr/samplesheet-check-backend",
    "branch_source": {
        "dev": "dev",
        "prod": "main"
    },
    "alias_domain_name":{
        "dev": ["api.sscheck.dev.umccr.org"],
        "prod": ["api.sscheck.umccr.org", "api.sscheck.prod.umccr.org"]
    }
}

app = cdk.App(
    context={
        "app_stage": app_stage,
        "props": props
    }
)

PipelineStack(
  app,
  "SSCheckBackEndCdkPipeline",
  stack_name = "sscheck-backend-pipeline",
  tags={
    "sstage": app_stage,
    "stack":"sscheck-backend-pipeline"
  }
)

""" 
The Predeployment stack are meant to be run once, before the pipeline stack is deployed.
Failure to do so may result in a stack rollback on the pipeline stack.
NOTE: Please Validate SSL Certificate from predeployment stack thorugh console. (for prod account)
"""
PredeploymentStack(
    app,
    "SSCheckBackEndPredeploymentStack",
    stack_name="sscheck-backend-predeployment",
    tags={
        "stage": app_stage,
        "stack": "sscheck-backend-predeployment"
    }
)

app.synth()
