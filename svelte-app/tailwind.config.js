/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				// Brand colors from Figma design
				primary: {
					light: '#F5DCC4',
					DEFAULT: '#DE8430',
					dark: '#B86A20'
				},
				dark: {
					DEFAULT: '#191919',
					light: '#2D2D2D'
				},
				muted: {
					DEFAULT: '#707070',
					light: '#9A9A9A'
				},
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
			},
			fontFamily: {
				sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif']
			}
		}
	},
	plugins: [
		require('@tailwindcss/typography')
	]
};
