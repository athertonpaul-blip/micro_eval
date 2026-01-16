#!/usr/bin/env python3
"""
Micro Edu Tasks Generator
Generates AI responses for educational micro-tasks using both API and local models.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

import requests
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model Registry
MODELS = {
    "gpt4o": {
        "type": "api",
        "id": "openai/gpt-4o",
        "display_name": "GPT-4o"
    },
    "claude": {
        "type": "api",
        "id": "anthropic/claude-3.5-sonnet",
        "display_name": "Claude 3.5 Sonnet"
    },
    "gemini": {
        "type": "api",
        "id": "google/gemini-pro-1.5",
        "display_name": "Gemini 1.5 Pro"
    },
    "phi3": {
        "type": "local",
        "id": "microsoft/Phi-3-mini-4k-instruct",
        "display_name": "Phi-3 Mini"
    }
}

# Paths
SCRIPT_DIR = Path(__file__).parent
TASKS_FILE = SCRIPT_DIR / "tasks.json"
OUTPUT_FILE = SCRIPT_DIR.parent / "docs" / "data.json"


class ModelGenerator:
    """Handles generation from both API and local models."""

    def __init__(self):
        self.local_models = {}
        self.api_key = OPENROUTER_API_KEY

    def load_local_model(self, model_id: str):
        """Load a local Hugging Face model (lazy loading)."""
        if model_id in self.local_models:
            return self.local_models[model_id]

        print(f"Loading local model: {model_id}...")
        try:
            from transformers import pipeline
            import torch

            # Determine device and dtype
            device_map = "auto" if torch.cuda.is_available() else "cpu"
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

            model = pipeline(
                "text-generation",
                model=model_id,
                device_map=device_map,
                torch_dtype=torch_dtype,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.7,
            )

            self.local_models[model_id] = model
            print(f"Model loaded successfully on {device_map}")
            return model

        except Exception as e:
            print(f"Error loading local model {model_id}: {e}")
            return None

    def generate_api(self, model_id: str, prompt: str) -> Optional[str]:
        """Generate response using OpenRouter API."""
        if not self.api_key:
            print("Error: OPENROUTER_API_KEY not set in .env file")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/micro-edu-tasks",
            "X-Title": "Micro Edu Tasks Generator"
        }

        payload = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        try:
            response = requests.post(
                OPENROUTER_BASE_URL,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            print(f"API Error for {model_id}: {e}")
            return None
        except (KeyError, IndexError) as e:
            print(f"Unexpected API response format for {model_id}: {e}")
            return None

    def generate_local(self, model_id: str, prompt: str) -> Optional[str]:
        """Generate response using local Hugging Face model."""
        model = self.load_local_model(model_id)
        if model is None:
            return None

        try:
            # Format prompt for instruction-following models
            formatted_prompt = f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"

            result = model(
                formatted_prompt,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                return_full_text=False
            )

            return result[0]["generated_text"].strip()

        except Exception as e:
            print(f"Local generation error for {model_id}: {e}")
            return None

    def generate(self, model_key: str, prompt: str) -> Optional[str]:
        """Route generation to appropriate handler."""
        if model_key not in MODELS:
            print(f"Unknown model: {model_key}")
            return None

        model_config = MODELS[model_key]
        model_type = model_config["type"]
        model_id = model_config["id"]

        if model_type == "api":
            return self.generate_api(model_id, prompt)
        elif model_type == "local":
            return self.generate_local(model_id, prompt)
        else:
            print(f"Unknown model type: {model_type}")
            return None


def load_tasks() -> List[Dict[str, Any]]:
    """Load tasks from tasks.json."""
    if not TASKS_FILE.exists():
        print(f"Error: {TASKS_FILE} not found")
        sys.exit(1)

    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_existing_data() -> List[Dict[str, Any]]:
    """Load existing data.json if it exists."""
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Existing data.json is corrupted. Starting fresh.")
            return []
    return []


def save_data(data: List[Dict[str, Any]]):
    """Save data to data.json."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to {OUTPUT_FILE}")


def merge_tasks(tasks: List[Dict], existing_data: List[Dict]) -> List[Dict]:
    """Merge new tasks with existing data (incremental building)."""
    existing_map = {item["id"]: item for item in existing_data}

    merged = []
    for task in tasks:
        task_id = task["id"]

        if task_id in existing_map:
            # Keep existing responses
            merged_task = existing_map[task_id].copy()
            # Update metadata if changed
            merged_task["persona"] = task["persona"]
            merged_task["title"] = task["title"]
            merged_task["prompt"] = task["prompt"]
            merged.append(merged_task)
        else:
            # New task
            merged.append({
                "id": task["id"],
                "persona": task["persona"],
                "title": task["title"],
                "prompt": task["prompt"],
                "responses": {}
            })

    return merged


def main():
    """Main execution flow."""
    print("=" * 60)
    print("Micro Edu Tasks Generator")
    print("=" * 60)

    # Load tasks and existing data
    tasks = load_tasks()
    existing_data = load_existing_data()
    data = merge_tasks(tasks, existing_data)

    print(f"\nLoaded {len(tasks)} tasks")
    print(f"Found {len(existing_data)} existing entries")

    # Initialize generator
    generator = ModelGenerator()

    # Determine which model keys to use (API-only by default for safety)
    model_keys = ["gpt4o", "claude", "gemini"]

    # Ask user if they want to include local models
    use_local = input("\nInclude local models? (y/n, default: n): ").strip().lower()
    if use_local == "y":
        model_keys.append("phi3")

    print(f"\nUsing models: {', '.join(model_keys)}")

    # Generate responses
    total_generations = 0
    skipped = 0

    for task_idx, task in enumerate(data):
        print(f"\n[{task_idx + 1}/{len(data)}] Task: {task['title']} ({task['id']})")

        for model_key in tqdm(model_keys, desc="Models", leave=False):
            # Skip if already exists
            if model_key in task.get("responses", {}):
                skipped += 1
                tqdm.write(f"  ✓ {model_key}: Already exists (skipping)")
                continue

            # Generate
            tqdm.write(f"  → {model_key}: Generating...")
            response = generator.generate(model_key, task["prompt"])

            if response:
                if "responses" not in task:
                    task["responses"] = {}
                task["responses"][model_key] = response
                total_generations += 1
                tqdm.write(f"  ✓ {model_key}: Success ({len(response)} chars)")
            else:
                tqdm.write(f"  ✗ {model_key}: Failed")

            # Rate limiting for API calls
            if MODELS[model_key]["type"] == "api":
                time.sleep(1)

        # Save incrementally after each task
        save_data(data)

    print("\n" + "=" * 60)
    print(f"Generation complete!")
    print(f"  New generations: {total_generations}")
    print(f"  Skipped (existing): {skipped}")
    print(f"  Output: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
