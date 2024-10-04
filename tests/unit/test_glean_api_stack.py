import aws_cdk as core
import aws_cdk.assertions as assertions

from src.glean_api_stack import GleanApiStack

# example tests. To run these tests, uncomment this file along with the example
# resource in glean/glean_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = GleanApiStack(app, "glean")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
