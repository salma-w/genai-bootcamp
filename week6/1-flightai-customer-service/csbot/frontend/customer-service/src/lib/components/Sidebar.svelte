<script lang="ts">
	import { Plane, MessageSquare } from 'lucide-svelte';
</script>

<aside class="sidebar">
	<nav>
		<ul>
			<li>
				<a href="/trips">
					<Plane class="icon" />
					<span>Trips</span>
				</a>
			</li>
			<li>
				<a href="/support-chat">
					<MessageSquare class="icon" />
					<span>Support Chat</span>
				</a>
			</li>
		</ul>
	</nav>
</aside>

<style>
	.sidebar {
		width: 250px;
		background-color: #f4f4f4;
		padding: 20px;
		height: 100vh;
		border-right: 1px solid #ddd;
	}
	nav ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	nav li a {
		display: flex;
		align-items: center;
		padding: 10px;
		text-decoration: none;
		color: #333;
		border-radius: 5px;
		margin-bottom: 10px;
	}
	nav li a:hover {
		background-color: #e0e0e0;
	}
	.icon {
		margin-right: 10px;
	}
</style>
