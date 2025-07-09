We are working on a SvelteKit 5 SPA written in TypeScript.
All files should be under `week5/3-flightai-customer-service/csbot/frontend/customer-service`.

When creating code, create separate libraries and group logically into
files.

All API endpoints should be referenced unqualified as it runs on the same host.
When sending a `tripId` in a URL make sure you urlencode.

When building the UI, spend the time to make it look clean, crisp and professional.
The lucide-svelte icon toolkit is available and should be used.

# TODO

- [x] Add function to load chat history on page load
      
Chat history should be loaded from `/api/chat`. It will be provided in JSON format as follows:

```json
{"messages": [{"role": "user", "content": [{"text": "Who are you?"}]}, {"role": "assistant", "content": [{"text": "I'm Claude, an AI assistant created by Anthropic. I'm here to help you with various tasks, answer questions, and have conversations. I can assist with things like writing, analysis, math, coding, creative tasks, and more. \n\nI notice I also have access to a weather function that can provide current weather information for locations if you need that. Is there anything specific I can help you with today?"}]}]}
```
Create a function that can be used on a page later

- [x] Add a function to load trips

Load trips from `/api/trips`. Here is a sample result:

```json
[{"trip_id": "T#6f5b75f9-a1b8-404a-8ff3-2f194f0ddefa", "name": "Summer weekend"}, {"trip_id": "T#72cfa3b4-a76c-4175-9aa5-7625412bfbd9", "name": "Nana's 80th"}]
```

- [x] Add a function to show trip details

Take the trip ID as an argument and load the flights for a trip with a `GET` request to `/api/trips/${tripId}`.
The trip will be returned as JSON like this:

```json
{"name":"Summer weekend","flights":[{"trip_id":"T#6f5b75f9-a1b8-404a-8ff3-2f194f0ddefa","from_airport":"NCE","to_airport":"MUC","departure_time":"2025-07-28T20:00:00Z","arrival_time":"2025-07-28T21:30:00Z","price":"275","ticket_type":"Basic Economy","payment_status":"paid","flight_id":"F#c233ab43-f7b5-4309-a957-5754c906ecb6"},{"trip_id":"T#6f5b75f9-a1b8-404a-8ff3-2f194f0ddefa","from_airport":"MUC","to_airport":"NCE","departure_time":"2025-07-25T18:00:00Z","arrival_time":"2025-07-25T19:30:00Z","price":"250","ticket_type":"Basic Economy","payment_status":"paid","flight_id":"F#fe2a6022-e518-4d9b-9e44-d07655ab5b25"}]}
```

- [x] Add a function to rename trips

A trip can be renamed with a `POST` to `/api/trips/${tripId}/rename`. Send a JSON object with a key `name` and the new trip name as the value.

- [x] Create a sidebar to be shown on all pages

Add a sidebar shown on the left of the page. It should have two entries, 'Trips' and 'Support Chat'
This sidebar should be shown on all pages.

- [x] Create the front page

On page load, load the chat history.
Show the header 'Welcome to FlightAI'.
Manage your trips and get help here.
Ensure the sidebar is shown.

- [x] Create a trip details page

The page should show the details for a given `tripId`: the trip name and the flights associated with the trip.
It should have the option to rename the trip. After the trip has been renamed the trip details should be
re-fetched and the page updated.

- [x] Create the trips page

The trips page should show a list of trip names, each of which should be a link to the trip details page
for that trip

- [x] Create the Support Chat page

The Support Chat page should show the conversation between the user and an assistant. On page load the chat history
should be loaded and displayed.
The user should be able to enter a message to the assistant. This message should be a `POST` message to `/api/chat`, with
a JSON object with the key `prompt` and the value the text entered by the user. The response will be provided as a
`text/event-stream`.

- [x] Format markdown on the support chat page

The assistant may return markdown. This should be processed and formatted nightly. If you need an additional package
from npm for this, please ask the user to install it rather than trying to do it yourself.
