import aws_cdk as cdk

from csbot.backend.infra import Backend
from csbot.frontend.infra import Frontend

class CSBot(cdk.Stack):
    def __init__(self, scope: cdk.App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        backend = Backend(self, 'Backend')
        frontend = Frontend(self, 'Frontend', backend_endpoint=backend.domain_name)

        _ = cdk.CfnOutput(
            self, 
            'FrontendURL',
            value=f"https://{frontend.domain_name}",
            description='Frontend UI URL'
        )
