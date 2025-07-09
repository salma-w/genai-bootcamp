export interface MessageContent {
	text: string;
}

export interface Message {
	role: 'user' | 'assistant';
	content: MessageContent[];
}

export interface ChatHistory {
	messages: Message[];
}

export interface Trip {
	trip_id: string;
	name: string;
}

export interface Flight {
	trip_id: string;
	from_airport: string;
	to_airport: string;
	departure_time: string;
	arrival_time: string;
	price: string;
	ticket_type: string;
	payment_status: string;
	flight_id: string;
}

export interface FullTrip {
	name: string;
	flights: Flight[];
}
