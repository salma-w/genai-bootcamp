from aws_cdk import Duration, Fn, RemovalPolicy
from constructs import Construct
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_s3 as s3

class Backend(Construct):
    endpoint: str
    domain_name: str

    def __init__(self, scope: "Construct", id: str) -> None:
        super().__init__(scope, id)

        dynamodb_table = dynamodb.TableV2(self, 'CSBackendTable',
                                          partition_key=dynamodb.Attribute(name='PK', type=dynamodb.AttributeType.STRING),
                                          sort_key=dynamodb.Attribute(name='SK', type=dynamodb.AttributeType.STRING),
                                          removal_policy=RemovalPolicy.DESTROY,
                                        )
        state_bucket = s3.Bucket(self, 'StateBucket')

        fn = _lambda.DockerImageFunction(self, 'CSBackend',
                                            function_name='CSBackend',
                                            timeout=Duration.seconds(60),
                                            architecture=_lambda.Architecture.X86_64,
                                            code=_lambda.DockerImageCode.from_image_asset(
                                                directory='csbot/backend/src',
                                                file='Dockerfile'
                                            ),
                                            environment={
                                                 "MODEL_ID": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                                                 "AWS_LWA_INVOKE_MODE": "response_stream",
                                                 "STATE_BUCKET": state_bucket.bucket_name,
                                                 "DDB_TABLE": dynamodb_table.table_name,
                                            },
                                            memory_size=1024,
                                        )
        _ = state_bucket.grant_read_write(fn)
        _ = dynamodb_table.grant_read_write_data(fn)
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
        self.endpoint = fn_url.url
        self.domain_name = Fn.select(2, Fn.split('/', self.endpoint)) # Remove the protocol part from the URL
