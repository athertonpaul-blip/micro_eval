<script lang="ts">
	import { goto } from '$app/navigation';
	import type { Persona } from '$lib/types';
	import { PERSONA_INFO } from '$lib/types';

	const personas: Persona[] = ['educator', 'developer', 'policymaker'];

	const personaImages: Record<Persona, string> = {
		educator: '/educator.jpg',
		developer: '/developer.jpg',
		policymaker: '/policy_maker.jpg'
	};

	function selectPersona(persona: Persona) {
		goto(`/compare?persona=${persona}`);
	}
</script>

<svelte:head>
	<title>Micro Evals - AI Model Comparison for Education</title>
</svelte:head>

<!-- Hero Section with Background Image -->
<section class="relative min-h-[600px] flex items-center justify-center overflow-hidden">
	<!-- Background Image -->
	<div
		class="absolute inset-0 bg-cover bg-center bg-no-repeat"
		style="background-image: url('/hero-bg.jpg');"
	></div>

	<!-- Gradient Overlay -->
	<div
		class="absolute inset-0"
		style="background: linear-gradient(244deg, rgba(33, 21, 1, 0.85) 8%, rgba(34, 21, 1, 0.4) 28%, rgba(33, 21, 1, 0.75) 74%);"
	></div>

	<!-- Navigation -->
	<nav class="absolute top-0 left-0 right-0 px-6 py-4 z-10">
		<div class="max-w-7xl mx-auto flex items-center justify-between">
			<a href="https://fab-ai.org" class="hover:opacity-80 transition-opacity">
				<img src="/Fab-AI-logo-white-transparent.svg" alt="Fab AI" class="h-8" />
			</a>
			<div class="flex items-center gap-6">
				<a href="/compare" class="text-white/80 hover:text-white transition-colors font-medium">
					Compare
				</a>
				<a href="/leaderboard" class="text-white/80 hover:text-white transition-colors font-medium">
					Leaderboard
				</a>
			</div>
		</div>
	</nav>

	<!-- Hero Content -->
	<div class="relative z-10 text-center px-4 max-w-4xl mx-auto">
		<h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6">
			Compare AI Model Responses
		</h1>
		<p class="text-xl md:text-2xl text-white/80 max-w-2xl mx-auto">
			See how the latest AI models handle real educational tasks. Choose your role to explore relevant scenarios.
		</p>
	</div>
</section>

<!-- Main Content -->
<main class="max-w-6xl mx-auto px-4 py-16">
	<!-- Persona Cards -->
	<div class="grid md:grid-cols-3 gap-6">
		{#each personas as persona}
			<button
				onclick={() => selectPersona(persona)}
				class="group bg-white rounded-xl p-8 text-left shadow-sm border border-gray-200 hover:shadow-lg hover:border-primary transition-all"
			>
				<div class="w-16 h-16 mb-4 rounded-full overflow-hidden">
					<img
						src={personaImages[persona]}
						alt={PERSONA_INFO[persona].label}
						class="w-full h-full object-cover"
					/>
				</div>
				<h2 class="text-2xl font-semibold text-dark mb-2 group-hover:text-primary transition-colors">
					{PERSONA_INFO[persona].label}
				</h2>
				<p class="text-muted">
					{PERSONA_INFO[persona].description}
				</p>
				<div class="mt-6 flex items-center text-primary font-medium">
					Explore tasks
					<svg class="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
					</svg>
				</div>
			</button>
		{/each}
	</div>

	<!-- Info Section -->
	<div class="mt-16 text-center">
		<h3 class="text-lg font-semibold text-dark mb-4">How it works</h3>
		<div class="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
			<div class="text-center">
				<div class="w-12 h-12 bg-primary-light rounded-full flex items-center justify-center mx-auto mb-3">
					<span class="text-xl text-primary-dark">1</span>
				</div>
				<p class="text-muted">Choose your role to see relevant tasks</p>
			</div>
			<div class="text-center">
				<div class="w-12 h-12 bg-primary-light rounded-full flex items-center justify-center mx-auto mb-3">
					<span class="text-xl text-primary-dark">2</span>
				</div>
				<p class="text-muted">Select a task from the sidebar</p>
			</div>
			<div class="text-center">
				<div class="w-12 h-12 bg-primary-light rounded-full flex items-center justify-center mx-auto mb-3">
					<span class="text-xl text-primary-dark">3</span>
				</div>
				<p class="text-muted">Compare responses from three AI models</p>
			</div>
		</div>
	</div>
</main>

<!-- Footer -->
<footer class="border-t border-gray-200 py-8">
	<div class="max-w-6xl mx-auto px-4 text-center text-muted text-sm">
		<p>Pre-computed responses for reliable, fast comparisons. No live API calls.</p>
	</div>
</footer>
