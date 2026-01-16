import type { PageServerLoad } from './$types';
import { getAllTasks } from '$lib/data';
import type { Persona } from '$lib/types';

export const load: PageServerLoad = async ({ url }) => {
	const persona = (url.searchParams.get('persona') as Persona) || 'educator';
	const tasks = await getAllTasks();

	return {
		tasks,
		initialPersona: persona
	};
};
