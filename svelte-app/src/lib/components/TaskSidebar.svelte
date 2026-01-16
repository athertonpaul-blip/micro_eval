<script lang="ts">
	import type { TaskWithResponses } from '$lib/types';

	interface Props {
		tasks: TaskWithResponses[];
		selectedTaskId: string | null;
		onSelectTask: (task: TaskWithResponses) => void;
	}

	let { tasks, selectedTaskId, onSelectTask }: Props = $props();
</script>

<aside class="w-80 bg-white border-r border-gray-200 overflow-y-auto">
	<div class="p-4">
		<h2 class="text-lg font-semibold text-gray-900 mb-4">Tasks</h2>
		{#if tasks.length === 0}
			<p class="text-gray-500 text-sm">No tasks available</p>
		{:else}
			<div class="space-y-2">
				{#each tasks as task (task.id)}
					<button
						onclick={() => onSelectTask(task)}
						class="w-full text-left px-4 py-3 rounded-lg transition-all {selectedTaskId === task.id
							? 'bg-blue-50 border-2 border-blue-500 text-blue-900'
							: 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent text-gray-900'}"
					>
						<div class="font-medium mb-1">{task.title}</div>
						<div class="text-xs text-gray-500 line-clamp-2">{task.description}</div>
					</button>
				{/each}
			</div>
		{/if}
	</div>
</aside>
