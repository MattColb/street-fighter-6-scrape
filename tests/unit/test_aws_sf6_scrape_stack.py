import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_sf6_scrape.aws_sf6_scrape_stack import AwsSf6ScrapeStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_sf6_scrape/aws_sf6_scrape_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsSf6ScrapeStack(app, "aws-sf6-scrape")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
