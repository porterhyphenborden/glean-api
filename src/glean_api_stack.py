from aws_cdk import (
    Stack,
    aws_s3 as s3,
    RemovalPolicy,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_lambda_python_alpha as _plambda,
    aws_cognito as cognito,
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

        """ Lambdas """

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

        get_events_lambda = _plambda.PythonFunction(
            self,
            "GetEventsLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            entry="src",
            index="endpoints/get_events.py",
            handler="handler",
            environment={
                "GLEAN_TABLE_NAME": glean_table.table_name,
            }
        )

        """ Cognito resources """

        user_pool = cognito.UserPool(
            self,
            "GleanApiUserPool",
            user_pool_name="glean_api_user_pool",
            self_sign_up_enabled=True,
            auto_verify={"email": True},
            sign_in_aliases=cognito.SignInAliases(email=True),
        )

        cognito_domain = user_pool.add_domain(
            "GleanCognitoDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="glean-api",
            )
        )

        user_pool_client = user_pool.add_client(
            "GleanApiUserPoolClient",
            generate_secret=False,
            auth_flows={
                "user_password": True,
                "user_srp": True,
                "admin_user_password": True,
            },
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True
                ),
                callback_urls=["https://example.com/callback"],
            )
        )

        """ Api resources """

        api = apigateway.RestApi(
            self,
            "GleanApi",
            rest_api_name="glean",
        )

        authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self,
            "CognitoAuthorizer",
            cognito_user_pools=[user_pool]
        )

        users = api.root.add_resource("users")
        user_by_id = users.add_resource("{user_id}")
        events = user_by_id.add_resource("events")
        events.add_method(
            "POST",
            integration=apigateway.LambdaIntegration(create_event_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )
        seasons = events.add_resource("seasons")
        season = seasons.add_resource("{season}")
        season.add_method(
            "GET",
            integration=apigateway.LambdaIntegration(get_events_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )
        crops = season.add_resource("crops")
        crop = crops.add_resource("{crop}")
        crop.add_method(
            "GET",
            integration=apigateway.LambdaIntegration(get_events_lambda),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        ### Permissions ###
        glean_table.grant_read_write_data(create_event_lambda)
        glean_table.grant_read_data(get_events_lambda)

        CfnOutput(self, "GleanBucketName", value=glean_bucket.bucket_name)
        CfnOutput(self, "GleanTableName", value=glean_table.table_name)
        CfnOutput(self, "GleanApiUrl", value=api.url)
        CfnOutput(self, "CognitoDomainUrl", value=cognito_domain.domain_name)
