from aws_cdk import (
    Stack,
    aws_s3 as s3,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class GleanApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        glean_bucket = s3.Bucket(self, "Bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.RETAIN
        )

        CfnOutput(self, "GleanBucketName", value=glean_bucket.bucket_name)
