from aws_cdk import Duration, RemovalPolicy
from constructs import Construct
import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_deployment as s3deploy

class Frontend(Construct):
    domain_name: str

    def __init__(self, scope: Construct, id: str, backend_endpoint: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        frontend_bucket = s3.Bucket(self, 'FrontendBucket')

        s3_origin = origins.S3BucketOrigin.with_origin_access_control(frontend_bucket,
                                                                       origin_access_levels=[cloudfront.AccessLevel.READ, cloudfront.AccessLevel.LIST],
                                                                      )
        origin_request_policy = cloudfront.OriginRequestPolicy(self, "OriginRequestPolicy",
                                                               cookie_behavior=cloudfront.OriginRequestCookieBehavior.all(),
                                                               )
        backend_origin = origins.HttpOrigin(
            domain_name=backend_endpoint,
            read_timeout=Duration.seconds(60),
            keepalive_timeout=Duration.seconds(60),
            connection_timeout=Duration.seconds(10),
        )
        
        distribution = cloudfront.Distribution(self, 'Distribution',
                                                            default_root_object='index.html',
                                                            default_behavior=cloudfront.BehaviorOptions(origin=s3_origin),
                                                            additional_behaviors={
                                                                '/api/*': cloudfront.BehaviorOptions(
                                                                    origin=backend_origin,
                                                                    origin_request_policy=origin_request_policy,
                                                                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                                                                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED
                                                                )
                                                            }
                                              )
        
        _ = s3deploy.BucketDeployment(self, 'DeployFrontend',
                                      sources=[s3deploy.Source.asset('./twin/frontend/src')],
                                      destination_bucket=frontend_bucket,
                                      distribution=distribution,
                                      distribution_paths=['/*'],
                                     )
        
        self.domain_name = distribution.distribution_domain_name
