<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import Navbar from '$lib/components/Navbar.svelte';
	import TaskSidebar from '$lib/components/TaskSidebar.svelte';
	import ResponseArena from '$lib/components/ResponseArena.svelte';
	import type { Persona, TaskWithResponses } from '$lib/types';

	interface Props {
		data: {
			tasks: TaskWithResponses[];
			initialPersona: Persona;
		};
	}

	let { data }: Props = $props();

	// Use derived to reactively get the initial persona
	let initialPersona = $derived(data.initialPersona);
	let currentPersona = $state<Persona>(initialPersona);
	let selectedTask = $state<TaskWithResponses | null>(null);
	let isLoading = $state(false);

	// Update currentPersona when data.initialPersona changes
	$effect(() => {
		currentPersona = initialPersona;
	});

	// Check if voting mode is enabled via URL param
	let votingMode = $derived($page.url.searchParams.get('voting') === 'true');

	// Filter tasks by persona
	let filteredTasks = $derived(data.tasks.filter((t) => t.persona === currentPersona));

	function handlePersonaChange(persona: Persona) {
		currentPersona = persona;
		selectedTask = null;
		// Update URL without navigation
		const url = new URL(window.location.href);
		url.searchParams.set('persona', persona);
		window.history.replaceState({}, '', url);
	}

	function handleSelectTask(task: TaskWithResponses) {
		// Simulate loading for better UX (like the original)
		isLoading = true;
		selectedTask = task;

		// Staggered reveal like the original
		setTimeout(() => {
			isLoading = false;
		}, 600 + Math.random() * 400);
	}

	function handleExit() {
		goto('/');
	}

	function toggleVotingMode() {
		const url = new URL(window.location.href);
		if (votingMode) {
			url.searchParams.delete('voting');
		} else {
			url.searchParams.set('voting', 'true');
		}
		window.history.replaceState({}, '', url);
		// Force reactivity update
		goto(url.toString(), { replaceState: true });
	}

	async function handleVote(taskId: string, winner: string, loser: string) {
		const response = await fetch('/api/vote', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ taskId, winner, loser })
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.message || 'Vote failed');
		}

		return response.json();
	}
</script>

<svelte:head>
	<title>{votingMode ? 'Vote' : 'Compare'} - Micro Evals</title>
</svelte:head>

<div class="h-screen flex flex-col overflow-hidden">
	<Navbar
		{currentPersona}
		onPersonaChange={handlePersonaChange}
		showPersonaToggle={true}
		onExit={handleExit}
	/>

	<!-- Mode toggle bar -->
	<div class="bg-gray-100 border-b border-gray-200 px-4 py-2 flex items-center justify-between">
		<div class="flex items-center gap-4">
			<span class="text-sm text-gray-600">Mode:</span>
			<div class="flex items-center gap-1 bg-white rounded-lg p-1 shadow-sm">
				<button
					onclick={toggleVotingMode}
					class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors {!votingMode
						? 'bg-blue-600 text-white'
						: 'text-gray-600 hover:text-gray-900'}"
				>
					Compare
				</button>
				<button
					onclick={toggleVotingMode}
					class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors {votingMode
						? 'bg-blue-600 text-white'
						: 'text-gray-600 hover:text-gray-900'}"
				>
					Vote
				</button>
			</div>
		</div>
		{#if votingMode}
			<p class="text-sm text-gray-500">
				Select a task, then vote for the better response (blind A vs B)
			</p>
		{/if}
	</div>

	<div class="flex-1 flex overflow-hidden">
		<TaskSidebar
			tasks={filteredTasks}
			selectedTaskId={selectedTask?.id ?? null}
			onSelectTask={handleSelectTask}
		/>

		<ResponseArena
			task={selectedTask}
			{isLoading}
			{votingMode}
			onVote={handleVote}
		/>
	</div>
</div>
