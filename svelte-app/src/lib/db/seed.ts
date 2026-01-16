import 'dotenv/config';
import { drizzle } from 'drizzle-orm/node-postgres';
import pg from 'pg';
import { tasks, responses, leaderboard, votes } from './schema';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const pool = new pg.Pool({
	connectionString: process.env.DATABASE_URL
});

const db = drizzle(pool);

async function seed() {
	console.log('Seeding database from data.json...');

	try {
		// Read data.json - path is relative to this script
		const dataPath = path.resolve(__dirname, '../../../../docs/data.json');
		const rawData = fs.readFileSync(dataPath, 'utf8');
		const jsonData = JSON.parse(rawData);

		// Collect all unique model keys from all tasks
		const allModelKeys = new Set<string>();
		for (const taskData of jsonData) {
			if (taskData.responses) {
				Object.keys(taskData.responses).forEach((key) => allModelKeys.add(key));
			}
		}
		const models = Array.from(allModelKeys);
		console.log(`Found ${models.length} models: ${models.join(', ')}`);

		// Clear existing data (order matters due to foreign keys)
		// Delete in reverse order of dependencies: votes -> responses -> tasks
		await db.delete(votes);
		await db.delete(responses);
		await db.delete(leaderboard);
		await db.delete(tasks);

		// Insert tasks
		for (const taskData of jsonData) {
			await db.insert(tasks).values({
				id: taskData.id,
				title: taskData.title,
				description: taskData.prompt, // Mapping 'prompt' from JSON to 'description' in DB
				persona: taskData.persona
			});
			console.log(`Inserted task: ${taskData.title}`);

			// Insert responses for ALL models found in this task's responses
			if (taskData.responses) {
				for (const modelKey of Object.keys(taskData.responses)) {
					const content = taskData.responses[modelKey];
					await db.insert(responses).values({
						taskId: taskData.id,
						modelKey,
						content,
						eloRating: 1000,
						totalComparisons: 0
					});
				}
			}
		}

		// Initialize leaderboard for all models
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
	} catch (error) {
		console.error('Error during seeding:', error);
	} finally {
		await pool.end();
	}
}

seed().catch(console.error);
