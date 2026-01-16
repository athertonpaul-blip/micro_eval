import { db, tasks, responses } from '$lib/db';
import { eq } from 'drizzle-orm';
import type { Task } from '$lib/types';

export async function getAllTasks(): Promise<Task[]> {
	const allTasks = await db.select().from(tasks);

	const tasksWithResponses: Task[] = [];

	for (const task of allTasks) {
		const taskResponses = await db
			.select()
			.from(responses)
			.where(eq(responses.taskId, task.id));

		const responseMap: Record<string, string> = {};
		for (const r of taskResponses) {
			responseMap[r.modelKey] = r.content;
		}

		tasksWithResponses.push({
			id: task.id,
			title: task.title,
			description: task.description,
			persona: task.persona as Task['persona'],
			responses: {
				gpt4o: responseMap['gpt4o'] || '',
				claude: responseMap['claude'] || '',
				gemini: responseMap['gemini'] || ''
			}
		});
	}

	return tasksWithResponses;
}

export async function getTaskById(id: string): Promise<Task | null> {
	const [task] = await db.select().from(tasks).where(eq(tasks.id, id));

	if (!task) return null;

	const taskResponses = await db
		.select()
		.from(responses)
		.where(eq(responses.taskId, id));

	const responseMap: Record<string, string> = {};
	for (const r of taskResponses) {
		responseMap[r.modelKey] = r.content;
	}

	return {
		id: task.id,
		title: task.title,
		description: task.description,
		persona: task.persona as Task['persona'],
		responses: {
			gpt4o: responseMap['gpt4o'] || '',
			claude: responseMap['claude'] || '',
			gemini: responseMap['gemini'] || ''
		}
	};
}
