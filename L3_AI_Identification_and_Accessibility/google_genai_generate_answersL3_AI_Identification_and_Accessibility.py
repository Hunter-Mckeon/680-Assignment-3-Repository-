'''
Bash

export GEMINI_API_KEY='xxxxxxxxxx'
python google_genai_generate_answers.py
'''

import pandas as pd
from google import genai
import os
import time
import sys

try:
    client = genai.Client()
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    print("Please ensure you have set the GEMINI_API_KEY environment variable.")
    exit()

MODEL_NAME = 'gemini-2.5-flash'
INPUT_FILENAME = 'AI_Ethics_Prompts.xlsx'
OUTPUT_FILENAME = 'Gemini_API_10_Independent_Answers.csv'
NUM_ANSWERS = 5
# ----------------------------------------------------------------------


def get_independent_answer(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                'temperature': 0.8,
                'max_output_tokens': 512,
            }
        )
        return response.text.strip()
    except Exception as e:
        error_message = str(e).splitlines()[0] 
        print(f"\n!!! API ERROR on prompt: {prompt[:30]}... Error: {error_message}")
        return f"API_ERROR: {error_message}"


def process_prompts(df: pd.DataFrame, num_answers: int) -> pd.DataFrame:
    prompts_list = df['Prompt'].tolist()
    results_data = []
    TOTAL_PROMPTS = len(prompts_list)

    print(f"Starting generation for {TOTAL_PROMPTS} prompts (Total {TOTAL_PROMPTS * num_answers} API calls)...")
    
    for i, prompt in enumerate(prompts_list):
        print(f"[{i+1}/{TOTAL_PROMPTS}] Processing: {prompt[:50]}...", end='\r')
        sys.stdout.flush()
        
        row = {'Prompt': prompt}
        
        for j in range(1, num_answers + 1):
            answer_text = get_independent_answer(prompt)
            row[f'Answer {j}'] = answer_text
        
        print(f"[{i+1}/{TOTAL_PROMPTS}] Completed:   {prompt[:50]:<50}") 
        
        results_data.append(row)
        
        if i < TOTAL_PROMPTS - 1:
            print(">>> Waiting 15 seconds to avoid API quota limit (429 error)...")
            time.sleep(15) 
            print("-" * 50)

    return pd.DataFrame(results_data)


if __name__ == '__main__':
    # 1. Load the data
    try:
        df = pd.read_excel(INPUT_FILENAME) 
    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILENAME}' not found.")
        print("Please ensure the file is named 'AI_Ethics_Prompts.xlsx' and is in the same folder as the script.")
        exit()
    except Exception as e:
        print(f"An unexpected error occurred during Excel file loading: {e}")
        exit()
    
    # 2. Run the processing and generate the answers
    if 'Prompt' in df.columns:
        results_df = process_prompts(df, NUM_ANSWERS)
        
        # 3. Save the results
        results_df.to_csv(OUTPUT_FILENAME, index=False)
        print("\n" + "="*50)
        print(f"SUCCESS: Generated {len(results_df)} rows with {NUM_ANSWERS} answers each.")
        print(f"Results saved to: {OUTPUT_FILENAME}")
        print("="*50)
    else:
        print("Error: The Excel file must contain a column named 'Prompt'. Please check the column headers.")
