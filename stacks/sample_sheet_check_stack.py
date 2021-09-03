from aws_cdk import (
    core as cdk,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_cognito as cognito,
    aws_ssm as ssm,
    aws_route53 as route53,
    aws_route53_targets as route53t,
    aws_certificatemanager as acm
)

class SampleSheetCheckStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Cognito parameters are from data portal terraform stack
        cog_user_pool_id = ssm.StringParameter.from_string_parameter_name(
            self,
            "CogUserPoolID",
            string_parameter_name="/data_portal/client/cog_user_pool_id",
        ).string_value

        # Load SSM parameter (created Via Console)
        data_portal_metadata_api = ssm.StringParameter.from_string_parameter_attributes(self, "urlValue",
            parameter_name="/sscheck/metadata-api"
        ).string_value

        # Query domain_name config from SSM Parameter Store (Created via Conosle)
        domain_name = ssm.StringParameter.from_string_parameter_name(
            self,
            "DomainName",
            string_parameter_name="/sscheck/domain",
        ).string_value

        # --- Query deployment env specific config from SSM Parameter Store
        hosted_zone_id = ssm.StringParameter.from_string_parameter_name(
            self,
            "HostedZoneID",
            string_parameter_name="hosted_zone_id"
        ).string_value

        hosted_zone_name = ssm.StringParameter.from_string_parameter_name(
            self,
            "HostedZoneName",
            string_parameter_name="hosted_zone_name"
        ).string_value
        
        cert_use1_arn = ssm.StringParameter.from_string_parameter_name(
            self,
            "SSLCertUSE1ARN",
            string_parameter_name="cert_use1_arn",
        )

        cert_use1 = acm.Certificate.from_certificate_arn(
            self,
            "SSLCertUSE1",
            certificate_arn=cert_use1_arn.string_value,
        )
        # Create a Lambda Layer
        sample_check_layer = lambda_.LayerVersion(
            self,
            "SamplecheckLambdaLayer",
            code=lambda_.Code.from_asset("lambdas/layers/umccr_utils/python38-umccr_utils.zip"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
            description="A samplecheck library layer for python 3.8"
        )

        # Create a lambda function along with the layered crated above
        sample_sheet_check_lambda = lambda_.Function(
            self,
            "SampleSheetValidationLambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            timeout=cdk.Duration.seconds(60),
            code=lambda_.Code.from_asset("lambdas/functions"),
            handler="main.lambda_handler",
            layers=[sample_check_layer],
            environment={"data_portal_metadata_api": data_portal_metadata_api}
        )

        # Cors Configuration
        cors_config = apigateway.CorsOptions(
            allow_origins = [ '*' ],
            allow_methods = ["POST", "OPTIONS"]
        )

        # Create an apigateway to access the function
        api = apigateway.RestApi(
            self, "sample-sheet-validation-api",
            rest_api_name = "Sample Sheet Validation",
            default_cors_preflight_options = cors_config,
            domain_name=apigateway.DomainNameOptions(
                domain_name="api."+domain_name,
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
            authorizer_name = "cognitoAuthorizer",
            identity_source = apigateway.IdentitySource.header('Authorization')
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

        route53.ARecord(
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
            parameter_name="/sscheck/lambda-api",
            string_value=api.root.url,
            tier=ssm.ParameterTier.STANDARD
        )

