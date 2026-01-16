require('dotenv').config();

module.exports = {
	apps: [
		{
			name: 'micro-evals',
			script: 'build/index.js',
			cwd: __dirname,
			instances: 1,
			autorestart: true,
			watch: false,
			max_memory_restart: '500M',
			env: {
				NODE_ENV: 'production',
				PORT: 3000,
				DATABASE_URL: process.env.DATABASE_URL
			},
			env_production: {
				NODE_ENV: 'production',
				PORT: 3000,
				DATABASE_URL: process.env.DATABASE_URL
			}
		}
	]
};
