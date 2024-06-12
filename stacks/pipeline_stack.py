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
    aws_codebuild as codebuild,
    aws_chatbot as chatbot
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
            pipeline_name="sscheck-backend",
        )

        # Fetch github repository for changes
        code_pipeline_source = pipelines.CodePipelineSource.connection(
            repo_string="umccr/samplesheet-check-backend",
            branch=props["branch_source"][app_stage],
            connection_arn=codestar_arn,
            trigger_on_push=True
        )

        # Create A pipeline for cdk stack and react build
        self_mutate_pipeline = pipelines.CodePipeline(
            self,
            "CodePipeline",
            docker_enabled_for_synth=True,
            self_mutation=True,
            code_pipeline=sscheck_backend_pipeline,
            synth=pipelines.ShellStep(
                "CDKShellScript",
                input=code_pipeline_source,
                commands=[
                    # Synth CDK
                    "yarn cdk synth",

                    # Lambda unit test
                    "cd src",
                    "python -m unittest discover utils -v",
                    "python -m unittest discover samplesheet -v",
                ],
                install_commands=[
                    "make install",
                    "docker -v"
                ],
                primary_output_directory="cdk.out"
            ),
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=codebuild.BuildEnvironment(
                    build_image=codebuild.LinuxArmBuildImage.AMAZON_LINUX_2_STANDARD_3_0,
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

        # SSM parameter for AWS Slack Alerts Chatbot ARN
        chatbot_alerts_arn = ssm.StringParameter.from_string_parameter_attributes(
            self,
            "ChatbotAlertsARN",
            parameter_name="/ chatbot/slack/umccr/alerts-arn"
        ).string_value

        chatbot_slack_alerts = chatbot.SlackChannelConfiguration.from_slack_channel_configuration_arn(
            self,
            'SlackAlertsChannelConfiguration',
            chatbot_alerts_arn
        )

        # Add Chatbot Notification
        self_mutate_pipeline.pipeline.notify_on(
            "SlackNotificationSscheckBackEndPipeline",
            target=chatbot_slack_alerts,
            events=[
                codepipeline.PipelineNotificationEvents.PIPELINE_EXECUTION_FAILED,
                codepipeline.PipelineNotificationEvents.PIPELINE_EXECUTION_SUCCEEDED
            ],
            detail_type=codestarnotifications.DetailType.BASIC,
            enabled=True,
            notification_rule_name="SlackNotificationSscheckBackEndPipeline")
