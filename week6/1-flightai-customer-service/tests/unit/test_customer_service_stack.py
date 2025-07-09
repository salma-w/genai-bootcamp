import aws_cdk as core
import aws_cdk.assertions as assertions

from customer_service.customer_service_stack import CustomerServiceStack

# example tests. To run these tests, uncomment this file along with the example
# resource in customer_service/customer_service_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CustomerServiceStack(app, "customer-service")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
