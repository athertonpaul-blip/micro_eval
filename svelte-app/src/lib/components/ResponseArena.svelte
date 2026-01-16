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

	let isVoting = $state(false);
	let voteResult = $state<{
		winner: { model: string; newRating: number; change: string };
		loser: { model: string; newRating: number; change: string };
		selectedSide: 'A' | 'B';
	} | null>(null);

	// For A vs B voting: randomly selected pair
	let modelA = $state<string | null>(null);
	let modelB = $state<string | null>(null);

	// Track expanded state for each response card
	let expandedA = $state(false);
	let expandedB = $state(false);

	// Track expanded state for compare mode (multiple models)
	let expandedModels = $state<Set<string>>(new Set());

	// Get all available models from the task's responses
	let availableModels = $derived(task ? (Object.keys(task.responses) as string[]) : []);

	// Track which models are visible (for compare mode)
	let visibleModels = $state<Set<string>>(new Set());

	// Initialize visible models and random pair when task changes
	$effect(() => {
		if (task) {
			visibleModels = new Set(availableModels);
			expandedModels = new Set();
			voteResult = null;
			selectRandomPair();
		}
	});

	function toggleExpanded(modelKey: string) {
		if (expandedModels.has(modelKey)) {
			expandedModels.delete(modelKey);
		} else {
			expandedModels.add(modelKey);
		}
		expandedModels = new Set(expandedModels);
	}

	// Re-select random pair when switching to voting mode
	$effect(() => {
		if (votingMode && task && !voteResult) {
			selectRandomPair();
		}
	});

	function selectRandomPair() {
		if (availableModels.length < 2) return;

		// Shuffle and pick first two
		const shuffled = [...availableModels].sort(() => Math.random() - 0.5);
		modelA = shuffled[0];
		modelB = shuffled[1];
		// Reset expanded states for new matchup
		expandedA = false;
		expandedB = false;
	}

	// Filter to only show selected models (for compare mode)
	let displayedModels = $derived(availableModels.filter((key) => visibleModels.has(key)));

	function getModelInfo(key: string) {
		return (
			MODELS.find((m) => m.key === key) || {
				key,
				name: key.charAt(0).toUpperCase() + key.slice(1).replace(/-/g, ' '),
				color: '#888888'
			}
		);
	}

	function toggleModel(modelKey: string) {
		if (visibleModels.has(modelKey)) {
			visibleModels.delete(modelKey);
		} else {
			visibleModels.add(modelKey);
		}
		visibleModels = new Set(visibleModels);
	}

	async function handleVote(selectedSide: 'A' | 'B') {
		if (!task || !modelA || !modelB || isVoting) return;

		const winner = selectedSide === 'A' ? modelA : modelB;
		const loser = selectedSide === 'A' ? modelB : modelA;

		isVoting = true;
		try {
			const result = await onVote(task.id, winner, loser);
			voteResult = {
				...result,
				selectedSide
			};
		} catch (error) {
			console.error('Vote failed:', error);
			alert('Failed to submit vote. Please try again.');
		} finally {
			isVoting = false;
		}
	}

	function nextMatchup() {
		voteResult = null;
		selectRandomPair();
	}

	function renderMarkdown(content: string): string {
		return marked.parse(content) as string;
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
				<div
					class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"
				></div>
				<p class="text-gray-600">Loading responses...</p>
			</div>
		</div>
	{:else if votingMode}
		<!-- A vs B Voting Mode -->
		<div class="max-w-6xl mx-auto p-6">
			<!-- Task Header -->
			<div class="mb-6 text-center">
				<h2 class="text-2xl font-bold text-gray-900 mb-2">{task.title}</h2>
				<p class="text-gray-600">{task.description}</p>
			</div>

			{#if voteResult}
				<!-- Vote Result Reveal -->
				<div class="mb-6 bg-white rounded-lg border border-gray-200 p-6 text-center">
					<h3 class="text-xl font-semibold text-gray-900 mb-4">Results Revealed!</h3>
					<div class="flex justify-center gap-8 mb-6">
						<div class="text-center">
							<div
								class="text-sm text-gray-500 mb-1"
								style="color: {getModelInfo(modelA!).color}"
							>
								Response A
							</div>
							<div class="font-semibold text-lg" style="color: {getModelInfo(modelA!).color}">
								{getModelInfo(modelA!).name}
							</div>
							<div
								class="text-sm {voteResult.selectedSide === 'A'
									? 'text-green-600 font-medium'
									: 'text-red-600'}"
							>
								{voteResult.selectedSide === 'A' ? voteResult.winner.change : voteResult.loser.change}
							</div>
						</div>
						<div class="text-2xl text-gray-400 self-center">vs</div>
						<div class="text-center">
							<div
								class="text-sm text-gray-500 mb-1"
								style="color: {getModelInfo(modelB!).color}"
							>
								Response B
							</div>
							<div class="font-semibold text-lg" style="color: {getModelInfo(modelB!).color}">
								{getModelInfo(modelB!).name}
							</div>
							<div
								class="text-sm {voteResult.selectedSide === 'B'
									? 'text-green-600 font-medium'
									: 'text-red-600'}"
							>
								{voteResult.selectedSide === 'B' ? voteResult.winner.change : voteResult.loser.change}
							</div>
						</div>
					</div>
					<p class="text-gray-600 mb-4">
						You voted for <span class="font-semibold">{getModelInfo(voteResult.selectedSide === 'A' ? modelA! : modelB!).name}</span>
					</p>
					<button
						onclick={nextMatchup}
						class="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
					>
						Next Matchup
					</button>
				</div>
			{:else}
				<!-- Voting Instructions -->
				<div class="mb-6 text-center">
					<p class="text-gray-500 text-sm">
						Which response is better? Expand to read more, then vote.
					</p>
				</div>
			{/if}

			<!-- A vs B Response Cards -->
			{#if modelA && modelB}
				<div class="grid grid-cols-2 gap-6">
					<!-- Response A -->
					<div
						class="bg-white rounded-lg shadow-sm border-2 transition-all {voteResult?.selectedSide === 'A' ? 'ring-2 ring-green-400 border-green-400' : 'border-gray-200'}"
					>
						<!-- Header -->
						<div
							class="px-4 py-3 border-b flex items-center justify-between {voteResult
								? ''
								: 'bg-blue-50'}"
							style={voteResult ? `background-color: ${getModelInfo(modelA).color}20` : ''}
						>
							<div class="flex items-center gap-2">
								{#if voteResult}
									<span
										class="w-3 h-3 rounded-full"
										style="background-color: {getModelInfo(modelA).color}"
									></span>
									<span class="font-semibold text-gray-900">{getModelInfo(modelA).name}</span>
								{:else}
									<span class="w-3 h-3 rounded-full bg-blue-500"></span>
									<span class="font-semibold text-gray-900">Response A</span>
								{/if}
							</div>
							{#if voteResult?.selectedSide === 'A'}
								<span class="text-green-600 font-medium">Winner</span>
							{/if}
						</div>

						<!-- Content -->
						<div class="relative">
							<div
								class="p-4 prose prose-sm max-w-none overflow-hidden transition-all duration-300"
								style={expandedA ? 'max-height: none;' : 'max-height: 200px;'}
							>
								{@html renderMarkdown(task.responses[modelA] || '')}
							</div>
							{#if !expandedA}
								<div class="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-white to-transparent pointer-events-none"></div>
							{/if}
						</div>

						<!-- Expand/Collapse and Vote buttons -->
						<div class="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
							<button
								onclick={(e) => { e.stopPropagation(); expandedA = !expandedA; }}
								class="text-sm text-gray-500 hover:text-gray-700"
							>
								{expandedA ? 'Show less' : 'Show more'}
							</button>
							{#if !voteResult && !isVoting}
								<button
									onclick={() => handleVote('A')}
									class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
								>
									Vote for A
								</button>
							{/if}
						</div>
					</div>

					<!-- Response B -->
					<div
						class="bg-white rounded-lg shadow-sm border-2 transition-all {voteResult?.selectedSide === 'B' ? 'ring-2 ring-green-400 border-green-400' : 'border-gray-200'}"
					>
						<!-- Header -->
						<div
							class="px-4 py-3 border-b flex items-center justify-between {voteResult
								? ''
								: 'bg-orange-50'}"
							style={voteResult ? `background-color: ${getModelInfo(modelB).color}20` : ''}
						>
							<div class="flex items-center gap-2">
								{#if voteResult}
									<span
										class="w-3 h-3 rounded-full"
										style="background-color: {getModelInfo(modelB).color}"
									></span>
									<span class="font-semibold text-gray-900">{getModelInfo(modelB).name}</span>
								{:else}
									<span class="w-3 h-3 rounded-full bg-orange-500"></span>
									<span class="font-semibold text-gray-900">Response B</span>
								{/if}
							</div>
							{#if voteResult?.selectedSide === 'B'}
								<span class="text-green-600 font-medium">Winner</span>
							{/if}
						</div>

						<!-- Content -->
						<div class="relative">
							<div
								class="p-4 prose prose-sm max-w-none overflow-hidden transition-all duration-300"
								style={expandedB ? 'max-height: none;' : 'max-height: 200px;'}
							>
								{@html renderMarkdown(task.responses[modelB] || '')}
							</div>
							{#if !expandedB}
								<div class="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-white to-transparent pointer-events-none"></div>
							{/if}
						</div>

						<!-- Expand/Collapse and Vote buttons -->
						<div class="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
							<button
								onclick={(e) => { e.stopPropagation(); expandedB = !expandedB; }}
								class="text-sm text-gray-500 hover:text-gray-700"
							>
								{expandedB ? 'Show less' : 'Show more'}
							</button>
							{#if !voteResult && !isVoting}
								<button
									onclick={() => handleVote('B')}
									class="px-4 py-2 bg-orange-600 text-white text-sm font-medium rounded-lg hover:bg-orange-700 transition-colors"
								>
									Vote for B
								</button>
							{/if}
						</div>
					</div>
				</div>
			{/if}

			{#if isVoting}
				<div class="mt-6 flex justify-center">
					<div class="flex items-center gap-2 text-gray-600">
						<div
							class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"
						></div>
						<span>Submitting vote...</span>
					</div>
				</div>
			{/if}
		</div>
	{:else}
		<!-- Compare Mode (original behavior) -->
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
							<span class="w-2 h-2 rounded-full" style="background-color: {model.color}"></span>
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
				<div
					class="grid gap-6"
					style="grid-template-columns: repeat({displayedModels.length}, minmax(300px, 1fr));"
				>
					{#each displayedModels as modelKey}
						{@const model = getModelInfo(modelKey)}
						{@const content = task.responses[modelKey] || ''}
						{@const isExpanded = expandedModels.has(modelKey)}
						<div class="bg-white rounded-lg shadow-sm border-2 border-gray-200">
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
							</div>

							<!-- Response Content -->
							<div class="relative">
								<div
									class="p-4 prose prose-sm max-w-none overflow-hidden transition-all duration-300"
									style={isExpanded ? 'max-height: none;' : 'max-height: 200px;'}
								>
									{#if content}
										{@html renderMarkdown(content)}
									{:else}
										<p class="text-gray-500 italic">No response available</p>
									{/if}
								</div>
								{#if !isExpanded && content}
									<div class="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-white to-transparent pointer-events-none"></div>
								{/if}
							</div>

							<!-- Expand/Collapse button -->
							{#if content}
								<div class="px-4 py-2 border-t border-gray-100">
									<button
										onclick={() => toggleExpanded(modelKey)}
										class="text-sm text-gray-500 hover:text-gray-700"
									>
										{isExpanded ? 'Show less' : 'Show more'}
									</button>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>
