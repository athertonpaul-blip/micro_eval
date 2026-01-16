#!/usr/bin/env python3
"""
Micro Edu Tasks Generator
Generates AI responses for educational micro-tasks using both API and local models.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model Registry
# Note: Model IDs are for OpenRouter API. If a model ID doesn't work, check OpenRouter's model list:
# https://openrouter.ai/models
MODELS = {
    "gpt5.2-medium": {
        "type": "api",
        "id": "openai/gpt-5.2",  # GPT-5.2 (medium thinking - standard)
        "display_name": "GPT-5.2"
    },
    "gpt5.2-low": {
        "type": "api",
        "id": "openai/gpt-4o-mini",  # GPT-4o Mini (low thinking alternative - gpt-5.2-instant not available)
        "display_name": "GPT-4o Mini"
    },
    "gpt5-mini": {
        "type": "api",
        "id": "openai/gpt-5-mini",  # GPT-5 Mini
        "display_name": "GPT-5 Mini"
    },
    "claude": {
        "type": "api",
        "id": "anthropic/claude-sonnet-4.5",  # Claude Sonnet 4.5 (latest)
        "display_name": "Claude Sonnet 4.5"
    },
    "claude-opus": {
        "type": "api",
        "id": "anthropic/claude-opus-4.5",  # Claude Opus 4.5 (latest)
        "display_name": "Claude Opus 4.5"
    },
    "gemini": {
        "type": "api",
        "id": "google/gemini-3-flash-preview",  # Gemini 3 Flash Preview (latest)
        "display_name": "Gemini 3 Flash"
    },
    "gemini-pro": {
        "type": "api",
        "id": "google/gemini-3-pro-preview",  # Gemini 3 Pro
        "display_name": "Gemini 3.0 Pro"
    },
    "gemma-3-4b": {
        "type": "api",
        "id": "google/gemma-3-4b-it",  # Gemma 3 4B Instruct
        "display_name": "Gemma 3 4B"
    },
    "phi3": {
        "type": "local",
        "id": "microsoft/Phi-3-mini-4k-instruct",
        "display_name": "Phi-3 Mini"
    }
}

# Paths
SCRIPT_DIR = Path(_file_).parent
TASKS_FILE = SCRIPT_DIR / "tasks.json"
OUTPUT_FILE = SCRIPT_DIR.parent / "docs" / "data.json"
SVELTE_DATA_FILE = SCRIPT_DIR.parent / "svelte-app" / "src" / "lib" / "data" / "tasks.json"


class ModelGenerator:
    """Handles generation from both API and local models."""

    def _init_(self):
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

    def generate_api(self, model_id: str, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate response using OpenRouter API. Returns (response, error_message)."""
        if not self.api_key:
            return None, "OPENROUTER_API_KEY not set in .env file"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/micro-edu-tasks",
            "X-Title": "Micro Edu Tasks Generator"
        }

        # Determine max_tokens based on model type
        # Reasoning models (like Gemini Pro) need much higher limits
        is_reasoning_model = "gemini" in model_id.lower() and "pro" in model_id.lower()
        max_tokens = 32000 if is_reasoning_model else 16000
        
        payload = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,  # Higher limit for reasoning models
            "temperature": 0.7
        }

        # Retry logic for network issues - be patient, some models take a while
        max_retries = 5  # More retries for slow models
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"  Retry attempt {attempt + 1}/{max_retries} for {model_id}...")
                else:
                    print(f"  Waiting for {model_id} response... (this may take a while)")
                
                # Use stream=False to avoid chunked encoding issues
                # Increased timeouts: 30s to connect, 300s (5 min) to read - some models are slow
                response = requests.post(
                    OPENROUTER_BASE_URL,
                    headers=headers,
                    json=payload,
                    timeout=(30, 300),  # (connect timeout, read timeout) - 5 minutes for slow models
                    stream=False  # Disable streaming to avoid SSL read issues
                )
                
                # Check for errors and log details
                if not response.ok:
                    error_detail = response.text[:1000]  # Increased limit to see more details
                    try:
                        error_json = response.json()
                        # Try to get more detailed error info
                        error_obj = error_json.get("error", {})
                        error_detail = error_obj.get("message", error_obj.get("type", str(error_json)))
                        # Also log the full error object for debugging
                        if error_obj:
                            print(f"  Full error object: {error_obj}")
                    except:
                        pass
                    error_msg = f"HTTP {response.status_code}: {error_detail}"
                    print(f"API Error for {model_id}: {error_msg}")
                    # For 400 errors (bad request), don't retry - the request is invalid
                    # But for other errors (429, 500, 502, 503), we should retry
                    if response.status_code == 400:
                        return None, error_msg
                    # For other errors, continue to retry logic below
                    if attempt < max_retries - 1:
                        wait_time = 5 * (2 ** attempt)
                        print(f"  Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    return None, error_msg
                
                response.raise_for_status()
                data = response.json()
                
                # Debug: log the response structure
                print(f"  Response keys: {list(data.keys())}")
                
                # Validate response structure
                if "choices" not in data:
                    error_msg = f"No 'choices' key in API response. Response keys: {list(data.keys())}"
                    print(f"API Error for {model_id}: {error_msg}")
                    print(f"  Full response: {str(data)[:500]}")
                    return None, error_msg
                
                if len(data["choices"]) == 0:
                    error_msg = "Empty 'choices' array in API response"
                    print(f"API Error for {model_id}: {error_msg}")
                    print(f"  Full response: {str(data)[:500]}")
                    return None, error_msg
                
                # Check if content exists
                choice = data["choices"][0]
                if "message" not in choice:
                    error_msg = f"No 'message' key in choice. Choice keys: {list(choice.keys())}"
                    print(f"API Error for {model_id}: {error_msg}")
                    print(f"  Full choice: {str(choice)[:500]}")
                    return None, error_msg
                
                message = choice["message"]
                content = message.get("content", "")
                reasoning = message.get("reasoning", "")
                finish_reason = choice.get("finish_reason", "unknown")
                
                # Check if response was truncated
                if finish_reason in ["length", "max_tokens", "MAX_TOKENS"]:
                    print(f"  Warning: Response may be truncated (finish_reason: {finish_reason})")
                
                # Some models (like Gemini Pro with reasoning) may have content in both fields
                # or the final answer in content and thinking steps in reasoning
                # Combine them if both exist, prioritizing content as the final answer
                if content and reasoning:
                    # If both exist, combine them (reasoning first for context, then final answer)
                    combined = f"{reasoning}\n\n---\n\n{content}" if reasoning else content
                    print(f"  Note: Combined 'reasoning' and 'content' fields for {model_id}")
                    return combined, None
                elif reasoning and not content:
                    # Only reasoning exists - this might be the full response or just thinking steps
                    print(f"  Note: Using 'reasoning' field for {model_id} (content was empty)")
                    if finish_reason in ["length", "max_tokens", "MAX_TOKENS"]:
                        print(f"  Warning: Reasoning field may be incomplete due to token limit")
                    return reasoning, None
                elif content:
                    # Only content exists (normal case)
                    return content, None
                else:
                    # Neither exists
                    error_msg = f"Empty content in response message (finish_reason: {finish_reason})"
                    print(f"API Error for {model_id}: {error_msg}")
                    print(f"  Message keys: {list(message.keys())}")
                    print(f"  Full choice: {str(choice)[:500]}")
                    return None, error_msg

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, 
                    requests.exceptions.SSLError, OSError, BrokenPipeError) as e:
                error_msg = str(e)[:200]  # Limit error message length
                if attempt < max_retries - 1:
                    # Exponential backoff: 5s, 10s, 20s, 40s - be patient
                    wait_time = 5 * (2 ** attempt)
                    print(f"  Network/timeout error for {model_id} (attempt {attempt + 1}/{max_retries}): {type(e)._name_}")
                    print(f"  Error: {error_msg}")
                    print(f"  Waiting {wait_time} seconds before retry... (some models take a while)")
                    time.sleep(wait_time)
                    continue
                else:
                    error_msg_full = f"{type(e)._name_}: {error_msg} (after {max_retries} attempts)"
                    print(f"API Error for {model_id}: {error_msg_full}")
                    print(f"  Skipping this model and continuing...")
                    return None, error_msg_full
                    
            except requests.exceptions.RequestException as e:
                error_msg = str(e)
                error_type = type(e)._name_
                error_detail = None
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_json = e.response.json()
                        error_detail = error_json.get("error", {}).get("message", str(error_json))
                    except:
                        try:
                            error_detail = e.response.text[:300]
                        except:
                            pass
                
                error_msg_full = f"{error_type}: {error_msg}"
                if error_detail:
                    error_msg_full += f" - {error_detail}"
                
                print(f"API Error for {model_id}: {error_msg_full}")
                return None, error_msg_full
            except (KeyError, IndexError) as e:
                error_msg = f"Unexpected API response format: {e}"
                print(f"API Error for {model_id}: {error_msg}")
                try:
                    if 'data' in locals():
                        print(f"  Response data keys: {list(data.keys())}")
                        print(f"  Response data sample: {str(data)[:300]}")
                except:
                    pass
                return None, error_msg
            except Exception as e:
                error_msg = str(e)
                error_type = type(e)._name_
                error_msg_full = f"{error_type}: {error_msg}"
                print(f"Unexpected error for {model_id}: {error_msg_full}")
                import traceback
                print(f"  Traceback: {traceback.format_exc()[-500:]}")  # Last 500 chars of traceback
                return None, error_msg_full
        
        return None, "Max retries exceeded"

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

    def generate(self, model_key: str, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        """Route generation to appropriate handler. Returns (response, error_message)."""
        if model_key not in MODELS:
            return None, f"Unknown model: {model_key}"

        model_config = MODELS[model_key]
        model_type = model_config["type"]
        model_id = model_config["id"]

        if model_type == "api":
            result, error = self.generate_api(model_id, prompt)
            return result, error
        elif model_type == "local":
            result = self.generate_local(model_id, prompt)
            return result, None if result else f"Local generation failed for {model_id}"
        else:
            return None, f"Unknown model type: {model_type}"


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
    """Save data to data.json and sync to Svelte app."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Also copy to Svelte app location
    SVELTE_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SVELTE_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nData saved to {OUTPUT_FILE}")
    print(f"Data synced to {SVELTE_DATA_FILE}")


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

    # Determine which model keys to use
    # Default: all OpenAI, Google, and Anthropic/Claude models
    model_keys = [
        "gpt5.2-medium", "gpt5.2-low", "gpt5-mini",  # OpenAI
        "claude", "claude-opus",  # Anthropic
        "gemini", "gemini-pro", "gemma-3-4b"  # Google
    ]
    
    # Ask user which models to regenerate
    print("\nAvailable models:")
    print("  OpenAI: gpt5.2-medium, gpt5.2-low, gpt5-mini")
    print("  Anthropic: claude (Sonnet 4.5), claude-opus (Opus 4.5)")
    print("  Google: gemini (Flash), gemini-pro (Pro), gemma-3-4b (Gemma 3 4B)")
    print("  Local: phi3")
    user_input = input(f"\nEnter models to regenerate (comma-separated, or press Enter for all API models): ").strip()
    if user_input:
        model_keys = [key.strip() for key in user_input.split(",")]
    
    print(f"\nUsing models: {', '.join(model_keys)}")
    print("Mode: Only regenerate if response is empty or missing")

    # Generate responses
    total_generations = 0
    skipped = 0

    def generate_single_model(model_key: str, prompt: str) -> Tuple[str, Optional[str], Optional[str]]:
        """Generate response for a single model. Returns (model_key, response, error_msg)."""
        try:
            response, error_msg = generator.generate(model_key, prompt)
            return model_key, response, error_msg
        except Exception as e:
            error_msg = f"{type(e)._name_}: {str(e)[:200]}"
            return model_key, None, error_msg

    for task_idx, task in enumerate(data):
        print(f"\n[{task_idx + 1}/{len(data)}] Task: {task['title']} ({task['id']})")

        # Collect models that need generation
        models_to_generate = []
        for model_key in model_keys:
            existing_response = task.get("responses", {}).get(model_key, "")
            
            # Check if response exists and is not empty
            if existing_response and existing_response.strip():
                # Check if response appears truncated (ends abruptly or is suspiciously short)
                # Truncated responses often end mid-sentence, mid-word, or with incomplete markdown
                response_trimmed = existing_response.strip()
                is_truncated = (
                    len(response_trimmed) < 100 or  # Very short responses
                    response_trimmed.endswith("| **3 -") or  # Ends mid-table
                    response_trimmed.endswith("**3 -") or  # Ends mid-table
                    response_trimmed.endswith("must be established") or  # Known truncation pattern
                    (not response_trimmed.endswith(".") and 
                     not response_trimmed.endswith("!") and 
                     not response_trimmed.endswith("?") and
                     not response_trimmed.endswith("```") and
                     len(response_trimmed) > 200)  # Long but doesn't end properly
                )
                
                if is_truncated:
                    print(f"  → {model_key}: Response appears truncated, will regenerate")
                    models_to_generate.append(model_key)
                else:
                    skipped += 1
                    print(f"  ✓ {model_key}: Already exists (skipping)")
            else:
                models_to_generate.append(model_key)

        if not models_to_generate:
            continue

        # Initialize responses dict if needed
        if "responses" not in task:
            task["responses"] = {}

        # Generate in parallel
        print(f"  Generating {len(models_to_generate)} model(s) in parallel...")
        with ThreadPoolExecutor(max_workers=len(models_to_generate)) as executor:
            # Submit all tasks
            future_to_model = {
                executor.submit(generate_single_model, model_key, task["prompt"]): model_key
                for model_key in models_to_generate
            }

            # Process results as they complete
            with tqdm(total=len(models_to_generate), desc="Models", leave=False) as pbar:
                for future in as_completed(future_to_model):
                    model_key = future_to_model[future]
                    try:
                        result_key, response, error_msg = future.result()
                        
                        if response:
                            task["responses"][result_key] = response
                            total_generations += 1
                            tqdm.write(f"  ✓ {result_key}: Success ({len(response)} chars)")
                        else:
                            if error_msg:
                                tqdm.write(f"  ✗ {result_key}: Failed - {error_msg}")
                            else:
                                tqdm.write(f"  ✗ {result_key}: Failed - No response returned")
                    except KeyboardInterrupt:
                        tqdm.write(f"  ✗ {model_key}: Interrupted by user")
                        executor.shutdown(wait=False, cancel_futures=True)
                        raise  # Re-raise to stop the script
                    except Exception as e:
                        error_msg = f"{type(e)._name_}: {str(e)[:200]}"
                        tqdm.write(f"  ✗ {model_key}: Failed - {error_msg}")
                    finally:
                        pbar.update(1)

        # Save incrementally after each task
        save_data(data)

    print("\n" + "=" * 60)
    print(f"Generation complete!")
    print(f"  New generations: {total_generations}")
    print(f"  Skipped (existing): {skipped}")
    print(f"  Output: {OUTPUT_FILE}")
    print("=" * 60)


if _name_ == "_main_":
    main()