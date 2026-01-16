/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				// Model colors
				gpt: {
					light: '#dcfce7',
					DEFAULT: '#22c55e',
					dark: '#16a34a'
				},
				claude: {
					light: '#f3e8ff',
					DEFAULT: '#a855f7',
					dark: '#9333ea'
				},
				gemini: {
					light: '#ffedd5',
					DEFAULT: '#f97316',
					dark: '#ea580c'
				}
			}
		}
	},
	plugins: [
		require('@tailwindcss/typography')
	]
};
