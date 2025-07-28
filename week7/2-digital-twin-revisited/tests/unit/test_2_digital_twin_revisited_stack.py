import aws_cdk as core
import aws_cdk.assertions as assertions

from 2_digital_twin_revisited.2_digital_twin_revisited_stack import 2DigitalTwinRevisitedStack

# example tests. To run these tests, uncomment this file along with the example
# resource in 2_digital_twin_revisited/2_digital_twin_revisited_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = 2DigitalTwinRevisitedStack(app, "2-digital-twin-revisited")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
