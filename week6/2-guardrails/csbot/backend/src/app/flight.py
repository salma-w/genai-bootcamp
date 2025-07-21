import logging
import os
import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field, constr

logger = logging.getLogger(__name__)

DDB_TABLE = os.environ.get("DDB_TABLE")
if not DDB_TABLE:
    logger.error("DDB_TABLE environment variable not set.")
    raise ValueError("DDB_TABLE environment variable not set.")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DDB_TABLE)


class TicketType(str, Enum):
    BASIC_ECONOMY = "Basic Economy"
    ECONOMY_FULLY_REFUNDABLE = "Economy fully refundable"


class PaymentStatus(str, Enum):
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Flight(BaseModel):
    trip_id: str
    from_airport: constr(min_length=3, max_length=3)
    to_airport: constr(min_length=3, max_length=3)
    departure_time: datetime
    arrival_time: datetime
    price: Decimal
    ticket_type: TicketType
    payment_status: PaymentStatus = PaymentStatus.PAID
    flight_id: str = Field(default_factory=lambda: f"F#{uuid.uuid4()}")

    def save(self) -> str:
        """Saves a new flight to DynamoDB."""
        if not self.trip_id.startswith("T#"):
            msg = f"trip_id '{self.trip_id}' must be prefixed with 'T#'"
            logger.error(msg)
            raise ValueError(msg)

        logger.info(f"Saving flight {self.flight_id} for trip {self.trip_id}")
        try:
            table.put_item(
                Item={
                    "PK": self.trip_id,
                    "SK": self.flight_id,
                    "Type": "Flight",
                    "FromAirport": self.from_airport,
                    "ToAirport": self.to_airport,
                    "DepartureTime": self.departure_time.isoformat(),
                    "ArrivalTime": self.arrival_time.isoformat(),
                    "Price": self.price,
                    "TicketType": self.ticket_type.value,
                    "PaymentStatus": self.payment_status.value,
                },
                ConditionExpression="attribute_not_exists(SK)",
            )
            logger.info(f"Successfully saved flight {self.flight_id}")
            return self.flight_id
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                msg = (
                    f"Flight {self.flight_id} already exists for trip {self.trip_id}."
                )
                logger.warning(msg)
                raise ValueError(msg) from e
            else:
                logger.error(f"Error saving flight {self.flight_id}: {e}")
                raise

    @staticmethod
    def update_payment_status(trip_id: str, flight_id: str, payment_status: PaymentStatus):
        """Updates the payment status of a flight."""
        logger.info(f"Updating payment status for flight {flight_id} in trip {trip_id} to {payment_status.value}")
        try:
            table.update_item(
                Key={"PK": trip_id, "SK": flight_id},
                UpdateExpression="SET PaymentStatus = :s",
                ExpressionAttributeValues={":s": payment_status.value},
                ConditionExpression="attribute_exists(PK) and attribute_exists(SK)",
            )
            logger.info(f"Successfully updated payment status for flight {flight_id}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                msg = f"Flight {flight_id} not found for trip {trip_id}."
                logger.warning(msg)
                raise ValueError(msg) from e
            else:
                logger.error(f"Error updating payment status for flight {flight_id}: {e}")
                raise
