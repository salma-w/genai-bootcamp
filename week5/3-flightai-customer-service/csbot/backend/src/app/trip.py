import logging
import os
import uuid

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

from flight import Flight

logger = logging.getLogger(__name__)

DDB_TABLE = os.environ.get("DDB_TABLE")
if not DDB_TABLE:
    logger.error("DDB_TABLE environment variable not set.")
    raise ValueError("DDB_TABLE environment variable not set.")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DDB_TABLE)


class FullTrip(BaseModel):
    name: str
    flights: list[Flight]


class Trip(BaseModel):
    user_id: str
    name: str
    trip_id: str = Field(default_factory=lambda: f"T#{uuid.uuid4()}")

    def save(self) -> str:
        """Saves a new trip to DynamoDB."""
        logger.info(f"Saving trip {self.trip_id} for user {self.user_id}")
        try:
            table.put_item(
                Item={
                    "PK": f"U#{self.user_id}",
                    "SK": self.trip_id,
                    "Name": self.name,
                    "Type": "Trip",
                },
                ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
            )
            logger.info(f"Successfully saved trip {self.trip_id}")
            return self.trip_id
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                msg = f"Trip {self.trip_id} for user {self.user_id} already exists."
                logger.warning(msg)
                raise ValueError(msg) from e
            else:
                logger.error(f"Error saving trip {self.trip_id}: {e}")
                raise

    @staticmethod
    def update_name(user_id: str, trip_id: str, new_name: str):
        """Updates the name of an existing trip."""
        logger.info(
            f"Updating trip {trip_id} for user {user_id} with new name '{new_name}'"
        )
        if not trip_id.startswith("T#"):
            msg = "trip_id must be prefixed with 'T#'"
            logger.error(msg)
            raise ValueError(msg)

        try:
            table.update_item(
                Key={"PK": f"U#{user_id}", "SK": trip_id},
                UpdateExpression="set #nm = :n",
                ExpressionAttributeNames={"#nm": "Name"},
                ExpressionAttributeValues={":n": new_name},
                ConditionExpression="attribute_exists(PK) AND attribute_exists(SK)",
            )
            logger.info(f"Successfully updated trip {trip_id}")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                msg = f"Trip {trip_id} for user {user_id} not found."
                logger.warning(msg)
                raise ValueError(msg) from e
            logger.error(f"Error updating trip {trip_id}: {e}")
            raise

    @staticmethod
    def list_for_user(user_id: str) -> list[dict]:
        """Lists all trips for a given user."""
        logger.info(f"Listing trips for user {user_id}")
        try:
            response = table.query(
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
                ExpressionAttributeValues={
                    ":pk": f"U#{user_id}",
                    ":sk_prefix": "T#",
                },
            )
            trips = []
            for item in response.get("Items", []):
                if item.get("Type") == "Trip":
                    trips.append({"trip_id": item["SK"], "name": item["Name"]})
            logger.info(f"Found {len(trips)} trips for user {user_id}")
            return trips
        except ClientError as e:
            logger.error(f"Error listing trips for user {user_id}: {e}")
            raise

    @staticmethod
    def get_full_trip(user_id: str, trip_id: str) -> FullTrip:
        """
        Retrieves the full trip details including the trip name and all associated flights.
        """
        if not trip_id.startswith("T#"):
            msg = "trip_id must be prefixed with 'T#'"
            logger.error(msg)
            raise ValueError(msg)

        logger.info(
            f"Retrieving full trip details for trip {trip_id} for user {user_id}"
        )
        try:
            # Get trip name
            trip_response = table.get_item(Key={"PK": f"U#{user_id}", "SK": trip_id})
            trip_item = trip_response.get("Item")
            if not trip_item:
                msg = f"Trip {trip_id} for user {user_id} not found."
                logger.warning(msg)
                raise ValueError(msg)

            trip_name = trip_item.get("Name")

            # Get flights
            flights_response = table.query(
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
                ExpressionAttributeValues={":pk": trip_id, ":sk_prefix": "F#"},
            )

            flights = []
            for item in flights_response.get("Items", []):
                flight_data = {
                    "trip_id": item["PK"],
                    "flight_id": item["SK"],
                    "from_airport": item["FromAirport"],
                    "to_airport": item["ToAirport"],
                    "departure_time": item["DepartureTime"],
                    "arrival_time": item["ArrivalTime"],
                    "price": item["Price"],
                    "ticket_type": item["TicketType"],
                    "payment_status": item["PaymentStatus"],
                }
                flights.append(Flight(**flight_data))

            return FullTrip(name=trip_name, flights=flights)
        except ClientError as e:
            logger.error(f"Error retrieving full trip details for trip {trip_id}: {e}")
            raise
