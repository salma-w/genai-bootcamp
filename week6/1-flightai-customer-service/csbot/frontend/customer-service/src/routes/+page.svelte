<script lang="ts">
	import { onMount } from 'svelte';
	import { loadChatHistory } from '$lib/api';

	onMount(async () => {
		try {
			await loadChatHistory();
		} catch (e) {
			console.error('Failed to load chat history:', e);
		}
	});
</script>

<div class="welcome-container">
	<h1>Welcome to FlightAI</h1>
	<p>Manage your trips and get help here.</p>
</div>

<style>
	.welcome-container {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		height: 100%;
		text-align: center;
	}

	h1 {
		font-size: 3rem;
		font-weight: 600;
		color: #2d3748;
		margin-bottom: 1rem;
	}

	p {
		font-size: 1.25rem;
		color: #718096;
	}
</style>
