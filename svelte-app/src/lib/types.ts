export type Persona = 'educator' | 'developer' | 'policymaker';

export interface Task {
	id: string;
	title: string;
	description: string;
	persona: Persona;
	responses?: {
		gpt4o: string;
		claude: string;
		gemini: string;
	};
}

export interface TaskWithResponses extends Task {
	responses: Record<string, string>; // Allow any model keys from data.json
}

export interface ModelResponse {
	modelKey: string;
	content: string;
	eloRating: number;
}

export const PERSONA_INFO: Record<Persona, { icon: string; label: string; description: string }> = {
	educator: {
		icon: '👩‍🏫',
		label: 'Educator',
		description: 'Tasks for teachers, curriculum designers, and education professionals'
	},
	developer: {
		icon: '💻',
		label: 'Developer',
		description: 'Technical tasks for software engineers and developers'
	},
	policymaker: {
		icon: '🏛️',
		label: 'Policymaker',
		description: 'Policy and governance tasks for administrators and decision-makers'
	}
};

export const MODELS = [
	{
		key: 'gpt4o',
		name: 'GPT-4o',
		color: '#10b981' // green-500
	},
	{
		key: 'claude',
		name: 'Claude 3.5 Sonnet',
		color: '#a855f7' // purple-500
	},
	{
		key: 'gemini',
		name: 'Gemini 1.5 Pro',
		color: '#f97316' // orange-500
	}
];
