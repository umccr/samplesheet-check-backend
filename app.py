#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from pipelines.cdkpipeline import CdkPipelineStack

account_id = os.environ.get('CDK_DEFAULT_ACCOUNT')
aws_region = os.environ.get('CDK_DEFAULT_REGION')
aws_env = {'account': account_id , 'region': aws_region}

 
app = cdk.App()

CdkPipelineStack(
  app,
  "SampleSheetBackEndCdkPipeline",
  stack_name = "cdkpipeline-sscheck-back-end-dev",
  env=aws_env,
  tags={
    "environment":"dev",
    "stack":"cdkpipeline-sscheck-back-end-dev"
  }
)

app.synth()
