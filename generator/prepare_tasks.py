#!/usr/bin/env python3
"""
Prepare micro-tasks for generation:
1. Fill in placeholders with realistic K-12 values
2. Recategorize admin tasks as policymaker
3. Output in format compatible with generate.py
"""

import json
import re
import random
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR / "educator_tasks.json"
OUTPUT_FILE = SCRIPT_DIR / "tasks.json"
HIERARCHY_OUTPUT = SCRIPT_DIR / "educator_tasks_filled.json"
STATIC_OUTPUT = SCRIPT_DIR.parent / "svelte-app" / "static" / "data" / "educator_tasks.json"

# Realistic values for placeholders - varied for good coverage
PLACEHOLDER_VALUES = {
    # Grade levels - mix across K-12
    'LEVEL': [
        'Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5',
        'Grade 6', 'Grade 7', 'Grade 8', 'Grade 9', 'Grade 10',
        'Grade 11', 'Grade 12', 'Kindergarten', 'Pre-K'
    ],
    'GRADE': [
        'Grade 3', 'Grade 5', 'Grade 7', 'Grade 9', 'Grade 11'
    ],
    'AGE': ['5-6', '7-8', '9-10', '11-12', '13-14', '15-16', '17-18'],

    # Topics - diverse across subjects
    'TOPIC': [
        'photosynthesis', 'fractions', 'the water cycle', 'World War II',
        'basic algebra', 'cellular respiration', 'the solar system',
        'punctuation and grammar', 'chemical reactions', 'ecosystems',
        'decimals and percentages', 'ancient civilizations', 'electricity',
        'creative writing', 'the human digestive system', 'geometry basics',
        'climate change', 'reading comprehension strategies', 'multiplication tables',
        'the American Revolution', 'plant life cycles', 'probability',
        'poetry analysis', 'forces and motion', 'map reading skills'
    ],
    'TOPICS': [
        'fractions, decimals, and percentages',
        'plant biology and ecosystems',
        'grammar, punctuation, and sentence structure',
        'ancient Egypt, Greece, and Rome'
    ],

    # Subjects
    'SUBJECT': [
        'Mathematics', 'Science', 'English Language Arts', 'Social Studies',
        'History', 'Biology', 'Physics', 'Chemistry', 'Geography',
        'Art', 'Music', 'Physical Education'
    ],
    'SUBJECTS': [
        'Mathematics and Science',
        'English and Social Studies',
        'Art and Music'
    ],

    # Concepts and skills
    'CONCEPT': [
        'equivalent fractions', 'photosynthesis', 'main idea and details',
        'cause and effect', 'the scientific method', 'place value',
        'character development', 'food chains', 'paragraph structure'
    ],
    'SKILL': [
        'critical thinking', 'problem-solving', 'reading fluency',
        'written expression', 'mathematical reasoning', 'scientific inquiry',
        'collaboration', 'time management', 'note-taking'
    ],
    'FOCUS': [
        'comprehension', 'accuracy', 'fluency', 'vocabulary development',
        'critical analysis', 'application', 'synthesis', 'evaluation'
    ],

    # Languages
    'LANGUAGE': [
        'English', 'Spanish', 'French', 'Mandarin', 'Hindi',
        'Arabic', 'Swahili', 'Portuguese'
    ],
    'LANG A': ['English', 'Spanish', 'French'],
    'LANG B': ['Spanish', 'French', 'Mandarin'],
    'TARGET LANGUAGE': ['Spanish', 'French', 'Mandarin', 'German'],

    # Counts and numbers
    'COUNT': ['3', '4', '5', '6', '8', '10'],
    'NUMBER': ['3', '5', '10', '15'],
    'MINUTES': ['5', '10', '15', '20', '30', '45'],
    'DAYS': ['3', '5', '7', '10', '14'],
    'CLASS SIZE': ['15', '20', '25', '30', '35'],
    'SIZE': ['small (15 students)', 'medium (25 students)', 'large (35 students)'],
    'RANGE': ['1-10', '1-20', '1-100', '10-50', '1-1000'],
    'ITEMS': ['5', '8', '10', '12', '15'],
    'SENTENCES': ['3', '5', '8'],
    'STEPS': ['3', '4', '5', '6'],

    # Time and dates
    'TIME': ['45 minutes', '60 minutes', '90 minutes', '2 hours'],
    'DATE': ['next Monday', 'Friday', 'end of the week', 'in two weeks'],
    'START': ['Monday', 'next week', 'September 1st'],
    'TARGET': ['end of term', 'December', 'by spring break'],

    # Context
    'CONTEXT': [
        'a rural school with limited resources',
        'an urban public school',
        'a mixed-ability classroom',
        'an inclusive classroom with diverse learners',
        'a resource-constrained environment'
    ],
    'MATERIALS': [
        'paper, pencils, and basic classroom supplies',
        'textbooks, worksheets, and a whiteboard',
        'manipulatives, flashcards, and chart paper',
        'recycled materials and natural objects',
        'digital devices and internet access'
    ],
    'CONSTRAINTS': [
        'limited technology access',
        'large class sizes',
        'mixed ability levels',
        'time constraints of 30 minutes per lesson'
    ],

    # Text and content
    'TEXT': [
        'a short story about friendship',
        'an informational article about weather patterns',
        'a poem by Robert Frost',
        'a chapter from Charlotte\'s Web',
        'a news article about environmental conservation'
    ],
    'PASTE': ['(See student work sample below)'],
    'PASTE TEXT': ['(See student work sample below)'],
    'NOTES': [
        'bullet points from a science observation',
        'rough draft ideas for a persuasive essay',
        'math problem-solving steps',
        'brainstormed vocabulary words'
    ],
    'WORDS': [
        'beautiful, wonderful, amazing, fantastic',
        'said, walked, looked, went',
        'addition, subtraction, multiplication, division'
    ],
    'HFW': ['the, and, is, was, they, have, said, what'],  # High frequency words

    # Literacy specific
    'GPCS': ['sh, ch, th, wh', 'ai, ay, ee, ea', 'tion, sion', 'ck, ng, nk'],  # Grapheme-phoneme correspondences
    'PATTERN': ['CVC words', 'CVCE words', 'consonant blends', 'vowel teams'],
    'STEM': ['un-, re-, pre-', '-ing, -ed, -er', '-tion, -ment'],

    # Assessment
    'MISCONCEPTIONS': [
        'students thinking multiplication always makes numbers bigger',
        'confusing there/their/they\'re',
        'believing heavier objects fall faster'
    ],
    'ERRORS': [
        'run-on sentences and comma splices',
        'incorrect subject-verb agreement',
        'misplaced decimal points'
    ],
    'ANSWERS': ['A, B, C, D', '1, 2, 3, 4'],
    'CRITERIA': [
        'clarity, organization, and evidence',
        'accuracy, completeness, and presentation',
        'creativity, effort, and improvement'
    ],

    # Goals and activities
    'GOAL': [
        'improve reading comprehension by 20%',
        'master multiplication facts through 12',
        'write a five-paragraph essay independently'
    ],
    'ACTIVITY': [
        'a hands-on science experiment',
        'a collaborative group project',
        'an independent reading task',
        'a math problem-solving challenge'
    ],
    'TASK': [
        'writing a persuasive paragraph',
        'solving multi-step word problems',
        'conducting a simple experiment'
    ],

    # Audience and communication
    'AUDIENCE': [
        'parents', 'school administrators', 'fellow teachers',
        'students', 'the school board'
    ],
    'CONCERN': [
        'a student struggling with reading',
        'classroom behavior management',
        'differentiation for gifted learners',
        'supporting English language learners'
    ],
    'QUESTION': [
        'How can I differentiate instruction for mixed-ability groups?',
        'What strategies help reluctant readers?',
        'How do I assess student understanding formatively?'
    ],

    # Additional placeholders for complete coverage
    'FACTS': ['plants need sunlight to grow, water is essential for life, the Earth rotates on its axis'],
    'DIRECTION': ['forward', 'step-by-step', 'from simple to complex'],
    'LENGTH': ['100 words', '200 words', '1 paragraph', '2-3 sentences'],
    'MULTIPLE': ['2', '3', '4', '5'],
    'OPERATION': ['addition', 'subtraction', 'multiplication', 'division'],
    'TONE': ['encouraging', 'formal', 'friendly', 'professional'],
    'ANSWER': ['The answer is 42', 'Plants use photosynthesis', 'Water freezes at 0 degrees Celsius'],
    'SKILLS': ['reading comprehension, writing fluency, and critical thinking'],
    'MISCONCEPTION': ['that heavier objects fall faster than lighter ones'],
    'SKILL GAP': ['difficulty with multi-digit multiplication'],
    'TASKS': ['reading assignment, vocabulary quiz, and group discussion'],
    'EXAM DATE': ['December 15th', 'end of term', 'next Friday'],
    'TABLE': ['multiplication table for 1-10', 'vocabulary word list', 'data chart'],

    # Single-use placeholders
    'OBJECTIVE': ['Students will be able to identify the main idea in a text'],
    'TOPIC 1': ['fractions'],
    'TOPIC 2': ['decimals'],
    'TERM': ['semester', 'quarter', 'school year'],
    'FACT/SENTENCE': ['The sun is a star'],
    'DESCRIPTION': ['a hands-on science activity about magnets'],
    'STORY/PROCEDURE': ['a short story about a brave mouse'],
    'FOCUS/TOPIC': ['reading fluency'],
    'SKILL TYPE': ['phonemic awareness'],
    'LOW': ['1', 'beginner'],
    'HIGH': ['10', 'advanced'],
    'LEVELS': ['beginner, intermediate, and advanced'],
    'LIST A': ['cat, bat, hat, mat'],
    'LIST B': ['dog, log, fog, jog'],
    'LISTS': ['animal words, action words, describing words'],
    'COL1': ['Word'],
    'COL2': ['Definition'],
    'COL3': ['Example Sentence'],
    'RHYME': ['-at', '-og', '-en'],
    'RIME': ['-at', '-og', '-en'],
    'PATTERN A': ['CVC'],
    'PATTERN B': ['CVCE'],
    'STORY/TOPIC': ['a story about friendship'],
    'WORD': ['beautiful', 'important', 'interesting'],
    'SCRIPT': ['print', 'cursive'],
    'LETTERS': ['a, b, c, d, e'],
    'NUMBERS': ['1, 2, 3, 4, 5'],
    'WHOLE': ['24', '100', '50'],
    'OPS': ['addition and subtraction'],
    'OP': ['addition'],
    'NAMES/OBJECTS': ['apples, oranges, and bananas'],
    'STRATEGY': ['think-aloud', 'graphic organizers', 'peer tutoring'],
    'DIGITS': ['2-digit', '3-digit'],
    'BRIGHT SPOTS': ['strong participation and improved test scores'],
    'CRITERION': ['organization and clarity'],
    'EVIDENCE': ['well-structured paragraphs with clear topic sentences'],
    'WEAKNESS': ['needs improvement in using supporting details'],
    'ITEM TYPE': ['multiple choice', 'short answer', 'essay'],
    'FROM': ['basic addition'],
    'TO': ['multi-digit multiplication'],
    'OUTCOME': ['improved reading comprehension scores'],
    'TRIGGER': ['off-task behavior during independent work'],
    'SUBJECT/GRADE': ['Grade 5 Mathematics'],
    'LOWER': ['Grade 3'],
    'HIGHER': ['Grade 7'],
    'GROUP': ['struggling readers', 'advanced learners', 'English language learners'],
    'PRIORITIES': ['improving literacy rates, reducing achievement gaps'],
    'WEAK AREAS': ['written expression and mathematical reasoning'],
    'FUNCTION': ['analyze student data', 'generate reports'],
    'RESULT': ['personalized learning recommendations'],
    'TEACHING QUESTION': ['How do I effectively use formative assessment?'],
    'GRADE/SUBJECT': ['Grade 4 Science'],
    'PLAN A': ['direct instruction with guided practice'],
    'PLAN B': ['inquiry-based learning with hands-on activities'],
    'STUDENTS LIST': ['Maria, John, Ahmed, and Priya'],
    'PERSON': ['the school counselor'],
    'ISSUE': ['a student showing signs of anxiety'],
    'TASK TYPE': ['problem-solving'],
    'ROOT': ['multi-step word problems'],
    'PROBLEM': ['students struggling with reading comprehension'],
    'SOURCE': ['the district curriculum guide'],
    'SCENARIO': ['a student who consistently misses homework deadlines'],
    'TERMS/STEPS': ['hypothesis, experiment, observation, conclusion'],
    'WEEKS': ['6', '8', '12'],
    'TOPICS + WEIGHTS': ['fractions (30%), decimals (30%), percentages (40%)'],
    'HOURS': ['2', '3', '4'],
    'KEY': ['answer key for the chapter 5 assessment'],
    'HOME CONTEXT': ['limited internet access and shared devices'],
    'GROUP SIZE': ['3-4 students'],
    'ADULT': ['parent or guardian'],
    'INSTITUTION': ['Riverside Elementary School'],
    'MONTH': ['October', 'March', 'November'],
    'TRIGGERS': ['loud noises and sudden transitions'],
    'NEED': ['extended time on assessments'],
    'DESTINATION': ['the science laboratory'],
    'LANDMARKS': ['the library, main office, and cafeteria'],
    'NAME': ['Alex Chen'],
    'MARK': ['B+'],
    'STRENGTHS': ['creative problem-solving and active participation'],
    'NEXT STEP': ['focus on showing work in math problems'],
    'THRESHOLD': ['80%'],
    'ITEM:QTY,...': ['pencils: 30, notebooks: 30, erasers: 15'],
    'REASON': ['scheduled maintenance'],
    'PURPOSE': ['parent-teacher conferences'],
    'DATE/TIME': ['November 15th at 3:00 PM'],
    'SCORES': ['85, 78, 92, 88, 76'],
    'MIN': ['70%'],
    'AIM': ['identify students needing intervention'],
    'NAMES/ROLES': ['Ms. Smith (Principal), Mr. Jones (Counselor), Mrs. Garcia (Teacher)'],
}

# Domains that should be recategorized as policymaker
POLICYMAKER_DOMAINS = ['Administration & Governance']

# Track which values have been used for each placeholder to ensure variety
used_values = {}

def get_placeholder_value(placeholder: str, task_index: int) -> str:
    """Get a value for a placeholder, cycling through options for variety."""
    key = placeholder.upper()

    # Handle special paste-style placeholders (long text samples)
    lower_key = placeholder.lower()
    if 'essay' in lower_key or 'student' in lower_key or 'sample' in lower_key or 'work' in lower_key:
        return """My summer vacation was amazing! My family and I went to visit my grandparents who live near the beach. We spent two weeks there and I had so much fun. Every morning, I would wake up early and run to the beach to collect seashells. My grandmother taught me how to make cookies and my grandfather showed me how to fish. One day, we caught three fish and cooked them for dinner! I also made new friends with some kids who were staying nearby. We played soccer on the beach and built sandcastles together. The best part was when we saw dolphins swimming in the ocean. I took lots of pictures to show my classmates. I was sad when it was time to go home, but I'm happy because we're planning to visit again next year. This was the best summer ever!"""

    if key not in PLACEHOLDER_VALUES:
        # Return a sensible default for unknown placeholders
        return f'[{placeholder}]'

    values = PLACEHOLDER_VALUES[key]

    # Use task_index to cycle through values for variety
    if key not in used_values:
        used_values[key] = 0

    idx = used_values[key] % len(values)
    used_values[key] += 1

    return values[idx]

def fill_placeholders(text: str, task_index: int) -> str:
    """Replace all [PLACEHOLDER] patterns with realistic values."""
    def replacer(match):
        placeholder = match.group(1)
        return get_placeholder_value(placeholder, task_index)

    return re.sub(r'\[([^\]]+)\]', replacer, text)

def determine_persona(task: dict) -> str:
    """Determine the appropriate persona for a task."""
    domain = task.get('domain', '')

    if domain in POLICYMAKER_DOMAINS:
        return 'policymaker'

    # Check category for additional admin-like tasks
    category = task.get('category', '')
    if 'admin' in category.lower() or 'governance' in category.lower():
        return 'policymaker'

    # Learning domain tasks are still educator tasks (they're prompts teachers use)
    return 'educator'

def process_tasks():
    """Process all tasks and prepare for generation."""
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    processed_tasks = []
    stats = {'educator': 0, 'policymaker': 0, 'developer': 0}

    for idx, task in enumerate(data['flatTasks']):
        # Fill in placeholders
        filled_prompt = fill_placeholders(task['prompt'], idx)
        filled_title = fill_placeholders(task['title'], idx)

        # Determine persona
        persona = determine_persona(task)
        stats[persona] += 1

        # Create task in generate.py format
        processed_task = {
            'id': task['id'],
            'persona': persona,
            'title': filled_title,
            'prompt': filled_prompt,
            # Keep metadata for reference
            'domain': task['domain'],
            'category': task['category'],
            'useCase': task['useCase']
        }

        processed_tasks.append(processed_task)

    return processed_tasks, stats

def build_hierarchy(tasks: list) -> dict:
    """Build hierarchical structure from flat tasks for frontend."""
    hierarchy = {}

    for task in tasks:
        if task['persona'] != 'educator':
            continue

        domain = task.get('domain', 'Other')
        category = task.get('category', 'Other')
        use_case = task.get('useCase', 'Other')

        if domain not in hierarchy:
            hierarchy[domain] = {
                'id': domain.lower().replace(' ', '_').replace('/', '_').replace('&', 'and'),
                'name': domain,
                'categories': {}
            }

        if category not in hierarchy[domain]['categories']:
            hierarchy[domain]['categories'][category] = {
                'id': category.lower().replace(' ', '_').replace('/', '_').replace('&', 'and'),
                'name': category,
                'useCases': {}
            }

        if use_case not in hierarchy[domain]['categories'][category]['useCases']:
            hierarchy[domain]['categories'][category]['useCases'][use_case] = {
                'id': use_case.lower().replace(' ', '_').replace('/', '_').replace('&', 'and'),
                'name': use_case,
                'tasks': []
            }

        # Add task to hierarchy
        hierarchy[domain]['categories'][category]['useCases'][use_case]['tasks'].append({
            'id': task['id'],
            'domain': domain,
            'category': category,
            'useCase': use_case,
            'title': task['title'],
            'prompt': task['prompt'],
            'teacherInputs': '',
            'modelDoes': '',
            'persona': 'educator'
        })

    # Convert to list format
    domains_list = []
    for domain_data in hierarchy.values():
        domain_entry = {
            'id': domain_data['id'],
            'name': domain_data['name'],
            'categories': []
        }
        for cat_data in domain_data['categories'].values():
            cat_entry = {
                'id': cat_data['id'],
                'name': cat_data['name'],
                'useCases': []
            }
            for uc_data in cat_data['useCases'].values():
                cat_entry['useCases'].append({
                    'id': uc_data['id'],
                    'name': uc_data['name'],
                    'tasks': uc_data['tasks']
                })
            domain_entry['categories'].append(cat_entry)
        domains_list.append(domain_entry)

    flat_tasks = [t for t in tasks if t['persona'] == 'educator']

    return {
        'hierarchy': domains_list,
        'flatTasks': flat_tasks
    }

def main():
    print("Preparing tasks for generation...")
    print("=" * 60)

    tasks, stats = process_tasks()

    # Save to tasks.json (for generate.py)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

    print(f"\nProcessed {len(tasks)} tasks:")
    print(f"  - Educator: {stats['educator']}")
    print(f"  - Policymaker: {stats['policymaker']}")
    print(f"  - Developer: {stats['developer']}")

    print(f"\nSaved to: {OUTPUT_FILE}")

    # Build and save hierarchical structure for frontend
    hierarchy_data = build_hierarchy(tasks)

    with open(HIERARCHY_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(hierarchy_data, f, indent=2, ensure_ascii=False)
    print(f"Hierarchy saved to: {HIERARCHY_OUTPUT}")

    # Copy to frontend static folder
    STATIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(STATIC_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(hierarchy_data, f, indent=2, ensure_ascii=False)
    print(f"Copied to: {STATIC_OUTPUT}")

    # Show some examples
    print("\n" + "=" * 60)
    print("Sample processed tasks:")
    print("=" * 60)

    for i, task in enumerate(tasks[:3]):
        print(f"\n[{task['persona'].upper()}] {task['title']}")
        print(f"Prompt: {task['prompt'][:150]}...")

    # Show a policymaker example if any
    policymaker_tasks = [t for t in tasks if t['persona'] == 'policymaker']
    if policymaker_tasks:
        print(f"\n[POLICYMAKER] {policymaker_tasks[0]['title']}")
        print(f"Prompt: {policymaker_tasks[0]['prompt'][:150]}...")

if __name__ == '__main__':
    main()
