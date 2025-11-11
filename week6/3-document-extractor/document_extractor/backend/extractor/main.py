from datetime import date
import json
import boto3
import os
from strands import Agent
import uuid
from pydantic import BaseModel, Field


# 1) Define the Pydantic model
class BankInfo(BaseModel):
    """Model that contains information about a Person"""
    bankname: str = Field(description="Name of the bank")
    accountnumber: str = Field(description="Account number")
    openingbalance: float = Field(description="Opening balance")
    closingbalance: str = Field(description="Closing balance")
    startdate: date = Field(description="Start date")
    enddate: str = Field(description="End date")
 
# 2) Pass the model to the agent


model_id = os.environ.get("MODEL_ID", "global.anthropic.claude-sonnet-4-5-20250929-v1:0")
s3_client = boto3.client('s3')

agent = Agent(model=model_id, callback_handler=None, structured_output_model=BankInfo)


def extract_bank_statement_data(document: bytes) -> dict:
    """
    Extracts structured data from a bank statement document.

    Args:
        document (bytes): Raw bytes of the uploaded bank statement PDF or image.
        BankInfo (BaseModel): 
            Structured model representing the extracted information.
            Includes:
                - bankname (str): Name of the bank.
                - accountnumber (str): Account number on the statement.
                - openingbalance (float): Balance at the start of the period.
                - closingbalance (str): Balance at the end of the period.
                - startdate (date): Starting date of the statement period.
                - enddate (str): Ending date of the statement period.

    Returns:
        dict: Parsed fields matching the BankInfo schema.

    """

    response = agent([
        {"text": "You extract structured fields from bank statements. "
                 "Return ONLY a JSON object matching the BankInfo schema."},
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
