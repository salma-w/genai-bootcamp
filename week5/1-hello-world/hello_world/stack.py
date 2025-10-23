import aws_cdk as cdk
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as _lambda

class HelloWorld(cdk.Stack):
    def __init__(self, scope: cdk.App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        fn = _lambda.DockerImageFunction(self, 'HelloWorld',
                                            function_name='HelloWorld',
                                            timeout=cdk.Duration.seconds(60),
                                            code=_lambda.DockerImageCode.from_image_asset(
                                                directory='hello_world/src',
                                                file='Dockerfile'
                                            ),
                                            architecture=_lambda.Architecture.X86_64,
                                            environment={
                                                 "MODEL_ID": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
                                                 "AWS_LWA_INVOKE_MODE": "response_stream",
                                            },
                                        )
        # Add Bedrock permissions to the Lambda function
        fn.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:InvokeModel"
                ],
                resources=["*"]
            )
        )
        fn_url = fn.add_function_url(
                    auth_type=_lambda.FunctionUrlAuthType.NONE,
                    invoke_mode=_lambda.InvokeMode.RESPONSE_STREAM,
                    cors=_lambda.FunctionUrlCorsOptions(
                        allowed_methods=[_lambda.HttpMethod.ALL],
                        allowed_origins=['*'],
                    ),
                 )

        _ = cdk.CfnOutput(
            self, 
            'HelloWorldEndpoint',
            value=fn_url.url,
            description='Hello World endpoint URL'
        )
