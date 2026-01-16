import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { db, leaderboard, responses, tasks } from '$lib/db';
import { eq, desc, sql } from 'drizzle-orm';

export const GET: RequestHandler = async ({ url }) => {
	try {
		const persona = url.searchParams.get('persona');

		// Get global leaderboard
		const globalRankings = await db
			.select()
			.from(leaderboard)
			.orderBy(desc(sql`CAST(${leaderboard.totalElo} AS NUMERIC)`));

		// Get per-task rankings if persona is specified
		let taskRankings: Array<{
			taskId: string;
			taskTitle: string;
			rankings: Array<{
				modelKey: string;
				eloRating: number;
				comparisons: number;
			}>;
		}> = [];

		if (persona) {
			// Get tasks for this persona
			const personaTasks = await db.select().from(tasks).where(eq(tasks.persona, persona));

			for (const task of personaTasks) {
				const taskResponses = await db
					.select()
					.from(responses)
					.where(eq(responses.taskId, task.id))
					.orderBy(desc(responses.eloRating));

				taskRankings.push({
					taskId: task.id,
					taskTitle: task.title,
					rankings: taskResponses.map((r) => ({
						modelKey: r.modelKey,
						eloRating: r.eloRating,
						comparisons: r.totalComparisons
					}))
				});
			}
		}

		// Calculate win rates
		const rankings = globalRankings.map((entry) => {
			const total = entry.wins + entry.losses;
			const winRate = total > 0 ? ((entry.wins / total) * 100).toFixed(1) : '0.0';

			return {
				modelKey: entry.modelKey,
				elo: parseFloat(entry.totalElo),
				wins: entry.wins,
				losses: entry.losses,
				totalComparisons: entry.totalComparisons,
				winRate: `${winRate}%`
			};
		});

		return json({
			global: rankings,
			byTask: taskRankings,
			lastUpdated: new Date().toISOString()
		});
	} catch (err) {
		console.error('Leaderboard error:', err);
		throw error(500, 'Failed to fetch leaderboard');
	}
};
