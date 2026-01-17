import { db, tasks, responses } from '$lib/db';
import { eq } from 'drizzle-orm';
import type { Task, EducatorTasksData } from '$lib/types';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

// Load educator tasks from JSON file
export function getEducatorTasks(): EducatorTasksData | null {
	try {
		// Try multiple paths for the JSON file
		const possiblePaths = [
			join(process.cwd(), 'static', 'data', 'educator_tasks.json'),
			join(process.cwd(), 'svelte-app', 'static', 'data', 'educator_tasks.json'),
			join(process.cwd(), '..', 'generator', 'educator_tasks.json'),
		];

		for (const filePath of possiblePaths) {
			if (existsSync(filePath)) {
				const content = readFileSync(filePath, 'utf-8');
				return JSON.parse(content) as EducatorTasksData;
			}
		}

		console.warn('educator_tasks.json not found in any expected location');
		return null;
	} catch (err) {
		console.error('Failed to load educator tasks:', err);
		return null;
	}
}

export async function getAllTasks(): Promise<Task[]> {
	if (!process.env.DATABASE_URL) {
		console.error('DATABASE_URL is not set');
		throw new Error('Database connection not configured');
	}

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
			responses: responseMap // Include all available models dynamically
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
		responses: responseMap // Include all available models dynamically
	};
}
