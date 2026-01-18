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
			// When running from svelte-app directory
			join(process.cwd(), 'static', 'data', 'educator_tasks.json'),
			// When running from project root
			join(process.cwd(), 'svelte-app', 'static', 'data', 'educator_tasks.json'),
			// Relative to generator
			join(process.cwd(), '..', 'generator', 'educator_tasks_filled.json'),
			join(process.cwd(), 'generator', 'educator_tasks_filled.json'),
			// Build output paths
			join(process.cwd(), 'build', 'client', 'data', 'educator_tasks.json'),
			join(process.cwd(), '.svelte-kit', 'output', 'client', 'data', 'educator_tasks.json'),
		];

		console.log('Looking for educator_tasks.json, cwd:', process.cwd());

		for (const filePath of possiblePaths) {
			if (existsSync(filePath)) {
				console.log('Found educator_tasks.json at:', filePath);
				const content = readFileSync(filePath, 'utf-8');
				return JSON.parse(content) as EducatorTasksData;
			}
		}

		console.warn('educator_tasks.json not found. Tried paths:', possiblePaths);
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

	// Fetch all tasks and all responses in parallel (2 queries instead of N+1)
	const [allTasks, allResponses] = await Promise.all([
		db.select().from(tasks),
		db.select().from(responses)
	]);

	// Group responses by taskId in memory
	const responsesByTaskId = new Map<string, Record<string, string>>();
	for (const r of allResponses) {
		if (!responsesByTaskId.has(r.taskId)) {
			responsesByTaskId.set(r.taskId, {});
		}
		responsesByTaskId.get(r.taskId)![r.modelKey] = r.content;
	}

	// Build tasks with their responses
	return allTasks.map((task) => ({
		id: task.id,
		title: task.title,
		description: task.description,
		persona: task.persona as Task['persona'],
		responses: responsesByTaskId.get(task.id) ?? {}
	}));
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
