The Lambda function we are working on has all of its code under
`csbot/backend/src/app`. It is written in Python 3.12.

When creating code, create classes, group logically into separate files
and use import statements to reference.
Use built-in type available with Python 3.9 and above where possible.

A DynamoDB table is available - the name of the table is in the
environment variable `DDB_TABLE`. The partition key is named `PK`
and the range key is named `SK`.

We are creating a backend for an airline customer service system.

# To do

- [x] Create a class for managing Trips, with each Trip a record stored in DynamoDB.
      Each Trip has a user provided name (eg "Nana's 80th").
      The PK should be the user's ID, which will be provided, prefixed with `U#`. The SK should be a
      UUID for the trip, prefxied with `T#`.
      Make sure that there is a way to save a new trip, and a way to update the trip name
- [x] Create a class for managing Flight records. Each flight corresponds to a flight the user has booked, and
      the records include:
      - A `from` airport (use 3 letter code)
      - A `to` airport (3 letter code)
      - The datetime in UTC when the flight leaves 
      - The datetime in UTC when the flight arrives,
      - A decimal value for the price paid
      - Ticket type - 'Basic Economy', or 'Economy fully refundable'.
      - Payment status - `paid`, `cancelled` or `refunded`.

      The `PK` should be the UUID for the trip including the `T#` prefix. The `SK` should be a UUID prefixed with `F#`.
- [x] Update the `Flight` class to enable the `PaymentStatus` to be updated
- [x] Add a method on the Trip class which retrieves the full trip details - the name of the trip and
      all flights associated with the trip. It should take the user ID as an argument
- [x] Add a `GET` API endpoint which allows a user to list all their trips. The `user_id` will be equal to the `session_id`.
- [x] Add a `POST` API endpoint which allows a user to rename their trip
- [x] When a new session is created via the `LoadHistory` method, add two dummy trips for the user:
      - Trip "Nana's 80th", with flights from Munich to Seoul one week in 2024, and a return flight the week after, economy class
      - Trip "Summer weekend", with flights from Munich to Nice on a Friday in two weeks time, and a return flight the Monday after.
- [x] Add `/api/trip/{trip_id}` which will return all flights for a given trip ID
