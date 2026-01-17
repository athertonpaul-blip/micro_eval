<script lang="ts">
	import type { Domain, Category, UseCase, EducatorTask } from '$lib/types';

	interface Props {
		hierarchy: Domain[];
		selectedTaskId: string | null;
		onSelectTask: (task: EducatorTask) => void;
	}

	let { hierarchy, selectedTaskId, onSelectTask }: Props = $props();

	// Navigation state
	let selectedDomain = $state<Domain | null>(null);
	let selectedCategory = $state<Category | null>(null);
	let selectedUseCase = $state<UseCase | null>(null);

	// Breadcrumb navigation
	type Level = 'domains' | 'categories' | 'useCases' | 'tasks';
	let currentLevel = $derived<Level>(
		selectedUseCase ? 'tasks' :
		selectedCategory ? 'useCases' :
		selectedDomain ? 'categories' :
		'domains'
	);

	function selectDomain(domain: Domain) {
		selectedDomain = domain;
		selectedCategory = null;
		selectedUseCase = null;
	}

	function selectCategory(category: Category) {
		selectedCategory = category;
		selectedUseCase = null;
	}

	function selectUseCase(useCase: UseCase) {
		selectedUseCase = useCase;
	}

	function goBack() {
		if (selectedUseCase) {
			selectedUseCase = null;
		} else if (selectedCategory) {
			selectedCategory = null;
		} else if (selectedDomain) {
			selectedDomain = null;
		}
	}

	function goToLevel(level: Level) {
		if (level === 'domains') {
			selectedDomain = null;
			selectedCategory = null;
			selectedUseCase = null;
		} else if (level === 'categories') {
			selectedCategory = null;
			selectedUseCase = null;
		} else if (level === 'useCases') {
			selectedUseCase = null;
		}
	}

	// Get count of tasks at each level
	function getDomainTaskCount(domain: Domain): number {
		return domain.categories.reduce((sum, cat) =>
			sum + cat.useCases.reduce((ucSum, uc) => ucSum + uc.tasks.length, 0), 0);
	}

	function getCategoryTaskCount(category: Category): number {
		return category.useCases.reduce((sum, uc) => sum + uc.tasks.length, 0);
	}
</script>

<aside class="w-80 max-w-[85vw] h-full bg-white border-r border-gray-200 overflow-y-auto shadow-lg md:shadow-none flex flex-col">
	<!-- Header with breadcrumb -->
	<div class="p-4 border-b border-gray-200 bg-gray-50">
		{#if currentLevel !== 'domains'}
			<button
				onclick={goBack}
				class="flex items-center gap-2 text-sm text-primary hover:text-primary-dark mb-2 transition-colors"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
				</svg>
				Back
			</button>
		{/if}

		<!-- Breadcrumb -->
		<div class="flex flex-wrap items-center gap-1 text-xs text-muted">
			<button
				onclick={() => goToLevel('domains')}
				class="hover:text-primary transition-colors {currentLevel === 'domains' ? 'text-dark font-medium' : ''}"
			>
				All Domains
			</button>
			{#if selectedDomain}
				<span class="text-gray-400">/</span>
				<button
					onclick={() => goToLevel('categories')}
					class="hover:text-primary transition-colors truncate max-w-[80px] {currentLevel === 'categories' ? 'text-dark font-medium' : ''}"
					title={selectedDomain.name}
				>
					{selectedDomain.name}
				</button>
			{/if}
			{#if selectedCategory}
				<span class="text-gray-400">/</span>
				<button
					onclick={() => goToLevel('useCases')}
					class="hover:text-primary transition-colors truncate max-w-[80px] {currentLevel === 'useCases' ? 'text-dark font-medium' : ''}"
					title={selectedCategory.name}
				>
					{selectedCategory.name}
				</button>
			{/if}
			{#if selectedUseCase}
				<span class="text-gray-400">/</span>
				<span class="text-dark font-medium truncate max-w-[80px]" title={selectedUseCase.name}>
					{selectedUseCase.name}
				</span>
			{/if}
		</div>
	</div>

	<!-- Content area -->
	<div class="flex-1 overflow-y-auto p-4">
		{#if currentLevel === 'domains'}
			<!-- Domain list -->
			<h2 class="text-lg font-semibold text-dark mb-4">Select a Domain</h2>
			<div class="space-y-2">
				{#each hierarchy as domain (domain.id)}
					<button
						onclick={() => selectDomain(domain)}
						class="w-full text-left px-4 py-4 rounded-lg bg-gray-50 hover:bg-primary-light border-2 border-transparent hover:border-primary transition-all group"
					>
						<div class="font-medium text-dark group-hover:text-primary-dark">{domain.name}</div>
						<div class="text-xs text-muted mt-1">
							{domain.categories.length} categories, {getDomainTaskCount(domain)} tasks
						</div>
					</button>
				{/each}
			</div>

		{:else if currentLevel === 'categories' && selectedDomain}
			<!-- Category list -->
			<h2 class="text-lg font-semibold text-dark mb-4">{selectedDomain.name}</h2>
			<p class="text-sm text-muted mb-4">Select a category</p>
			<div class="space-y-2">
				{#each selectedDomain.categories as category (category.id)}
					<button
						onclick={() => selectCategory(category)}
						class="w-full text-left px-4 py-3 rounded-lg bg-gray-50 hover:bg-primary-light border-2 border-transparent hover:border-primary transition-all group"
					>
						<div class="font-medium text-dark group-hover:text-primary-dark">{category.name}</div>
						<div class="text-xs text-muted mt-1">
							{category.useCases.length} use cases, {getCategoryTaskCount(category)} tasks
						</div>
					</button>
				{/each}
			</div>

		{:else if currentLevel === 'useCases' && selectedCategory}
			<!-- Use case list -->
			<h2 class="text-lg font-semibold text-dark mb-4">{selectedCategory.name}</h2>
			<p class="text-sm text-muted mb-4">Select a use case</p>
			<div class="space-y-2">
				{#each selectedCategory.useCases as useCase (useCase.id)}
					<button
						onclick={() => selectUseCase(useCase)}
						class="w-full text-left px-4 py-3 rounded-lg bg-gray-50 hover:bg-primary-light border-2 border-transparent hover:border-primary transition-all group"
					>
						<div class="font-medium text-dark group-hover:text-primary-dark">{useCase.name}</div>
						<div class="text-xs text-muted mt-1">{useCase.tasks.length} micro-tasks</div>
					</button>
				{/each}
			</div>

		{:else if currentLevel === 'tasks' && selectedUseCase}
			<!-- Task list -->
			<h2 class="text-lg font-semibold text-dark mb-4">{selectedUseCase.name}</h2>
			<p class="text-sm text-muted mb-4">{selectedUseCase.tasks.length} micro-tasks</p>
			<div class="space-y-2">
				{#each selectedUseCase.tasks as task (task.id)}
					<button
						onclick={() => onSelectTask(task)}
						class="w-full text-left px-4 py-3 rounded-lg transition-all {selectedTaskId === task.id
							? 'bg-primary-light border-2 border-primary text-dark'
							: 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent text-dark'}"
					>
						<div class="font-medium mb-1">{task.title}</div>
						<div class="text-xs text-muted line-clamp-2">{task.prompt}</div>
					</button>
				{/each}
			</div>
		{/if}
	</div>

	<!-- Footer with stats -->
	<div class="p-3 border-t border-gray-200 bg-gray-50 text-xs text-muted text-center">
		{hierarchy.length} domains, {hierarchy.reduce((s, d) => s + getDomainTaskCount(d), 0)} total tasks
	</div>
</aside>
