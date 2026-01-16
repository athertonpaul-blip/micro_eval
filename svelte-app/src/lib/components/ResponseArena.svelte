<script lang="ts">
	import { marked } from 'marked';
	import type { TaskWithResponses } from '$lib/types';
	import { MODELS } from '$lib/types';

	interface Props {
		task: TaskWithResponses | null;
		isLoading: boolean;
		votingMode: boolean;
		onVote: (taskId: string, winner: string, loser: string) => Promise<any>;
	}

	let { task, isLoading, votingMode, onVote }: Props = $props();

	let selectedWinner: string | null = $state(null);
	let isVoting = $state(false);

	const models = ['gpt4o', 'claude', 'gemini'] as const;

	function getModelInfo(key: string) {
		return MODELS.find((m) => m.key === key);
	}

	function handleSelectWinner(winner: string) {
		if (!task || isVoting) return;
		selectedWinner = winner;
	}

	async function handleVote() {
		if (!task || !selectedWinner || isVoting) return;

		// Find the loser (the other model)
		const loser = models.find((m) => m !== selectedWinner && task.responses[m]);
		if (!loser) return;

		isVoting = true;
		try {
			await onVote(task.id, selectedWinner, loser);
			// Reset selection after successful vote
			selectedWinner = null;
		} catch (error) {
			console.error('Vote failed:', error);
			alert('Failed to submit vote. Please try again.');
		} finally {
			isVoting = false;
		}
	}

	function renderMarkdown(content: string): string {
		return marked.parse(content);
	}
</script>

<div class="flex-1 overflow-y-auto bg-gray-50">
	{#if !task}
		<div class="h-full flex items-center justify-center">
			<div class="text-center text-gray-500">
				<p class="text-lg mb-2">Select a task to view responses</p>
				<p class="text-sm">Choose a task from the sidebar to compare AI model responses</p>
			</div>
		</div>
	{:else if isLoading}
		<div class="h-full flex items-center justify-center">
			<div class="text-center">
				<div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
				<p class="text-gray-600">Loading responses...</p>
			</div>
		</div>
	{:else}
		<div class="max-w-7xl mx-auto p-6">
			<!-- Task Header -->
			<div class="mb-6">
				<h2 class="text-2xl font-bold text-gray-900 mb-2">{task.title}</h2>
				<p class="text-gray-600">{task.description}</p>
			</div>

			<!-- Responses Grid -->
			<div class="grid md:grid-cols-3 gap-6">
				{#each models as modelKey}
					{@const model = getModelInfo(modelKey)}
					{@const content = task.responses[modelKey] || ''}
					<div
						class="bg-white rounded-lg shadow-sm border-2 transition-all {votingMode && selectedWinner ===
						modelKey
							? 'border-blue-500 ring-2 ring-blue-200'
							: votingMode
								? 'border-gray-200 hover:border-blue-300 cursor-pointer'
								: 'border-gray-200'}"
						onclick={() => votingMode && handleSelectWinner(modelKey)}
					>
						<!-- Model Header -->
						<div
							class="px-4 py-3 border-b border-gray-200 flex items-center justify-between"
							style="background-color: {model?.color || '#888'}20"
						>
							<div class="flex items-center gap-2">
								<span
									class="w-3 h-3 rounded-full"
									style="background-color: {model?.color || '#888'}"
								></span>
								<span class="font-semibold text-gray-900">{model?.name || modelKey}</span>
							</div>
							{#if votingMode && selectedWinner === modelKey}
								<span class="text-blue-600 font-medium">Selected</span>
							{/if}
						</div>

						<!-- Response Content -->
						<div class="p-4 prose prose-sm max-w-none">
							{#if content}
								{@html renderMarkdown(content)}
							{:else}
								<p class="text-gray-500 italic">No response available</p>
							{/if}
						</div>
					</div>
				{/each}
			</div>

			<!-- Voting Button -->
			{#if votingMode && selectedWinner}
				<div class="mt-6 flex justify-center">
					<button
						onclick={handleVote}
						disabled={isVoting}
						class="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
					>
						{isVoting ? 'Submitting vote...' : 'Submit Vote'}
					</button>
				</div>
			{/if}
		</div>
	{/if}
</div>
