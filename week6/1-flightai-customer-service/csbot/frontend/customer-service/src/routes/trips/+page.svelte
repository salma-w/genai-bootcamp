<script lang="ts">
	import { onMount } from 'svelte';
	import type { Trip } from '$lib/types';
	import { loadTrips } from '$lib/api';

	let trips: Trip[] = [];
	let isLoading = true;
	let error: string | null = null;

	onMount(async () => {
		try {
			trips = await loadTrips();
		} catch (e: any) {
			error = e.message;
		} finally {
			isLoading = false;
		}
	});
</script>

<div class="trips-container">
	<h1>Your Trips</h1>
	{#if isLoading}
		<p>Loading trips...</p>
	{:else if error}
		<p class="error">Error: {error}</p>
	{:else if trips.length > 0}
		<ul class="trips-list">
			{#each trips as trip (trip.trip_id)}
				<li>
					<a href="/trips/details?tripId={encodeURIComponent(trip.trip_id)}">{trip.name}</a>
				</li>
			{/each}
		</ul>
	{:else}
		<p>You have no trips planned.</p>
	{/if}
</div>

<style>
	.trips-container {
		padding: 20px;
		max-width: 800px;
		margin: auto;
	}

	h1 {
		font-size: 2.5rem;
		font-weight: 600;
		color: #2d3748;
		margin-bottom: 2rem;
	}

	.trips-list {
		list-style: none;
		padding: 0;
	}

	.trips-list li a {
		display: block;
		padding: 15px 20px;
		background-color: #fff;
		border: 1px solid #ddd;
		border-radius: 8px;
		margin-bottom: 10px;
		text-decoration: none;
		font-size: 1.1rem;
		color: #2d3748;
		transition:
			transform 0.2s,
			box-shadow 0.2s;
	}

	.trips-list li a:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}

	.error {
		color: #e53e3e;
		background-color: #fed7d7;
		padding: 1rem;
		border-radius: 5px;
	}
</style>
