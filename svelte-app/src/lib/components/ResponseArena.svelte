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

	// Get all available models from the task's responses
	let availableModels = $derived(
		task ? (Object.keys(task.responses) as string[]) : []
	);

	// Track which models are visible (all selected by default)
	let visibleModels = $state<Set<string>>(new Set());

	// Initialize visible models when task changes
	$effect(() => {
		if (task) {
			visibleModels = new Set(availableModels);
		}
	});

	// Filter to only show selected models
	let displayedModels = $derived(
		availableModels.filter((key) => visibleModels.has(key))
	);

	function getModelInfo(key: string) {
		return MODELS.find((m) => m.key === key) || {
			key,
			name: key.charAt(0).toUpperCase() + key.slice(1).replace(/-/g, ' '),
			color: '#888888'
		};
	}

	function toggleModel(modelKey: string) {
		if (visibleModels.has(modelKey)) {
			visibleModels.delete(modelKey);
		} else {
			visibleModels.add(modelKey);
		}
		// Create new Set to trigger reactivity
		visibleModels = new Set(visibleModels);
	}

	function handleSelectWinner(winner: string) {
		if (!task || isVoting) return;
		selectedWinner = winner;
	}

	async function handleVote() {
		if (!task || !selectedWinner || isVoting) return;

		// Find the loser (the other visible model)
		const loser = displayedModels.find((m) => m !== selectedWinner && task.responses[m]);
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

			<!-- Model Selection Checkboxes -->
			<div class="mb-6 bg-white rounded-lg border border-gray-200 p-4">
				<div class="flex items-center gap-2 mb-3">
					<span class="text-sm font-medium text-gray-700">Show models:</span>
					<button
						onclick={() => {
							visibleModels = new Set(availableModels);
						}}
						class="text-xs text-blue-600 hover:text-blue-700"
					>
						Select all
					</button>
					<span class="text-gray-400">|</span>
					<button
						onclick={() => {
							visibleModels = new Set();
						}}
						class="text-xs text-blue-600 hover:text-blue-700"
					>
						Deselect all
					</button>
				</div>
				<div class="flex flex-wrap gap-3">
					{#each availableModels as modelKey}
						{@const model = getModelInfo(modelKey)}
						<label class="flex items-center gap-2 cursor-pointer">
							<input
								type="checkbox"
								checked={visibleModels.has(modelKey)}
								onchange={() => toggleModel(modelKey)}
								class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
							/>
							<span
								class="w-2 h-2 rounded-full"
								style="background-color: {model.color}"
							></span>
							<span class="text-sm text-gray-700">{model.name}</span>
						</label>
					{/each}
				</div>
			</div>

			<!-- Responses Grid -->
			{#if displayedModels.length === 0}
				<div class="text-center py-12 text-gray-500">
					<p>No models selected. Check at least one model above to view responses.</p>
				</div>
			{:else}
				<div class="grid gap-6" style="grid-template-columns: repeat({displayedModels.length}, minmax(300px, 1fr));">
				{#each displayedModels as modelKey}
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
			{/if}

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
