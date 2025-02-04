from aws_cdk import (
    Stack,
    aws_sqs as sqs,
    aws_lambda,
    Duration,
    aws_dynamodb,
    aws_lambda_event_sources,
    RemovalPolicy
)
from constructs import Construct
import subprocess

class AwsSf6ScrapeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #DynamoDB
        #Lambdas
        #SQS Queue?
        sf6_queue = sqs.Queue(
            self, "SF6_Queue",
            visibility_timeout=Duration.seconds(300),
        )

        subprocess.run(["pip", "install", "-r", "lambdas/requirements.txt", "-t", "lambdas"])

        main_handler = aws_lambda.Function(
            self, "Main_SF6_Handler",
            runtime= aws_lambda.Runtime.PYTHON_3_10,
            handler = "main_handler.handler",
            code = aws_lambda.Code.from_asset("lambdas"),
            environment = {
                "SQS_QUEUE_URL": sf6_queue.queue_url
            },
            timeout=Duration.seconds(60)
        )

        sf6_queue.grant_send_messages(main_handler)

        db = aws_dynamodb.Table(
            self, "SF6_DB",
            removal_policy = RemovalPolicy.DESTROY,
        )

        page_handling_lambda = aws_lambda.Function(
            self, "Page_SF6_Handler",
            runtime= aws_lambda.Runtime.PYTHON_3_10,
            handler = "page_handler.handler",
            code = aws_lambda.Code.from_asset("lambdas"),
            environment = {
                "DYNAMO_DB_TABLE_NAME":db.table_name 
            },
            timeout=Duration.seconds(60)
        )

        page_handling_lambda.add_event_source(aws_lambda_event_sources.SqsEventSource(sf6_queue))

        db.grant_read_write_data(page_handling_lambda)