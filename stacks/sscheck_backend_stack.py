import os
from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_cognito as cognito,
    aws_ssm as ssm,
    aws_route53 as route53,
    aws_route53_targets as route53t,
    aws_certificatemanager as acm
)


class SampleSheetCheckBackEndStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Cognito parameters are from data portal terraform stack
        cog_user_pool_id = ssm.StringParameter.from_string_parameter_name(
            self,
            "CogUserPoolID",
            string_parameter_name="/data_portal/client/cog_user_pool_id",
        ).string_value

        # Load SSM parameter
        data_portal_domain_name = ssm.StringParameter.from_string_parameter_attributes(self, "urlValue",
                                                                                       parameter_name="/data_portal/backend/api_domain_name"
                                                                                       ).string_value

        # --- Query deployment env specific config from SSM Parameter Store
        hosted_zone_id = ssm.StringParameter.from_string_parameter_name(
            self,
            "HostedZoneID",
            string_parameter_name="/hosted_zone/umccr/id"
        ).string_value

        hosted_zone_name = ssm.StringParameter.from_string_parameter_name(
            self,
            "HostedZoneName",
            string_parameter_name="/hosted_zone/umccr/name"
        ).string_value

        cert_use1_arn = ssm.StringParameter.from_string_parameter_name(
            self,
            "SSLCertUSE1ARN",
            string_parameter_name="/sscheck/api/ssl_certificate_arn",
        )

        cert_use1 = acm.Certificate.from_certificate_arn(
            self,
            "SSLCertUSE1",
            certificate_arn=cert_use1_arn.string_value,
        )

        # Create a lambda function along with the layered crated above
        sample_sheet_check_lambda = lambda_.DockerImageFunction(
            self,
            "SamplesheetValidationLambda",
            architecture=lambda_.Architecture.ARM_64,
            timeout=Duration.seconds(40),
            code=lambda_.DockerImageCode.from_image_asset(
                directory=os.path.abspath(os.path.join(os.path.dirname(__file__), '../')),
                file="src/Dockerfile",
                exclude=["cdk.out", ".venv", "venv"]
            ),
            memory_size=2048,
            environment={"data_portal_domain_name": data_portal_domain_name}
        )

        # Cors Configuration
        cors_config = apigateway.CorsOptions(
            allow_origins=['*'],
            allow_methods=["POST", "OPTIONS"]
        )

        # Create an apigateway to access the function
        api = apigateway.RestApi(
            self, "sample-sheet-validation-api",
            rest_api_name="Sample Sheet Validation",
            default_cors_preflight_options=cors_config,
            domain_name=apigateway.DomainNameOptions(
                domain_name="api.sscheck." + hosted_zone_name,
                certificate=cert_use1,
                endpoint_type=apigateway.EndpointType.EDGE
            ),
            deploy_options={
                "logging_level": apigateway.MethodLoggingLevel.INFO,
                "data_trace_enabled": True
            }
        )

        # Integrate the apigateway with the lambda function
        sampleSheetValidationIntegration = apigateway.LambdaIntegration(sample_sheet_check_lambda)

        # Pool Config
        cog_user_pool = cognito.UserPool.from_user_pool_id(
            self,
            "ExistingUserPool",
            cog_user_pool_id
        )

        # Authorizer config
        auth_config = apigateway.CognitoUserPoolsAuthorizer(self, "cognitoAuthorizer",
                                                            cognito_user_pools=[cog_user_pool],
                                                            authorizer_name="cognitoAuthorizer",
                                                            identity_source=apigateway.IdentitySource.header(
                                                                'Authorization')
                                                            )

        # add method of the function for the api gateway
        api.root.add_method("POST", sampleSheetValidationIntegration,
                            authorization_type=apigateway.AuthorizationType.COGNITO,
                            authorizer=auth_config
                            )

        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            "HostedZone",
            hosted_zone_id=hosted_zone_id,
            zone_name=hosted_zone_name,
        )

        route53_lambda_api = route53.ARecord(
            self,
            "CreateARecordLambdaApi",
            target=route53.RecordTarget(
                alias_target=route53t.ApiGateway(api)
            ),
            zone=hosted_zone,
            record_name="api.sscheck"
        )

        # Write SSM parameter for REST api URL
        ssm.StringParameter(self, "samplesheetCheckLambdaApi",
                            allowed_pattern=".*",
                            description="The Lambda Rest-api Samplesheet Check",
                            parameter_name="/sscheck/lambda-api-domain",
                            string_value=route53_lambda_api.domain_name,
                            tier=ssm.ParameterTier.STANDARD
                            )
