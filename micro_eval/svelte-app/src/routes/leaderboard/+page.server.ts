import type { PageServerLoad } from './$types';
import { db, leaderboard, responses, tasks } from '$lib/db';
import { eq, desc, sql } from 'drizzle-orm';

export const load: PageServerLoad = async ({ url }) => {
	const persona = url.searchParams.get('persona');

	try {
		// Get global leaderboard
		const globalRankings = await db
			.select()
			.from(leaderboard)
			.orderBy(desc(sql`CAST(${leaderboard.totalElo} AS NUMERIC)`));

		// Transform to frontend format
		const rankings = globalRankings.map((entry, index) => {
			const total = entry.wins + entry.losses;
			const winRate = total > 0 ? ((entry.wins / total) * 100).toFixed(1) : '0.0';

			return {
				rank: index + 1,
				modelKey: entry.modelKey,
				elo: Math.round(parseFloat(entry.totalElo)),
				wins: entry.wins,
				losses: entry.losses,
				totalComparisons: entry.totalComparisons,
				winRate
			};
		});

		// Get per-task breakdown if persona specified
		let taskBreakdown: Array<{
			taskId: string;
			taskTitle: string;
			rankings: Array<{
				modelKey: string;
				eloRating: number;
				comparisons: number;
			}>;
		}> = [];

		if (persona) {
			const personaTasks = await db.select().from(tasks).where(eq(tasks.persona, persona));

			for (const task of personaTasks) {
				const taskResponses = await db
					.select()
					.from(responses)
					.where(eq(responses.taskId, task.id))
					.orderBy(desc(responses.eloRating));

				taskBreakdown.push({
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

		return {
			rankings,
			taskBreakdown,
			selectedPersona: persona
		};
	} catch (error) {
		console.error('Failed to load leaderboard:', error);
		// Return empty data if DB not available
		return {
			rankings: [],
			taskBreakdown: [],
			selectedPersona: persona
		};
	}
};
