import aws_cdk as cdk
from twin.backend.infra import Backend
from twin.frontend.infra import Frontend

class Twin(cdk.Stack):
    def __init__(self, scope: cdk.App, id: str,
                 kb_arn: str, # Bedrock Knowledge Base ARN
                 kb_id: str,  # Bedrock Knowledge Base ID
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        backend = Backend(self, 'Backend',
                          kb_arn=kb_arn,
                          kb_id=kb_id
                         )
        frontend = Frontend(self, 'Frontend', backend_endpoint=backend.domain_name)

        _ = cdk.CfnOutput(
            self, 
            'FrontendURL',
            value=f"https://{frontend.domain_name}",
            description='Frontend UI URL'
        )
