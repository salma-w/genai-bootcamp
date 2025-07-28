import aws_cdk as core
import aws_cdk.assertions as assertions

from 1_s3_vectors.1_s3_vectors_stack import 1S3VectorsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in 1_s3_vectors/1_s3_vectors_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = 1S3VectorsStack(app, "1-s3-vectors")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
