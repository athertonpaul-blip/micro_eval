<script lang="ts">
	import { goto } from '$app/navigation';
	import Navbar from '$lib/components/Navbar.svelte';
	import type { Persona } from '$lib/types';
	import { PERSONA_INFO } from '$lib/types';

	const personas: Persona[] = ['educator', 'developer', 'policymaker'];

	function selectPersona(persona: Persona) {
		goto(`/compare?persona=${persona}`);
	}
</script>

<svelte:head>
	<title>Micro Evals - AI Model Comparison for Education</title>
</svelte:head>

<Navbar />

<main class="max-w-6xl mx-auto px-4 py-16">
	<!-- Hero Section -->
	<div class="text-center mb-16">
		<h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
			Compare AI Model Responses
		</h1>
		<p class="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
			See how latest AI models handle real educational tasks. Choose your role to explore
			relevant scenarios.
		</p>
		<div class="flex items-center justify-center gap-4 text-sm text-gray-500">
			<span class="flex items-center gap-1">
				<span class="w-2 h-2 rounded-full bg-green-500"></span>
				GPT-4o
			</span>
			<span class="flex items-center gap-1">
				<span class="w-2 h-2 rounded-full bg-purple-500"></span>
				Claude 3.5 Sonnet
			</span>
			<span class="flex items-center gap-1">
				<span class="w-2 h-2 rounded-full bg-orange-500"></span>
				Gemini 1.5 Pro
			</span>
		</div>
	</div>

	<!-- Persona Cards -->
	<div class="grid md:grid-cols-3 gap-6">
		{#each personas as persona}
			<button
				onclick={() => selectPersona(persona)}
				class="group bg-white rounded-xl p-8 text-left shadow-sm border border-gray-200 hover:shadow-lg hover:border-gray-300 transition-all"
			>
				<div class="text-5xl mb-4">{PERSONA_INFO[persona].icon}</div>
				<h2 class="text-2xl font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
					{PERSONA_INFO[persona].label}
				</h2>
				<p class="text-gray-600">
					{PERSONA_INFO[persona].description}
				</p>
				<div class="mt-6 flex items-center text-blue-600 font-medium">
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
		<h3 class="text-lg font-semibold text-gray-900 mb-4">How it works</h3>
		<div class="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
			<div class="text-center">
				<div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
					<span class="text-xl">1</span>
				</div>
				<p class="text-gray-600">Choose your role to see relevant tasks</p>
			</div>
			<div class="text-center">
				<div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
					<span class="text-xl">2</span>
				</div>
				<p class="text-gray-600">Select a task from the sidebar</p>
			</div>
			<div class="text-center">
				<div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
					<span class="text-xl">3</span>
				</div>
				<p class="text-gray-600">Compare responses from three AI models</p>
			</div>
		</div>
	</div>
</main>

<!-- Footer -->
<footer class="border-t border-gray-200 mt-16 py-8">
	<div class="max-w-6xl mx-auto px-4 text-center text-gray-500 text-sm">
		<p>Pre-computed responses for reliable, fast comparisons. No live API calls.</p>
	</div>
</footer>
