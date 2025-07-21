import aws_cdk as core
import aws_cdk.assertions as assertions

from 2_document_extractor.2_document_extractor_stack import 2DocumentExtractorStack

# example tests. To run these tests, uncomment this file along with the example
# resource in 2_document_extractor/2_document_extractor_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = 2DocumentExtractorStack(app, "2-document-extractor")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
