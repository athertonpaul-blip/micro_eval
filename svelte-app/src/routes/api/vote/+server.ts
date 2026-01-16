import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { db, responses, votes, leaderboard } from '$lib/db';
import { calculateElo } from '$lib/db/elo';
import { eq, and, sql } from 'drizzle-orm';

export const POST: RequestHandler = async ({ request, cookies }) => {
	try {
		const body = await request.json();
		const { taskId, winner, loser } = body;

		// Validate input
		if (!taskId || !winner || !loser) {
			throw error(400, 'Missing required fields: taskId, winner, loser');
		}

		if (winner === loser) {
			throw error(400, 'Winner and loser cannot be the same');
		}

		// Model keys are validated by checking they exist in the responses table

		// Get or create session ID for anonymous tracking
		let sessionId = cookies.get('session_id');
		if (!sessionId) {
			sessionId = crypto.randomUUID();
			cookies.set('session_id', sessionId, {
				path: '/',
				httpOnly: true,
				sameSite: 'strict',
				maxAge: 60 * 60 * 24 * 365 // 1 year
			});
		}

		// Get current Elo ratings for both models on this task
		const [winnerResponse] = await db
			.select()
			.from(responses)
			.where(and(eq(responses.taskId, taskId), eq(responses.modelKey, winner)));

		const [loserResponse] = await db
			.select()
			.from(responses)
			.where(and(eq(responses.taskId, taskId), eq(responses.modelKey, loser)));

		if (!winnerResponse || !loserResponse) {
			throw error(404, 'Responses not found for the given task and models');
		}

		// Calculate new Elo ratings
		const { newWinnerRating, newLoserRating, winnerGain, loserLoss } = calculateElo(
			winnerResponse.eloRating,
			loserResponse.eloRating
		);

		// Update responses table with new ratings
		await db
			.update(responses)
			.set({
				eloRating: newWinnerRating,
				totalComparisons: sql`${responses.totalComparisons} + 1`
			})
			.where(eq(responses.id, winnerResponse.id));

		await db
			.update(responses)
			.set({
				eloRating: newLoserRating,
				totalComparisons: sql`${responses.totalComparisons} + 1`
			})
			.where(eq(responses.id, loserResponse.id));

		// Record the vote
		await db.insert(votes).values({
			taskId,
			winnerModel: winner,
			loserModel: loser,
			sessionId
		});

		// Update leaderboard aggregates
		await db
			.update(leaderboard)
			.set({
				wins: sql`${leaderboard.wins} + 1`,
				totalComparisons: sql`${leaderboard.totalComparisons} + 1`,
				updatedAt: new Date()
			})
			.where(eq(leaderboard.modelKey, winner));

		await db
			.update(leaderboard)
			.set({
				losses: sql`${leaderboard.losses} + 1`,
				totalComparisons: sql`${leaderboard.totalComparisons} + 1`,
				updatedAt: new Date()
			})
			.where(eq(leaderboard.modelKey, loser));

		// Recalculate average Elo for leaderboard
		// (average of all task-specific Elo ratings for this model)
		for (const modelKey of [winner, loser]) {
			const avgResult = await db
				.select({
					avgElo: sql<number>`AVG(${responses.eloRating})`
				})
				.from(responses)
				.where(eq(responses.modelKey, modelKey));

			if (avgResult[0]?.avgElo) {
				await db
					.update(leaderboard)
					.set({
						totalElo: avgResult[0].avgElo.toString()
					})
					.where(eq(leaderboard.modelKey, modelKey));
			}
		}

		return json({
			success: true,
			winner: {
				model: winner,
				newRating: newWinnerRating,
				change: `+${winnerGain}`
			},
			loser: {
				model: loser,
				newRating: newLoserRating,
				change: `-${loserLoss}`
			}
		});
	} catch (err) {
		console.error('Vote error:', err);
		if (err && typeof err === 'object' && 'status' in err) {
			throw err;
		}
		throw error(500, 'Failed to record vote');
	}
};
