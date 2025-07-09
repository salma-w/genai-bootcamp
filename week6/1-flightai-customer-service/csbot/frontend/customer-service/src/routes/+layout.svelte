<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import '../app.css';
</script>

<div class="app-container">
	<Sidebar />
	<main class="main-content">
		<slot />
	</main>
</div>

<style>
	.app-container {
		display: flex;
		height: 100vh;
	}

	.main-content {
		flex-grow: 1;
		padding: 20px;
		overflow: auto;
	}
</style>
