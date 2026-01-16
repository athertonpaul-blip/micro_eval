<script lang="ts">
	import { goto } from '$app/navigation';
	import { PERSONA_INFO, type Persona } from '$lib/types';

	interface Props {
		currentPersona?: Persona;
		showPersonaToggle?: boolean;
		onPersonaChange?: (persona: Persona) => void;
		onExit?: () => void;
	}

	let {
		currentPersona,
		showPersonaToggle = false,
		onPersonaChange,
		onExit
	}: Props = $props();

	const personas: Persona[] = ['educator', 'developer', 'policymaker'];

	function handlePersonaClick(persona: Persona) {
		if (onPersonaChange) {
			onPersonaChange(persona);
		} else {
			goto(`/compare?persona=${persona}`);
		}
	}

	function handleHome() {
		if (onExit) {
			onExit();
		} else {
			goto('/');
		}
	}
</script>

<nav class="bg-white border-b border-gray-200 px-4 py-3">
	<div class="max-w-7xl mx-auto flex items-center justify-between">
		<!-- Logo/Home -->
		<button onclick={handleHome} class="flex items-center gap-2 text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors">
			<span>Micro Evals</span>
		</button>

		<!-- Navigation Links -->
		<div class="flex items-center gap-6">
			<a href="/compare" class="text-gray-700 hover:text-blue-600 transition-colors font-medium">
				Compare
			</a>
			<a href="/leaderboard" class="text-gray-700 hover:text-blue-600 transition-colors font-medium">
				Leaderboard
			</a>

			{#if showPersonaToggle && currentPersona}
				<!-- Persona Selector -->
				<div class="flex items-center gap-2 border-l border-gray-200 pl-6 ml-6">
					<span class="text-sm text-gray-500 mr-2">View:</span>
					<div class="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
						{#each personas as persona}
							<button
								onclick={() => handlePersonaClick(persona)}
								class="px-3 py-1.5 rounded-md text-sm font-medium transition-colors {currentPersona ===
								persona
									? 'bg-white text-gray-900 shadow-sm'
									: 'text-gray-600 hover:text-gray-900'}"
							>
								{PERSONA_INFO[persona].icon} {PERSONA_INFO[persona].label}
							</button>
						{/each}
					</div>
				</div>
			{/if}
		</div>
	</div>
</nav>
