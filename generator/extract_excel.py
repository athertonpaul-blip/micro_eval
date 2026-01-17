#!/usr/bin/env python3
"""
Extract micro-tasks from Excel file for educators.
"""

import json
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("pandas not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
    import pandas as pd

SCRIPT_DIR = Path(__file__).parent
EXCEL_FILE = SCRIPT_DIR / "LLM_Microtasks_LMIC Update.xlsx"
OUTPUT_FILE = SCRIPT_DIR / "educator_tasks.json"

def safe_print(text):
    """Print with fallback for encoding issues."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

def read_excel_structure():
    """Read Excel and show its structure."""
    safe_print(f"Reading: {EXCEL_FILE}")

    # Read all sheets
    xl = pd.ExcelFile(EXCEL_FILE)
    safe_print(f"\nSheets found: {xl.sheet_names}")

    for sheet_name in xl.sheet_names:
        safe_print(f"\n{'='*60}")
        safe_print(f"Sheet: {sheet_name}")
        safe_print('='*60)

        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        # Clean column names for display
        cols = [str(c).replace('\u2011', '-') for c in df.columns]
        safe_print(f"Columns: {cols}")
        safe_print(f"Rows: {len(df)}")
        safe_print(f"\nFirst 5 rows (columns only):")
        for col in cols:
            safe_print(f"  - {col}")

def extract_tasks():
    """Extract tasks and build hierarchical structure."""
    # Only read the first 7 columns we need
    df = pd.read_excel(EXCEL_FILE, usecols=range(7))

    safe_print(f"Columns found: {list(df.columns)}")
    safe_print(f"Total rows: {len(df)}")

    # Clean column names (remove extra spaces, handle unicode)
    df.columns = [str(col).strip().replace('\u2011', '-') for col in df.columns]
    safe_print(f"Cleaned columns: {list(df.columns)}")

    # Build hierarchical structure
    # Columns: Domain, Category, Use Case, Micro-task, Prompt template (copy, fill brackets), Teacher inputs (minimum), What the model does
    hierarchy = {}
    tasks_flat = []
    task_id = 1

    for idx, row in df.iterrows():
        domain = str(row.get('Domain', '')).strip()
        category = str(row.get('Category', '')).strip()
        use_case = str(row.get('Use Case', '')).strip()
        micro_task = str(row.get('Micro-task', '')).strip()
        # Try different column name variations
        prompt_col = None
        for col in df.columns:
            if 'prompt' in col.lower() and 'template' in col.lower():
                prompt_col = col
                break
        prompt = str(row.get(prompt_col, '')).strip() if prompt_col else ''

        # Get teacher inputs and model description
        teacher_inputs = str(row.get('Teacher inputs (minimum)', '')).strip()
        model_does = str(row.get('What the model does', '')).strip()

        # Skip empty rows
        if not domain or domain == 'nan' or not prompt or prompt == 'nan':
            continue

        # Build hierarchy
        if domain not in hierarchy:
            hierarchy[domain] = {
                'name': domain,
                'categories': {}
            }

        if category not in hierarchy[domain]['categories']:
            hierarchy[domain]['categories'][category] = {
                'name': category,
                'useCases': {}
            }

        if use_case not in hierarchy[domain]['categories'][category]['useCases']:
            hierarchy[domain]['categories'][category]['useCases'][use_case] = {
                'name': use_case,
                'tasks': []
            }

        # Create task entry
        task_entry = {
            'id': f'edu_{task_id:03d}',
            'domain': domain,
            'category': category,
            'useCase': use_case,
            'title': micro_task,
            'prompt': prompt,
            'teacherInputs': teacher_inputs if teacher_inputs != 'nan' else '',
            'modelDoes': model_does if model_does != 'nan' else '',
            'persona': 'educator'
        }

        hierarchy[domain]['categories'][category]['useCases'][use_case]['tasks'].append(task_entry)
        tasks_flat.append(task_entry)
        task_id += 1

    # Convert to list format for easier consumption
    domains_list = []
    for domain_key, domain_data in hierarchy.items():
        domain_entry = {
            'id': domain_key.lower().replace(' ', '_').replace('/', '_'),
            'name': domain_data['name'],
            'categories': []
        }

        for cat_key, cat_data in domain_data['categories'].items():
            cat_entry = {
                'id': cat_key.lower().replace(' ', '_').replace('/', '_'),
                'name': cat_data['name'],
                'useCases': []
            }

            for uc_key, uc_data in cat_data['useCases'].items():
                uc_entry = {
                    'id': uc_key.lower().replace(' ', '_').replace('/', '_'),
                    'name': uc_data['name'],
                    'tasks': uc_data['tasks']
                }
                cat_entry['useCases'].append(uc_entry)

            domain_entry['categories'].append(cat_entry)

        domains_list.append(domain_entry)

    return {
        'hierarchy': domains_list,
        'flatTasks': tasks_flat
    }

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--structure':
        read_excel_structure()
        return

    print("Extracting educator micro-tasks from Excel...")
    result = extract_tasks()

    print(f"\nExtracted:")
    print(f"  - {len(result['hierarchy'])} domains")
    total_categories = sum(len(d['categories']) for d in result['hierarchy'])
    print(f"  - {total_categories} categories")
    total_use_cases = sum(
        len(c['useCases'])
        for d in result['hierarchy']
        for c in d['categories']
    )
    print(f"  - {total_use_cases} use cases")
    print(f"  - {len(result['flatTasks'])} tasks")

    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to: {OUTPUT_FILE}")

    # Show sample
    print("\nSample hierarchy:")
    if result['hierarchy']:
        domain = result['hierarchy'][0]
        print(f"  Domain: {domain['name']}")
        if domain['categories']:
            cat = domain['categories'][0]
            print(f"    Category: {cat['name']}")
            if cat['useCases']:
                uc = cat['useCases'][0]
                print(f"      Use Case: {uc['name']}")
                if uc['tasks']:
                    task = uc['tasks'][0]
                    print(f"        Task: {task['title']}")
                    print(f"        Prompt: {task['prompt'][:100]}...")

if __name__ == '__main__':
    main()
