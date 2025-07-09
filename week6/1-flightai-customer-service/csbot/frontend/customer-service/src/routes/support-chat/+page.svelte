<script lang="ts">
	import { onMount } from 'svelte';
	import { loadChatHistory } from '$lib/api';
	import type { Message } from '$lib/types';
	import { Send } from 'lucide-svelte';
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';

	let messages: Message[] = [];
	let userInput = '';
	let isLoading = false;
	let chatContainer: HTMLElement;

	onMount(async () => {
		isLoading = true;
		try {
			messages = await loadChatHistory();
		} catch (error) {
			console.error('Failed to load chat history:', error);
			// Show an error message to the user in a chat bubble
			messages = [
				{
					role: 'assistant',
					content: [{ text: "Sorry, I couldn't load the chat history." }]
				}
			];
		} finally {
			isLoading = false;
			setTimeout(scrollToBottom, 0);
		}
	});

	function scrollToBottom() {
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	}

	async function handleSubmit() {
		if (!userInput.trim()) return;
		isLoading = true;

		const promptValue = userInput.trim();
		const newUserMessage: Message = {
			role: 'user',
			content: [{ text: promptValue }]
		};

		const assistantMessage: Message = {
			role: 'assistant',
			content: [{ text: '' }]
		};

		messages = [...messages, newUserMessage, assistantMessage];
		userInput = '';
		setTimeout(scrollToBottom, 0);

		try {
			const response = await fetch('/api/chat', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ prompt: promptValue })
			});

			if (!response.ok) {
				throw new Error(`Network response was not ok: ${response.statusText}`);
			}

			if (!response.body) {
				throw new Error('Response has no body');
			}

			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			let buffer = '';

			while (true) {
				const { done, value } = await reader.read();
				if (done) {
					break;
				}

				buffer += decoder.decode(value, { stream: true });
				const lines = buffer.split('\n');
				buffer = lines.pop() || ''; // The last line might be incomplete.

				for (const line of lines) {
					if (line.startsWith('data: ')) {
						const jsonString = line.substring(6).trim();
						if (jsonString) {
							try {
								const chunk = JSON.parse(jsonString);
								assistantMessage.content[0].text += chunk;
								messages = messages; // to trigger reactivity
								scrollToBottom();
							} catch (e) {
								console.error('Failed to parse SSE data chunk:', jsonString, e);
							}
						}
					}
				}
			}
		} catch (error) {
			console.error('Error during chat stream:', error);
			assistantMessage.content[0].text = 'Sorry, something went wrong. Please try again.';
		} finally {
			isLoading = false;
			messages = messages; // to trigger reactivity
			setTimeout(scrollToBottom, 0);
		}
	}
</script>

<div class="chat-page-container">
	<h1 class="page-title">Support Chat</h1>

	<div class="chat-window" bind:this={chatContainer}>
		{#if isLoading && messages.length === 0}
			<div class="loading-history">
				<p>Loading chat history...</p>
			</div>
		{:else}
			{#each messages as message (message)}
				<div class="message-wrapper {message.role}">
					<div class="message-bubble">
						{#if message.content[0].text === '' && message.role === 'assistant' && isLoading}
							<div class="typing-indicator">
								<span /><span /><span />
							</div>
						{:else}
							{#if message.role === 'assistant'}
								{#each message.content as contentPart}
									{@html DOMPurify.sanitize(marked.parse(contentPart.text))}
								{/each}
							{:else}
								{#each message.content as contentPart}
									<p>{contentPart.text}</p>
								{/each}
							{/if}
						{/if}
					</div>
				</div>
			{/each}
		{/if}
	</div>

	<form class="chat-input-form" on:submit|preventDefault={handleSubmit}>
		<input
			type="text"
			class="chat-input"
			placeholder="Type your message..."
			bind:value={userInput}
			disabled={isLoading}
		/>
		<button type="submit" class="send-button" disabled={isLoading || !userInput.trim()}>
			<Send size={20} />
		</button>
	</form>
</div>

<style>
	.chat-page-container {
		display: flex;
		flex-direction: column;
		height: calc(100vh - 40px); /* Account for parent padding */
		max-width: 800px;
		margin: 0 auto;
	}

	.page-title {
		font-size: 2rem;
		margin-bottom: 20px;
		color: #333;
	}

	.chat-window {
		flex-grow: 1;
		overflow-y: auto;
		padding: 20px;
		border: 1px solid #ddd;
		border-radius: 8px;
		background-color: #f9f9f9;
		margin-bottom: 20px;
		display: flex;
		flex-direction: column;
		gap: 15px;
	}

	.loading-history {
		text-align: center;
		color: #888;
		margin: auto;
	}

	.message-wrapper {
		display: flex;
		max-width: 85%;
	}

	.message-wrapper.user {
		align-self: flex-end;
		flex-direction: row-reverse;
	}

	.message-wrapper.assistant {
		align-self: flex-start;
	}

	.message-bubble {
		padding: 12px 18px;
		border-radius: 20px;
		word-wrap: break-word;
	}

	.message-wrapper.user .message-bubble {
		background-color: #007bff;
		color: white;
		border-bottom-right-radius: 5px;
	}

	.message-wrapper.assistant .message-bubble {
		background-color: #fff;
		color: #333;
		border: 1px solid #eee;
		border-bottom-left-radius: 5px;
	}

	.message-bubble p {
		margin: 0;
		white-space: pre-wrap;
	}

	.chat-input-form {
		display: flex;
		gap: 10px;
		align-items: center;
	}

	.chat-input {
		flex-grow: 1;
		padding: 10px 15px;
		border: 1px solid #ccc;
		border-radius: 20px;
		font-size: 1rem;
		outline: none;
		transition: border-color 0.2s;
	}
	.chat-input:focus {
		border-color: #007bff;
	}

	.send-button {
		background-color: #007bff;
		color: white;
		border: none;
		border-radius: 50%;
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		transition: background-color 0.2s;
		flex-shrink: 0;
	}

	.send-button:hover:not(:disabled) {
		background-color: #0056b3;
	}

	.send-button:disabled {
		background-color: #c0c0c0;
		cursor: not-allowed;
	}

	.typing-indicator {
		display: flex;
		align-items: center;
		padding: 5px 0;
	}
	.typing-indicator span {
		height: 8px;
		width: 8px;
		background-color: #999;
		border-radius: 50%;
		display: inline-block;
		margin: 0 2px;
		animation: bounce 1.4s infinite ease-in-out both;
	}
	.typing-indicator span:nth-child(1) {
		animation-delay: -0.32s;
	}
	.typing-indicator span:nth-child(2) {
		animation-delay: -0.16s;
	}
	@keyframes bounce {
		0%,
		80%,
		100% {
			transform: scale(0);
		}
		40% {
			transform: scale(1);
		}
	}
</style>
