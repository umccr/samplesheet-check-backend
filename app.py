#!/usr/bin/env python3
import os

from aws_cdk import App

# Import cdk pipeline stack
from stacks.pipeline_stack import PipelineStack

# Account environment and region
account_id = os.environ.get('CDK_DEFAULT_ACCOUNT')
aws_region = os.environ.get('CDK_DEFAULT_REGION')

# Determine account stage (Identify if it is running on prod, stg, or dev)
if account_id == "472057503814":  # Prod account
    app_stage = "prod"
elif account_id == "455634345446":  # Staging account
    app_stage = "stg"
else:
    app_stage = "dev"

props = {
    "pipeline_artifact_bucket_name": {
        "dev": "sscheck-backend-artifact-dev",
        "stg": "sscheck-backend-artifact-stg",
        "prod": "sscheck-backend-artifact-prod"
    },
    "branch_source": {
        "dev": "dev",
        "stg":  "stg",
        "prod": "main"
    },
    "alias_domain_name": {
        "dev": ["api.sscheck.dev.umccr.org"],
        "stg": ["api.sscheck.stg.umccr.org"],
        "prod": ["api.sscheck.umccr.org", "api.sscheck.prod.umccr.org"]
    }
}

app = App(
    context={
        "app_stage": app_stage,
        "props": props
    }
)

PipelineStack(
    app,
    "SSCheckBackEndCdkPipeline",
    stack_name="sscheck-backend-pipeline",
    tags={
        "stage": app_stage,
        "stack": "sscheck-backend-pipeline"
    }
)

app.synth()
