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

<nav class="bg-white border-b border-gray-200 px-3 sm:px-4 py-2 sm:py-3">
	<div class="max-w-7xl mx-auto flex items-center justify-between gap-2">
		<!-- Logo/Home -->
		<div class="flex items-center gap-2 sm:gap-4 shrink-0">
			<a href="https://fab-ai.org" class="hover:opacity-70 transition-opacity hidden sm:block">
				<img src="/Fab-AI-logo-black-transparent.svg" alt="Fab AI" class="h-6" />
			</a>
			<span class="text-gray-300 hidden sm:block">|</span>
			<button onclick={handleHome} class="flex items-center gap-1.5 sm:gap-2 text-sm sm:text-base font-medium text-dark hover:text-primary transition-colors">
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
				</svg>
				<span>Home</span>
			</button>
		</div>

		<!-- Navigation Links -->
		<div class="flex items-center gap-2 sm:gap-6">
			<a href="/compare" class="text-muted hover:text-primary transition-colors font-medium text-sm sm:text-base">
				Compare
			</a>
			<a href="/leaderboard" class="text-muted hover:text-primary transition-colors font-medium text-sm sm:text-base">
				Leaderboard
			</a>

			{#if showPersonaToggle && currentPersona}
				<!-- Persona Selector - icons only on mobile -->
				<div class="flex items-center gap-1 sm:gap-2 border-l border-gray-200 pl-2 sm:pl-6 ml-1 sm:ml-6">
					<span class="text-sm text-muted mr-1 sm:mr-2 hidden md:block">View:</span>
					<div class="flex items-center gap-0.5 sm:gap-1 bg-gray-100 rounded-lg p-0.5 sm:p-1">
						{#each personas as persona}
							<button
								onclick={() => handlePersonaClick(persona)}
								class="px-1.5 sm:px-3 py-1 sm:py-1.5 rounded-md text-xs sm:text-sm font-medium transition-colors flex items-center gap-1 sm:gap-2 {currentPersona ===
								persona
									? 'bg-white text-dark shadow-sm'
									: 'text-muted hover:text-dark'}"
								title={PERSONA_INFO[persona].label}
							>
								<img src={PERSONA_INFO[persona].image} alt="" class="w-5 h-5 sm:w-4 sm:h-4 rounded-full object-cover" />
								<span class="hidden sm:inline">{PERSONA_INFO[persona].label}</span>
							</button>
						{/each}
					</div>
				</div>
			{/if}
		</div>
	</div>
</nav>
