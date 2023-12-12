from constructs import Construct
from aws_cdk import (
    Stage,
    Stack,
    RemovalPolicy,
    aws_ssm as ssm,
    pipelines,
    aws_s3 as s3,
    aws_codepipeline as codepipeline,
    aws_sns as sns,
    aws_codestarnotifications as codestarnotifications,
    aws_codebuild as codebuild
)
from stacks.sscheck_backend_stack import SampleSheetCheckBackEndStack


class SampleSheetCheckBackEndStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        app_stage = self.node.try_get_context("app_stage")

        # Create stack defined on stacks folder
        SampleSheetCheckBackEndStack(
            self,
            "SampleSheetCheckBackEnd",
            stack_name="sscheck-backend-stack",
            tags={
                "stage": app_stage,
                "stack": "sscheck-backend-stack"
            }
        )


# Class for the CDK pipeline stack
class PipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Defining app stage
        app_stage = self.node.try_get_context("app_stage")
        props = self.node.try_get_context("props")

        # Load SSM parameter for GitHub repo (Created via Console)
        codestar_arn = ssm.StringParameter.from_string_parameter_attributes(self, "codestarArn",
                                                                            parameter_name="codestar_github_arn"
                                                                            ).string_value

        # Create S3 bucket for artifacts
        pipeline_artifact_bucket = s3.Bucket(
            self,
            "sscheck-backend-artifact-bucket",
            bucket_name=props["pipeline_artifact_bucket_name"][app_stage],
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create a pipeline for status page
        sscheck_backend_pipeline = codepipeline.Pipeline(
            self,
            "SSCheckBackEndPipeline",
            artifact_bucket=pipeline_artifact_bucket,
            restart_execution_on_update=True,
            cross_account_keys=False,
            pipeline_name=props["pipeline_name"][app_stage],
        )

        # Fetch github repository for changes
        code_pipeline_source = pipelines.CodePipelineSource.connection(
            repo_string=props["repository_source"],
            branch=props["branch_source"][app_stage],
            connection_arn=codestar_arn,
            trigger_on_push=True
        )

        # Create A pipeline for cdk stack and react build
        self_mutate_pipeline = pipelines.CodePipeline(
            self,
            "CodePipeline",
            code_pipeline=sscheck_backend_pipeline,
            synth=pipelines.ShellStep(
                "CDKShellScript",
                input=code_pipeline_source,
                commands=[
                    "for dir in $(find ./src/layers/ -maxdepth 1 -mindepth 1 -type d); do /bin/bash ./build_lambda_layers.sh ${dir}; done",

                    # CDK lint test
                    "cdk synth",
                    "mkdir ./cfnnag_output",
                    "for template in $(find ./cdk.out -type f -maxdepth 2 -name '*.template.json'); do cp $template ./cfnnag_output; done",
                    "cfn_nag_scan --input-path ./cfnnag_output",

                    # Lambda testing
                    "cd src",
                    "pip install -r layers/runtime/requirements.txt",
                    "pip install layers/utils/",
                    "cd layers/utils",
                    "python -m unittest utils/tests/test_api.py",
                    "python -m unittest utils/tests/test_samplesheet.py",
                    "cd ../../samplesheet",
                    "python -m unittest tests/*",
                    "cd ../.."
                ],
                install_commands=[
                    "npm install -g aws-cdk",
                    "gem install cfn-nag",
                    "pip install -r requirements.txt",
                    "docker -v"
                ],
                primary_output_directory="cdk.out"
            ),
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                    privileged=True
                )
            )
        )

        # Deploy infrastructure
        self_mutate_pipeline.add_stage(
            SampleSheetCheckBackEndStage(
                self,
                "SampleSheetCheckBackEndStage"
            )
        )

        self_mutate_pipeline.build_pipeline()

        # SSM parameter for AWS SNS ARN
        data_portal_notification_sns_arn = ssm.StringParameter.from_string_parameter_attributes(
            self,
            "DataPortalSNSArn",
            parameter_name="/data_portal/backend/notification_sns_topic_arn"
        ).string_value

        # SNS chatbot
        data_portal_sns_notification = sns.Topic.from_topic_arn(
            self,
            "DataPortalSNS",
            topic_arn=data_portal_notification_sns_arn
        )

        # Add Chatbot Notificaiton
        self_mutate_pipeline.pipeline.notify_on(
            "SlackNotificationSscheckBackEndPipeline",
            target=data_portal_sns_notification,
            events=[
                codepipeline.PipelineNotificationEvents.PIPELINE_EXECUTION_FAILED,
                codepipeline.PipelineNotificationEvents.PIPELINE_EXECUTION_SUCCEEDED
            ],
            detail_type=codestarnotifications.DetailType.BASIC,
            enabled=True,
            notification_rule_name="SlackNotificationSscheckBackEndPipeline")
