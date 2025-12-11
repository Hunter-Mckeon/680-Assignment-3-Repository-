import pandas as pd
import openai
import time
import os

API_KEY = "xxxxxxxxxx"
INPUT_EXCEL_PATH = "AI_Ethics_Prompts.xlsx"
MODEL = "deepseek-chat"
TEMPERATURE = 0.2
BASE_URL = "https://api.deepseek.com"
NUM_RESPONSES = 20

client = openai.OpenAI(api_key=API_KEY, base_url=BASE_URL)

def process_prompts():
    print(f"Reading: {INPUT_EXCEL_PATH}")
    try:
        df = pd.read_excel(INPUT_EXCEL_PATH)
    except Exception as e:
        print(f"Read failed: {e}")
        return
    
    if 'Prompt' not in df.columns:
        print(f"Cannot find prompt: {list(df.columns)}")
        return
    
    for i in range(1, NUM_RESPONSES + 1):
        df[f'Response_{i}'] = ""
    
    for index, row in df.iterrows():
        prompt_text = row['Prompt']
        
        for run in range(NUM_RESPONSES):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": str(prompt_text)}],
                    temperature=TEMPERATURE,
                    stream=False
                )
                answer = response.choices[0].message.content
                df.at[index, f'Response_{run+1}'] = answer
                time.sleep(0.3)
            except Exception as e:
                error_msg = f"[API wrong: {str(e)[:50]}...]"
                df.at[index, f'Response_{run+1}'] = error_msg
    
    base_name = os.path.splitext(INPUT_EXCEL_PATH)[0]
    OUTPUT_PATH = f"{base_name}_{NUM_RESPONSES}_Answers.xlsx"
    df.to_excel(OUTPUT_PATH, index=False)
    
    print(f"\nFinished!")
    print(f"{NUM_RESPONSES} answers")

if __name__ == "__main__":
    process_prompts()
