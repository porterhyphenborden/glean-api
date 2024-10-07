from aws_cdk import (
    Stack,
    aws_s3 as s3,
    RemovalPolicy,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_lambda_python_alpha as _plambda,
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

        glean_table = dynamodb.Table(
            self,
            "GleanTable",
            partition_key=dynamodb.Attribute(
                name="pk",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="sk",
                type=dynamodb.AttributeType.STRING,
            )
        )

        create_event_lambda = _plambda.PythonFunction(
            self,
            "CreateEventLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            entry="src",
            index="endpoints/create_event.py",
            handler="handler",
            environment={
                "GLEAN_TABLE_NAME": glean_table.table_name,
            }
        )

        api = apigateway.RestApi(
            self,
            "GleanApi",
            rest_api_name="glean",
        )

        users = api.root.add_resource("users")
        user_by_id = users.add_resource("{user_id}")
        events = user_by_id.add_resource("events")
        events.add_method("POST", integration=apigateway.LambdaIntegration(create_event_lambda))

        ### Permissions ###
        glean_table.grant_read_write_data(create_event_lambda)

        CfnOutput(self, "GleanBucketName", value=glean_bucket.bucket_name)
        CfnOutput(self, "GleanTableName", value=glean_table.table_name)
        CfnOutput(self, "GleanApiUrl", value=api.url)
