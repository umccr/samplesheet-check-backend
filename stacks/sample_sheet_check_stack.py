from aws_cdk import (core as cdk,
                     aws_apigateway as apigateway,
                     aws_lambda as lambda_,
                     aws_cognito as cognito,
                     aws_ssm as ssm
                     )

class SampleSheetCheckStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a Lambda Layer
        sample_check_layer = lambda_.LayerVersion(
            self,
            "SamplecheckLambdaLayer",
            code=lambda_.Code.from_asset("lambdas/layers/umccr_utils/python38-umccr_utils.zip"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
            description="A samplecheck library layer for python 3.8"
        )

        # Load SSM parameter
        data_portal_metadata_api = ssm.StringParameter.from_string_parameter_attributes(self, "urlValue",
            parameter_name="/samplesheet-check/be/data-porta-metadata-api"
        ).string_value

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
            deploy_options={
                "logging_level": apigateway.MethodLoggingLevel.INFO,
                "data_trace_enabled": True
            }
        )

        # Integrate the apigateway with the lambda function
        sampleSheetValidationIntegration = apigateway.LambdaIntegration(sample_sheet_check_lambda)
        
        # Load SSM parameter
        arn_cognito_pool = ssm.StringParameter.from_string_parameter_attributes(self, "bucketValue",
            parameter_name="/samplesheet-check/be/arn-cognito-pool"
        ).string_value
        
        # Pool Config
        user_pool = cognito.UserPool.from_user_pool_arn(self, "existingUserPool",
            user_pool_arn = arn_cognito_pool
        )

        # Authorizer config
        auth_config = apigateway.CognitoUserPoolsAuthorizer(self, "cognitoAuthorizer",
            cognito_user_pools=[user_pool],
            authorizer_name = "cognitoAuthorizer",
            identity_source = apigateway.IdentitySource.header('Authorization')
        )

        # add method of the function for the api gateway
        api.root.add_method("POST", sampleSheetValidationIntegration,
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=auth_config
        )

        # Create SSM parameter for REST api URL
        ssm.StringParameter(self, "samplesheetCheckLambdaApi",
            allowed_pattern=".*",
            description="The Lambda Rest-api Samplesheet Check",
            parameter_name="/samplesheet-check/be/rest-api",
            string_value=api.root.url,
            tier=ssm.ParameterTier.STANDARD
        )
