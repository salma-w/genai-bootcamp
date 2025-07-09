<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import type { FullTrip } from '$lib/types';
	import { loadTripDetails, renameTrip } from '$lib/api';
	import { Edit, Save, XCircle } from 'lucide-svelte';

	let trip: FullTrip | null = null;
	let isLoading = true;
	let error: string | null = null;
	let isRenaming = false;
	let newName = '';
	let tripId: string | null = null;

	async function loadData() {
		if (!tripId) {
			error = 'Trip ID not found.';
			isLoading = false;
			return;
		}
		isLoading = true;
		error = null;
		try {
			trip = await loadTripDetails(tripId);
			if (trip) {
				newName = trip.name;
			}
		} catch (e: any) {
			error = e.message;
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		tripId = $page.url.searchParams.get('tripId');
		loadData();
	});

	async function handleRename() {
		if (!trip || !tripId || newName.trim() === '' || newName === trip.name) {
			isRenaming = false;
			return;
		}
		try {
			await renameTrip(tripId, newName.trim());
			isRenaming = false;
			await loadData(); // Refresh data
		} catch (e: any) {
			error = e.message;
		}
	}

	function formatDateTime(dateTimeString: string) {
		const options: Intl.DateTimeFormatOptions = {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
			timeZoneName: 'short'
		};
		return new Date(dateTimeString).toLocaleString(undefined, options);
	}
</script>

<div class="trip-details-container">
	{#if isLoading}
		<p>Loading trip details...</p>
	{:else if error}
		<p class="error">Error: {error}</p>
	{:else if trip}
		<div class="header">
			{#if isRenaming}
				<form on:submit|preventDefault={handleRename} class="rename-form">
					<input type="text" bind:value={newName} class="rename-input" />
					<button type="submit" class="icon-button"><Save size={20} /></button>
					<button type="button" on:click={() => (isRenaming = false)} class="icon-button cancel"
						><XCircle size={20} /></button
					>
				</form>
			{:else}
				<h1>{trip.name}</h1>
				<button on:click={() => (isRenaming = true)} class="icon-button" title="Rename trip"
					><Edit size={20} /></button
				>
			{/if}
		</div>

		<h2>Flights</h2>
		<div class="flights-grid">
			{#each trip.flights as flight (flight.flight_id)}
				<div class="flight-card">
					<div class="flight-path">
						<span class="airport">{flight.from_airport}</span>
						<span>&rarr;</span>
						<span class="airport">{flight.to_airport}</span>
					</div>
					<p><strong>Departure:</strong> {formatDateTime(flight.departure_time)}</p>
					<p><strong>Arrival:</strong> {formatDateTime(flight.arrival_time)}</p>
					<p><strong>Price:</strong> ${flight.price}</p>
					<p><strong>Ticket:</strong> {flight.ticket_type}</p>
					<p>
						<strong>Payment:</strong>
						<span class="status {flight.payment_status}">{flight.payment_status}</span>
					</p>
				</div>
			{/each}
		</div>
	{:else}
		<p>Trip not found.</p>
	{/if}
</div>

<style>
	.trip-details-container {
		padding: 20px;
		max-width: 900px;
		margin: auto;
	}

	.header {
		display: flex;
		align-items: center;
		margin-bottom: 2rem;
		gap: 10px;
	}

	h1 {
		font-size: 2.5rem;
		font-weight: 600;
		color: #2d3748;
		margin: 0;
		flex-grow: 1;
	}

	.rename-form {
		display: flex;
		flex-grow: 1;
		gap: 10px;
	}

	.rename-input {
		font-size: 2.2rem;
		padding: 5px 10px;
		border: 1px solid #ccc;
		border-radius: 5px;
		flex-grow: 1;
		font-family: inherit;
		font-weight: 600;
		color: #2d3748;
	}

	.icon-button {
		background: none;
		border: none;
		cursor: pointer;
		padding: 5px;
		color: #4a5568;
		display: inline-flex;
		align-items: center;
	}
	.icon-button:hover {
		color: #2d3748;
	}
	.icon-button.cancel:hover {
		color: #e53e3e;
	}

	h2 {
		font-size: 1.8rem;
		border-bottom: 2px solid #eee;
		padding-bottom: 0.5rem;
		margin-bottom: 1.5rem;
		color: #333;
	}

	.flights-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 20px;
	}

	.flight-card {
		border: 1px solid #ddd;
		border-radius: 8px;
		padding: 20px;
		background-color: #fff;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
		transition: box-shadow 0.2s;
	}
	.flight-card:hover {
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}

	.flight-path {
		font-size: 1.2rem;
		font-weight: 500;
		margin-bottom: 15px;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.airport {
		font-weight: bold;
	}

	.flight-card p {
		margin: 8px 0;
		color: #4a5568;
		display: flex;
		justify-content: space-between;
	}

	.status {
		padding: 3px 8px;
		border-radius: 12px;
		font-size: 0.8rem;
		font-weight: 500;
		text-transform: capitalize;
	}

	.status.paid {
		background-color: #c6f6d5;
		color: #2f855a;
	}

	.status.unpaid {
		background-color: #fed7d7;
		color: #c53030;
	}

	.error {
		color: #e53e3e;
		background-color: #fed7d7;
		padding: 1rem;
		border-radius: 5px;
	}
</style>
