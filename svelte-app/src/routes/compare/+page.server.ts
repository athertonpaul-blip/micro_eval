import type { PageServerLoad } from './$types';
import { getAllTasks, getEducatorTasks } from '$lib/data';
import type { Persona } from '$lib/types';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ url }) => {
	const persona = (url.searchParams.get('persona') as Persona) || 'educator';

	// Load educator hierarchy data
	const educatorData = getEducatorTasks();

	try {
		const tasks = await getAllTasks();
		return {
			tasks,
			initialPersona: persona,
			educatorHierarchy: educatorData?.hierarchy ?? [],
			educatorFlatTasks: educatorData?.flatTasks ?? []
		};
	} catch (err) {
		console.error('Failed to load tasks:', err);
		// Return empty tasks array instead of crashing
		// This allows the page to load even if DB is not set up
		return {
			tasks: [],
			initialPersona: persona,
			educatorHierarchy: educatorData?.hierarchy ?? [],
			educatorFlatTasks: educatorData?.flatTasks ?? []
		};
	}
};
