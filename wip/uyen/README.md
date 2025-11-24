📂 Project Structure
code.py – Main script that runs the pipeline.

- barem.txt – Prompt template defining evaluation criteria.

- selected_dialogues.json – Input file containing dialogues to evaluate.

- barem_results_summary_gemini_pro.json – Output summary (dialogue ID, average score, model score).

- barem_results_full_gemini_pro.json – Full evaluation results from Gemini.

⚙️ How It Works
Read Prompt Loads the evaluation instructions from barem.txt.

Read Dialogues Loads dialogue data from selected_dialogues.json. Each dialogue must include:

- dialogue_id

- average_score

- turns (list of speaker turns)

- overall_scores (optional)

Format Transcripts Converts each dialogue into a text format consistent with BAREM examples.

Batch Processing Groups dialogues into batches (default: 10 per batch) and prepares them for Gemini.

Call Gemini Sends the formatted batch to Gemini (gemini-2.0-flash) for evaluation. Gemini returns a strict JSON array of results.

Parse & Validate Cleans the response, ensures it is valid JSON, and matches the number of dialogues.

Extract Scores Collects the OverallExperience.score from each result and builds a summary.

Save Outputs

barem_results_summary_gemini_pro.json: compact summary with dialogue ID, average score, and model score.

barem_results_full_gemini_pro.json: full detailed results.



▶️ Usage
1. Install dependencies:


```pip install google-generativeai```

2. Add your Gemini API key in code.py:

```genai.configure(api_key="YOUR_API_KEY")```

3. Prepare input files:

barem.txt with evaluation instructions.

selected_dialogues.json with dialogue data.

4. Run the script:

python code.py
