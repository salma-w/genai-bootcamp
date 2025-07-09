import type { ChatHistory, Message, Trip, FullTrip } from './types';

export async function loadChatHistory(): Promise<Message[]> {
	const response = await fetch('/api/chat');
	if (!response.ok) {
		throw new Error('Failed to fetch chat history');
	}
	const data: ChatHistory = await response.json();
	return data.messages;
}

export async function loadTrips(): Promise<Trip[]> {
	const response = await fetch('/api/trips');
	if (!response.ok) {
		throw new Error('Failed to fetch trips');
	}
	const data: Trip[] = await response.json();
	return data;
}

export async function loadTripDetails(tripId: string): Promise<FullTrip> {
	const response = await fetch(`/api/trip/${encodeURIComponent(tripId)}`);
	if (!response.ok) {
		throw new Error('Failed to fetch trip details');
	}
	const data: FullTrip = await response.json();
	return data;
}

export async function renameTrip(tripId: string, newName: string): Promise<void> {
	const response = await fetch(`/api/trips/${encodeURIComponent(tripId)}/rename`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ name: newName })
	});
	if (!response.ok) {
		throw new Error('Failed to rename trip');
	}
}
