<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import Navbar from '$lib/components/Navbar.svelte';
	import TaskSidebar from '$lib/components/TaskSidebar.svelte';
	import HierarchicalSidebar from '$lib/components/HierarchicalSidebar.svelte';
	import ResponseArena from '$lib/components/ResponseArena.svelte';
	import type { Persona, TaskWithResponses, Domain, EducatorTask } from '$lib/types';

	interface Props {
		data: {
			tasks: TaskWithResponses[];
			initialPersona: Persona;
			educatorHierarchy: Domain[];
			educatorFlatTasks: EducatorTask[];
		};
	}

	let { data }: Props = $props();

	// Use derived to reactively get the initial persona
	let initialPersona = $derived(data.initialPersona);
	let currentPersona = $state<Persona>(initialPersona);
	let selectedTask = $state<TaskWithResponses | null>(null);
	let isLoading = $state(false);
	let sidebarOpen = $state(false);

	// Update currentPersona when data.initialPersona changes
	$effect(() => {
		currentPersona = initialPersona;
	});

	// Check if voting mode is enabled via URL param
	let votingMode = $derived($page.url.searchParams.get('voting') === 'true');

	// Check if we're in educator mode with hierarchy
	let isEducatorMode = $derived(currentPersona === 'educator' && data.educatorHierarchy.length > 0);

	// Filter tasks by persona (for non-educator personas)
	let filteredTasks = $derived(data.tasks.filter((t) => t.persona === currentPersona));

	// Auto-select first task when tasks load or persona changes (only for non-educator)
	$effect(() => {
		if (!isEducatorMode && filteredTasks.length > 0 && !selectedTask) {
			handleSelectTask(filteredTasks[0]);
		}
	});

	// Convert educator task to TaskWithResponses format
	// Look up responses from database tasks since JSON doesn't have them
	function educatorTaskToTaskWithResponses(task: EducatorTask): TaskWithResponses {
		// Find the matching task from the database (which has responses)
		const dbTask = data.tasks.find(t => t.id === task.id);

		return {
			id: task.id,
			title: task.title,
			description: task.prompt,
			persona: 'educator',
			responses: dbTask?.responses || task.responses || {}
		};
	}

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
		// Close sidebar on mobile after selection
		sidebarOpen = false;

		// Staggered reveal like the original
		setTimeout(() => {
			isLoading = false;
		}, 600 + Math.random() * 400);
	}

	function handleSelectEducatorTask(task: EducatorTask) {
		handleSelectTask(educatorTaskToTaskWithResponses(task));
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
	<div class="bg-gray-50 border-b border-gray-200 px-3 sm:px-4 py-2 flex items-center justify-between gap-2">
		<div class="flex items-center gap-2 sm:gap-4">
			<!-- Mobile sidebar toggle -->
			<button
				onclick={() => sidebarOpen = !sidebarOpen}
				class="md:hidden p-2 -ml-1 text-muted hover:text-dark rounded-lg hover:bg-gray-200 transition-colors"
				aria-label="Toggle task list"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
				</svg>
			</button>
			<span class="text-sm text-muted hidden sm:inline">Mode:</span>
			<div class="flex items-center gap-1 bg-white rounded-lg p-1 shadow-sm">
				<button
					onclick={toggleVotingMode}
					class="px-2 sm:px-3 py-1.5 rounded-md text-sm font-medium transition-colors {!votingMode
						? 'bg-primary text-white'
						: 'text-muted hover:text-dark'}"
				>
					Compare
				</button>
				<button
					onclick={toggleVotingMode}
					class="px-2 sm:px-3 py-1.5 rounded-md text-sm font-medium transition-colors {votingMode
						? 'bg-primary text-white'
						: 'text-muted hover:text-dark'}"
				>
					Vote
				</button>
			</div>
		</div>
		{#if votingMode}
			<p class="text-sm text-muted hidden md:block">
				Select a task, then vote for the better response (blind A vs B)
			</p>
		{/if}
	</div>

	<div class="flex-1 flex overflow-hidden relative">
		<!-- Mobile overlay -->
		{#if sidebarOpen}
			<button
				class="fixed inset-0 bg-black/50 z-40 md:hidden"
				onclick={() => sidebarOpen = false}
				aria-label="Close sidebar"
			></button>
		{/if}

		<!-- Sidebar - drawer on mobile, always visible on desktop -->
		<div
			class="fixed md:relative top-0 bottom-0 left-0 z-50 md:z-auto transform transition-transform duration-300 ease-in-out md:transform-none {sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}"
		>
			{#if isEducatorMode}
				<HierarchicalSidebar
					hierarchy={data.educatorHierarchy}
					selectedTaskId={selectedTask?.id ?? null}
					onSelectTask={handleSelectEducatorTask}
				/>
			{:else}
				<TaskSidebar
					tasks={filteredTasks}
					selectedTaskId={selectedTask?.id ?? null}
					onSelectTask={handleSelectTask}
				/>
			{/if}
		</div>

		<ResponseArena
			task={selectedTask}
			{isLoading}
			{votingMode}
			onVote={handleVote}
		/>
	</div>
</div>
