from typing import Text
from aws_cdk import (
    core as cdk,   
    aws_ssm as ssm,
    aws_route53 as route53,
    aws_certificatemanager as acm
)

class PredeploymentStack(cdk.Stack):
    """The stack is meant to deploy manually once before any other stack"""

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Defining app constants
        app_stage = self.node.try_get_context("app_stage")
        props = self.node.try_get_context("props")

        # --- Query deployment env specific config from SSM Parameter Store
        # Query existing UMCCR domain

        umccr_domain = ssm.StringParameter.from_string_parameter_name(
            self,
            "DomainName",
            string_parameter_name="umccr_domain",
        ).string_value

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

        # Fetch existing hosted_zone
        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            "HostedZone",
            hosted_zone_id=hosted_zone_id,
            zone_name=hosted_zone_name,
        )

        cert_use1 = acm.DnsValidatedCertificate(
            self,
            "SSLCertificateUSE1StatusPage",
            subject_alternative_names=props["alias_domain_name"][app_stage],
            hosted_zone=hosted_zone,
            region="us-east-1",
            domain_name= "api.sscheck." + umccr_domain,
            validation=acm.CertificateValidation.from_dns(
                hosted_zone=hosted_zone
            )
        )

        # Create ARN for cert_use1 created above
        ssm.StringParameter(
            self,
            "StatusPageSSLCertificateARN",
            string_value=cert_use1.certificate_arn,
            tier=ssm.ParameterTier.STANDARD,
            description="SSL Certificate ARN for sscheck-frontend stack",
            parameter_name="/sscheck/api/ssl_certificate_arn",
        )
