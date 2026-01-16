<script lang="ts">
	import { goto } from '$app/navigation';
	import Navbar from '$lib/components/Navbar.svelte';
	import { MODELS, PERSONA_INFO, type Persona } from '$lib/types';

	interface Props {
		data: {
			rankings: Array<{
				rank: number;
				modelKey: string;
				elo: number;
				wins: number;
				losses: number;
				totalComparisons: number;
				winRate: string;
			}>;
			taskBreakdown: Array<{
				taskId: string;
				taskTitle: string;
				rankings: Array<{
					modelKey: string;
					eloRating: number;
					comparisons: number;
				}>;
			}>;
			selectedPersona: string | null;
		};
	}

	let { data }: Props = $props();

	const personas: Persona[] = ['educator', 'developer', 'policymaker'];

	function getModelInfo(modelKey: string) {
		return MODELS.find((m) => m.key === modelKey);
	}

	function handlePersonaFilter(persona: string | null) {
		if (persona) {
			goto(`/leaderboard?persona=${persona}`);
		} else {
			goto('/leaderboard');
		}
	}

	function getRankEmoji(rank: number) {
		if (rank === 1) return '🥇';
		if (rank === 2) return '🥈';
		if (rank === 3) return '🥉';
		return `#${rank}`;
	}
</script>

<svelte:head>
	<title>Leaderboard - Micro Evals</title>
</svelte:head>

<Navbar />

<main class="max-w-6xl mx-auto px-4 py-8">
	<!-- Header -->
	<div class="mb-8">
		<h1 class="text-3xl font-bold text-dark mb-2">Model Leaderboard</h1>
		<p class="text-muted">
			Rankings based on Elo rating from head-to-head comparisons. Higher Elo = better performance.
		</p>
	</div>

	<!-- Persona Filter -->
	<div class="mb-8">
		<div class="flex items-center gap-2 flex-wrap">
			<span class="text-sm font-medium text-muted mr-2">Filter by persona:</span>
			<button
				onclick={() => handlePersonaFilter(null)}
				class="px-4 py-2 rounded-lg text-sm font-medium transition-all {!data.selectedPersona
					? 'bg-primary text-white'
					: 'bg-gray-100 text-muted hover:bg-gray-200'}"
			>
				All
			</button>
			{#each personas as persona}
				<button
					onclick={() => handlePersonaFilter(persona)}
					class="px-4 py-2 rounded-lg text-sm font-medium transition-all {data.selectedPersona ===
					persona
						? 'bg-primary text-white'
						: 'bg-gray-100 text-muted hover:bg-gray-200'}"
				>
					{PERSONA_INFO[persona].icon}
					{PERSONA_INFO[persona].label}
				</button>
			{/each}
		</div>
	</div>

	<!-- Global Rankings -->
	<div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-8">
		<div class="px-6 py-4 border-b border-gray-200">
			<h2 class="text-lg font-semibold text-dark">Global Rankings</h2>
		</div>

		{#if data.rankings.length === 0}
			<div class="p-8 text-center text-muted">
				<p>No votes recorded yet. Start voting to see rankings!</p>
				<a href="/compare" class="text-primary hover:underline mt-2 inline-block"> Go to Compare </a>
			</div>
		{:else}
			<table class="w-full">
				<thead class="bg-gray-50">
					<tr>
						<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
							Rank
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
							Model
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
							Elo Rating
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
							Win Rate
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
							W / L
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-muted uppercase tracking-wider">
							Comparisons
						</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-200">
					{#each data.rankings as entry (entry.modelKey)}
						{@const model = getModelInfo(entry.modelKey)}
						<tr class="hover:bg-gray-50">
							<td class="px-6 py-4 whitespace-nowrap text-2xl">
								{getRankEmoji(entry.rank)}
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="flex items-center gap-2">
									<span
										class="w-3 h-3 rounded-full"
										style="background-color: {model?.color || '#888'}"
									></span>
									<span class="font-medium text-dark">{model?.name || entry.modelKey}</span>
								</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<span class="text-lg font-semibold text-dark">{entry.elo}</span>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<span class="text-muted">{entry.winRate}%</span>
							</td>
							<td class="px-6 py-4 whitespace-nowrap">
								<span class="text-green-600">{entry.wins}</span>
								<span class="text-gray-400 mx-1">/</span>
								<span class="text-red-600">{entry.losses}</span>
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-muted">
								{entry.totalComparisons}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	</div>

	<!-- Per-Task Breakdown (if persona selected) -->
	{#if data.selectedPersona && data.taskBreakdown.length > 0}
		<div class="space-y-6">
			<h2 class="text-lg font-semibold text-dark">
				Rankings by Task ({PERSONA_INFO[data.selectedPersona as Persona].label})
			</h2>

			{#each data.taskBreakdown as task (task.taskId)}
				<div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
					<div class="px-4 py-3 bg-gray-50 border-b border-gray-200">
						<h3 class="font-medium text-dark">{task.taskTitle}</h3>
					</div>
					<div class="p-4">
						<div class="flex items-center gap-4">
							{#each task.rankings as ranking, index (ranking.modelKey)}
								{@const model = getModelInfo(ranking.modelKey)}
								<div
									class="flex items-center gap-2 px-3 py-2 rounded-lg {index === 0
										? 'bg-primary-light border border-primary'
										: 'bg-gray-50'}"
								>
									<span class="text-lg">{getRankEmoji(index + 1)}</span>
									<span
										class="w-2 h-2 rounded-full"
										style="background-color: {model?.color || '#888'}"
									></span>
									<span class="font-medium">{model?.name}</span>
									<span class="text-muted text-sm">({ranking.eloRating})</span>
								</div>
							{/each}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}

	<!-- CTA -->
	<div class="mt-8 text-center">
		<a
			href="/compare?voting=true"
			class="inline-flex items-center gap-2 px-6 py-3 bg-primary text-white font-medium rounded-lg hover:bg-primary-dark transition-colors"
		>
			<span>Vote on Comparisons</span>
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
			</svg>
		</a>
	</div>
</main>
