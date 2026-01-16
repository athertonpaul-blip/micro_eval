# Micro Evals - SvelteKit Edition

A modern SvelteKit application for comparing AI model responses on educational micro-tasks, with Elo-based voting and leaderboards.

## Tech Stack

- **Framework**: SvelteKit 2 with Svelte 5
- **Database**: PostgreSQL with Drizzle ORM
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **Markdown**: Marked.js
- **Deployment**: Digital Ocean Droplet with Caddy & PM2

## Features

- **Persona-based filtering**: Tasks organized by Educator, Developer, Policymaker
- **Side-by-side comparison**: View GPT-4o, Claude, and Gemini responses
- **Elo-based voting**: Head-to-head comparisons that affect model rankings
- **Leaderboard**: Global and per-task model rankings
- **Markdown rendering**: Rich text formatting for AI responses
- **Responsive design**: Works on desktop and mobile

## Getting Started

### Prerequisites

- Node.js 20+
- PostgreSQL 15+

### Local Development

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your database URL

# Push database schema
npm run db:push

# Seed the database with tasks
npm run db:seed

# Start development server
npm run dev
```

### Database Commands

```bash
npm run db:generate  # Generate migrations from schema changes
npm run db:migrate   # Run migrations
npm run db:push      # Push schema directly (dev)
npm run db:studio    # Open Drizzle Studio GUI
npm run db:seed      # Seed tasks from JSON
```

## Project Structure

```
src/
├── lib/
│   ├── components/       # Svelte components
│   │   ├── Navbar.svelte
│   │   ├── TaskSidebar.svelte
│   │   ├── ResponseCard.svelte
│   │   ├── ResponseArena.svelte
│   │   └── VotingUI.svelte
│   ├── db/              # Database layer
│   │   ├── schema.ts    # Drizzle schema
│   │   ├── index.ts     # DB connection
│   │   ├── elo.ts       # Elo calculations
│   │   └── seed.ts      # Seed script
│   ├── data/            # Data access layer
│   │   ├── index.ts     # Query functions
│   │   └── tasks.json   # Fallback data
│   ├── utils/
│   │   └── markdown.ts
│   └── types.ts
├── routes/
│   ├── +layout.svelte
│   ├── +page.svelte           # Landing page
│   ├── compare/
│   │   ├── +page.server.ts
│   │   └── +page.svelte       # Compare/Vote interface
│   ├── leaderboard/
│   │   ├── +page.server.ts
│   │   └── +page.svelte       # Model rankings
│   └── api/
│       ├── vote/+server.ts    # POST /api/vote
│       └── leaderboard/+server.ts
└── app.css
```

## Database Schema

```sql
-- Tasks with prompts
tasks (id, persona, title, prompt, created_at)

-- Model responses with Elo ratings
responses (id, task_id, model_key, content, elo_rating, total_comparisons)

-- Individual votes
votes (id, task_id, winner_model, loser_model, session_id, created_at)

-- Aggregated leaderboard
leaderboard (model_key, total_elo, wins, losses, total_comparisons)
```

## API Endpoints

### POST /api/vote
Record a vote for head-to-head comparison.

```json
{
  "taskId": "edu_01",
  "winner": "claude",
  "loser": "gpt4o"
}
```

### GET /api/leaderboard
Get model rankings.

```
GET /api/leaderboard
GET /api/leaderboard?persona=educator
```

## Deployment to Digital Ocean

### 1. Initial Droplet Setup

```bash
# On fresh Ubuntu 22.04 droplet, run:
chmod +x setup-droplet.sh
./setup-droplet.sh
```

### 2. Clone and Configure

```bash
cd /opt/microevals
git clone https://github.com/YOUR_USERNAME/micro-evals.git .
cd svelte-app

# Edit environment
nano .env  # Add DATABASE_URL

# Install and build
npm install
npm run db:push
npm run db:seed
npm run build
```

### 3. Configure Caddy (HTTPS)

Edit `/etc/caddy/Caddyfile`:

```
yourdomain.com {
    reverse_proxy localhost:3000
}
```

Then: `systemctl restart caddy`

### 4. Start with PM2

```bash
pm2 start ecosystem.config.cjs --env production
pm2 save
pm2 startup
```

### 5. Deploy Updates

```bash
./deploy.sh
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `NODE_ENV` | `development` or `production` |
| `PORT` | Server port (default: 3000) |

## Elo Rating System

The app uses standard chess Elo with K-factor of 32:

- Starting rating: 1500
- Ratings updated after each vote
- Beating higher-rated models = more points
- Global Elo = average of task-specific Elos
