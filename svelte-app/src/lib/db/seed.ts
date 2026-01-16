import 'dotenv/config';
import { drizzle } from 'drizzle-orm/node-postgres';
import pg from 'pg';
import { tasks, responses, leaderboard } from './schema';

const pool = new pg.Pool({
	connectionString: process.env.DATABASE_URL
});

const db = drizzle(pool);

const sampleTasks = [
	{
		id: 'task-1',
		title: 'Explain photosynthesis to a 5th grader',
		description: 'Create an age-appropriate explanation of photosynthesis for elementary school students.',
		persona: 'educator'
	},
	{
		id: 'task-2',
		title: 'Write a quiz on the American Revolution',
		description: 'Generate a 10-question multiple choice quiz about the American Revolution for high school students.',
		persona: 'educator'
	},
	{
		id: 'task-3',
		title: 'Help me understand quadratic equations',
		description: 'Explain how to solve quadratic equations step by step.',
		persona: 'student'
	}
];

const models = ['gpt4o', 'claude', 'gemini'];

async function seed() {
	console.log('Seeding database...');

	// Clear existing data
	await db.delete(responses);
	await db.delete(leaderboard);
	await db.delete(tasks);

	// Insert tasks
	for (const task of sampleTasks) {
		await db.insert(tasks).values(task);
		console.log(`Inserted task: ${task.title}`);

		// Insert placeholder responses for each model
		for (const modelKey of models) {
			await db.insert(responses).values({
				taskId: task.id,
				modelKey,
				content: `Sample response from ${modelKey} for "${task.title}"`,
				eloRating: 1000,
				totalComparisons: 0
			});
		}
	}

	// Initialize leaderboard
	for (const modelKey of models) {
		await db.insert(leaderboard).values({
			modelKey,
			totalElo: '1000',
			wins: 0,
			losses: 0,
			totalComparisons: 0
		});
		console.log(`Initialized leaderboard for: ${modelKey}`);
	}

	console.log('Seeding complete!');
	await pool.end();
}

seed().catch(console.error);
