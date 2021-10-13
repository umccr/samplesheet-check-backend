#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from pipelines.cdkpipeline import CdkPipelineStack
 
app = cdk.App()

CdkPipelineStack(
  app,
  "SampleSheetBackEndCdkPipeline",
  stack_name = "cdkpipeline-sscheck-back-end",
  tags={
    "stack":"cdkpipeline-sscheck-back-end"
  }
)

app.synth()
