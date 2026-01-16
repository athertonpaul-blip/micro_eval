import { pgTable, text, integer, timestamp, uuid, real } from 'drizzle-orm/pg-core';

export const tasks = pgTable('tasks', {
	id: text('id').primaryKey(),
	title: text('title').notNull(),
	description: text('description').notNull(),
	persona: text('persona').notNull(),
	createdAt: timestamp('created_at').defaultNow().notNull()
});

export const responses = pgTable('responses', {
	id: uuid('id').defaultRandom().primaryKey(),
	taskId: text('task_id').notNull().references(() => tasks.id),
	modelKey: text('model_key').notNull(),
	content: text('content').notNull(),
	eloRating: real('elo_rating').default(1000).notNull(),
	totalComparisons: integer('total_comparisons').default(0).notNull(),
	createdAt: timestamp('created_at').defaultNow().notNull()
});

export const votes = pgTable('votes', {
	id: uuid('id').defaultRandom().primaryKey(),
	taskId: text('task_id').notNull().references(() => tasks.id),
	winnerModel: text('winner_model').notNull(),
	loserModel: text('loser_model').notNull(),
	sessionId: text('session_id').notNull(),
	createdAt: timestamp('created_at').defaultNow().notNull()
});

export const leaderboard = pgTable('leaderboard', {
	modelKey: text('model_key').primaryKey(),
	totalElo: text('total_elo').default('1000').notNull(),
	wins: integer('wins').default(0).notNull(),
	losses: integer('losses').default(0).notNull(),
	totalComparisons: integer('total_comparisons').default(0).notNull(),
	updatedAt: timestamp('updated_at').defaultNow().notNull()
});
