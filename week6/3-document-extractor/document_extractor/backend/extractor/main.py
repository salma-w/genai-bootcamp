import json
import boto3
import os
from strands import Agent
import uuid

model_id = os.environ.get("MODEL_ID", "")
s3_client = boto3.client('s3')

agent = Agent(model=model_id, callback_handler=None)


def extract_bank_statement_data(document: bytes) -> dict:
    """
    Extracts structured data from a bank statement document.
    """
    extractor_prompt = """
        Please extract the following information from this bank statement and return it as a JSON object:
        - BankName
        - AccountNumber
        - OpeningBalance
        - ClosingBalance
        - StartDate
        - EndDate
    """

    response = agent([
        {"text": extractor_prompt},
        {
            "document": {
                "format": "pdf",
                "name": f"bank_statement-{uuid.uuid4()}",
                "source": {
                    "bytes": document,
                },
            },
        },
    ])

    try:
        output = str(response)
        # Handle cases where the model returns JSON in a code block
        if "```json" in output:
            output = output.split("```json")[1].split("```")[0]
        
        return json.loads(output)
    except (json.JSONDecodeError, IndexError):
        print(f"Could not parse JSON from response: {output}")
        return {}


def handler(event, context):
    """
    Lambda handler for document extraction.
    """
    print("Extracting document data...")
    print(f"Event: {json.dumps(event)}")
    
    bucket = event['bucket']
    key = event['key']
    
    # Get the object from S3
    response = s3_client.get_object(Bucket=bucket, Key=key)
    
    # Read the binary content
    file_content = response['Body'].read()

    extracted_data = extract_bank_statement_data(file_content)

    is_valid = bool(extracted_data)

    return {
        'bucket': bucket,
        'key': key,
        'valid': is_valid,
        'extracted_data': extracted_data,
        'retry_count': event.get('retry_count', 0) + 1
    }
