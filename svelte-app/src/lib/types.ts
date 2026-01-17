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

// Hierarchical educator task structure
export interface EducatorTask {
	id: string;
	domain: string;
	category: string;
	useCase: string;
	title: string;
	prompt: string;
	teacherInputs: string;
	modelDoes: string;
	persona: 'educator';
	responses?: Record<string, string>;
}

export interface UseCase {
	id: string;
	name: string;
	tasks: EducatorTask[];
}

export interface Category {
	id: string;
	name: string;
	useCases: UseCase[];
}

export interface Domain {
	id: string;
	name: string;
	categories: Category[];
}

export interface EducatorTasksData {
	hierarchy: Domain[];
	flatTasks: EducatorTask[];
}

export interface ModelResponse {
	modelKey: string;
	content: string;
	eloRating: number;
}

export const PERSONA_INFO: Record<Persona, { icon: string; image: string; label: string; description: string }> = {
	educator: {
		icon: '👩‍🏫',
		image: '/educator.jpg',
		label: 'Educator',
		description: 'Tasks for teachers, curriculum designers, and education professionals'
	},
	developer: {
		icon: '💻',
		image: '/developer.jpg',
		label: 'Developer',
		description: 'Technical tasks for software engineers and developers'
	},
	policymaker: {
		icon: '🏛️',
		image: '/policy_maker.jpg',
		label: 'Policymaker',
		description: 'Policy and governance tasks for administrators and decision-makers'
	}
};

export const MODELS = [
	// GPT models (newest first)
	{
		key: 'gpt5.2-medium',
		name: 'GPT-5.2 Medium',
		color: '#10b981' // green-500
	},
	{
		key: 'gpt5.2-low',
		name: 'GPT-5.2 Low',
		color: '#34d399' // green-400
	},
	{
		key: 'gpt5-mini',
		name: 'GPT-5 Mini',
		color: '#6ee7b7' // green-300
	},
	{
		key: 'gpt4o',
		name: 'GPT-4o',
		color: '#059669' // green-600
	},
	// Claude models
	{
		key: 'claude-opus',
		name: 'Claude Opus',
		color: '#a855f7' // purple-500
	},
	{
		key: 'claude',
		name: 'Claude 3.5 Sonnet',
		color: '#c084fc' // purple-400
	},
	// Gemini models
	{
		key: 'gemini-pro',
		name: 'Gemini 3.0 Pro',
		color: '#f97316' // orange-500
	},
	{
		key: 'gemini',
		name: 'Gemini 3.0 Flash',
		color: '#fb923c' // orange-400
	},
	// Open models
	{
		key: 'gemma-3-4b',
		name: 'Gemma 3 4B',
		color: '#3b82f6' // blue-500
	}
];
