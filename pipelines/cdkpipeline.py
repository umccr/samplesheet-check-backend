# importing modules
from aws_cdk import (
    aws_ssm as ssm,
    pipelines,
    core as cdk,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild
)
from stacks.sscheck_backend_stack import SampleSheetCheckBackEndStack

class SampleSheetCheckBackEndStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create stack defined on stacks folder
        SampleSheetCheckBackEndStack(
            self,
            "SampleSheetCheckBackEnd",
            stack_name="sscheck-back-end-stack"
        )

# Class for the CDK pipeline stack
class CdkPipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Load SSM parameter for GitHub repo (Created via Console)
        codestar_arn = ssm.StringParameter.from_string_parameter_attributes(self, "codestarArn",
            parameter_name="codestar_github_arn"
        ).string_value

        cloud_artifact = codepipeline.Artifact(
            artifact_name="sscheck_pipeline_cloud"
        )

        source_artifact = codepipeline.Artifact(
            artifact_name="sscheck_pipeline_source",
        )

        # Fetch github repository for changes
        code_star_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            connection_arn = codestar_arn,
            output = source_artifact,
            owner = "umccr",
            repo = "samplesheet-check-backend",
            branch = "dev",
            action_name = "Source"
        )


        # Create CDK pipeline
        pipeline = pipelines.CdkPipeline(
            self,
            "CDKSampleSheetCheckBackEndPipeline",
            cloud_assembly_artifact = cloud_artifact,
            cross_account_keys =False,
            pipeline_name="sscheck-back-end",
            source_action = code_star_action,
            synth_action = pipelines.SimpleSynthAction(
                synth_command = "cdk synth",
                cloud_assembly_artifact = cloud_artifact,
                source_artifact = source_artifact,
                environment = codebuild.BuildEnvironment(
                    privileged=True
                ),
                install_commands = [
                    "npm install -g aws-cdk",
                    "gem install cfn-nag",
                    "pip install -r requirements.txt",
                    "docker -v"
                ],
                build_commands = [
                    "for dir in $(find ./lambdas/layers/ -maxdepth 1 -mindepth 1 -type d); do /bin/bash ./build_lambda_layers.sh ${dir}; done"
                ],
                test_commands = [
                    # CDK lint test
                    "cdk synth",
                    "mkdir ./cfnnag_output",
                    "for template in $(find ./cdk.out -type f -maxdepth 2 -name '*.template.json'); do cp $template ./cfnnag_output; done",
                    "cfn_nag_scan --input-path ./cfnnag_output",

                    # Lambda testing
                    "for dir in $(find layers/ -maxdepth 1 -mindepth 1 -type d); do pip install -r ${dir}/requirements.txt; done",
                    "cd layers",
                    "python -m unittest umccr_utils/tests/test_api.py",
                    "python -m unittest umccr_utils/tests/test_samplesheet.py",
                    "cd ../functions",
                    "python -m unittest tests/*",

                ],
                action_name = "Synth",
                project_name = "sscheck-back-end-synth",
            )

        )
            

        # Deploy infrastructure
        pipeline.add_application_stage(
            SampleSheetCheckBackEndStage(
                self,
                "SampleSheetCheckBackEndStage"
            )
        )


