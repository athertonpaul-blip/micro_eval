export type Persona = 'educator' | 'student' | 'admin';

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

export interface ModelResponse {
	modelKey: string;
	content: string;
	eloRating: number;
}
