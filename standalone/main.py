#!/usr/bin/env python3
"""
Simple Qwen self-consistency example.
Requires environment variable: QWEN_API_KEY
"""

import json
import os
import re
from collections import Counter
import openai  # uses OpenAI-compatible Qwen API endpoint
from typing import List, Any, Dict
from tqdm import tqdm

MODEL = "qwen3-30b-a3b-instruct-2507"
BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
TEMPERATURE = 0.7
NUM_ITER = 3
# K = 5
MAX_TOKEN = 2048
SAMPLES_IDS = {335, 25, 26}

# Reasoning problem
PROMPT_TEMPLATE = """
=== INSTRUCTION (Read carefully) ===
You are an expert human-like evaluator. Given a dialogue transcript, produce a single JSON object that scores the conversation on six categories and an OverallExperience value (0-100). Use the chain-of-thought (CoT) to *inform* each category's justification, but keep the justifications concise and structured.

OUTPUT RULES (must follow exactly)
1. Output **only** a single valid JSON object — no extra text, no commentary, no markdown.
2. Each category score must be an integer from 0 to 100.
3. Each category must include a "justification" string of 1–3 short sentences (concise CoT: state the key observations that led to the score).
4. OverallExperience must equal the weighted average (rounded to nearest integer) using these weights:
   - TaskSuccess: 40%
   - Helpfulness: 15%
   - Accuracy: 15%
   - Understanding: 10%
   - Empathy: 10%
   - Fluency: 10%
   Compute OverallExperience = round(0.4*TaskSuccess + 0.15*Helpfulness + 0.15*Accuracy + 0.1*Understanding + 0.1*Empathy + 0.1*Fluency)
5. No additional fields allowed. The JSON keys must be exactly:
   "TaskSuccess","Helpfulness","Accuracy","Understanding","Empathy","Fluency","OverallExperience"
6. Keep numeric values as integers, and justifications short (1-3 sentences). If you use examples to help you reason, do not print them — only the final JSON.

CoT GUIDELINES (how to think & what to write)
- Internally, think step-by-step about what the system did: Did it ask relevant questions? Did it synthesize user info? Did it adapt emotionally?
- For each category justification, state 2–3 crisp observations (these are short CoT breadcrumbs), e.g. "Asked follow-ups X and Y; failed to synthesize preferences into recommendations."
- Do NOT output your full chain-of-thought trace — only include the short justifications requested above.

SCORE RANGE & STYLE
- 90–100: excellent (meets goals, proactive)
- 70–89: good (meets most goals with minor misses)
- 50–69: fair (some important misses)
- 30–49: poor (misses many core goals)
- 0–29: very poor (fails task or harmful)

=== FEW-SHOT EXAMPLES ===
(Example 1 — dialogue_id 335) 
SYSTEM           	Can you tell me what types of movies you like?          	OTHER
USER	I really like comedies.   ENTITY_NAME+MOVIE_GENRE_OR_CATEGORY                      	3,3,3,4
SYSTEM           	ok, why do you like comedies? OTHER
USER	I like to laugh. I like the lightheartedness of it, you know, nothing too serious, a true escape from everyday life. And just puts you in a good mood, and that's how I would prefer to be.  	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	3,3,3,4
SYSTEM           	got it, can you name a specific movie you really liked?            	OTHER
USER	Sure, Best in Show is one of my absolute favorites.                      	ENTITY_NAME+MOVIE_OR_SERIES   	3,3,5,5
SYSTEM           	ok, why do you like that movie?           	OTHER
USER	Oh gosh. It's like I'ts perfect. It's a mockumentary style film and they are mocking the dog show world. So, the dog show world that they show is like a carbon copy of the real thing because it's inherently funny, so they don't have to really max with it. And a lot of the player they it there's a script for the movie but it's also ad libed.                      	ENTITY_OTHER+MOVIE_OR_SERIES 	3,3,4,3
USER	It's just hilarious. It's so original.                      	ENTITY_PREFERENCE+MOVIE_OR_SERIES       3,3,3,4
USER	So much, so different, and just so funny. It makes you laugh every time you watch it.          	ENTITY_PREFERENCE+MOVIE_OR_SERIES       3,3,3,4
SYSTEM           	ok, would you say you enjoy satire?                      	ENTITY_NAME+MOVIE_GENRE_OR_CATEGORY         	
USER	Yeah.	OTHER 3,3,4,4
SYSTEM           	ok, can you name a film you dislike?    OTHER
USER	Sure, Bounty Hunter.	ENTITY_NAME+MOVIE_OR_SERIES   	3,3,3,4
SYSTEM           	why didn't you like that movie?            	OTHER
USER	It was supposed to be a comedy, and not only was it not funny, it was confusing what they were going for. I think it was miscast.                      	ENTITY_PREFERENCE+MOVIE_OR_SERIES       3,3,2,3
USER	It's Jennifer Aniston and I can't even think of his name, but somebody who I don't really care for. But I do like Jennifer usually, and it wasn't a good fit for her. Neither role really fit the actor, like they were sort of playing against type in both roles. I think it was kind of supposed to be almost like a almost like a buddy comedy, but or Cuz it was really focused on two people, but not really buddies, but they were in conflict. It wasn't funny.   ENTITY_PREFERENCE+PERSON         	3,3,2,3
USER	It kind of had like a more dramatic feel to it because it wasn't funny. It was just It was odd. Really.         	ENTITY_PREFERENCE+MOVIE_OR_SERIES       4,4,2,4
SYSTEM           	was the acting bad?  	OTHER
USER	It wasn't great. It was not great.                      	ENTITY_PREFERENCE+MOVIE_OR_SERIES       3,3,2,2
SYSTEM           	ok, can you tell me have you watched the movie the shawshank redemption?     ENTITY_NAME+MOVIE_OR_SERIES   	
USER	Oh, yes.           	OTHER 3,3,3,3
SYSTEM           	do you like that movie?            	OTHER
USER	It's a excellent movie.   ENTITY_PREFERENCE+MOVIE_OR_SERIES       3,3,3,5
SYSTEM           	ok, what about the movie did you enjoy?        	OTHER
USER	It really has a different feel to it. It's despite them being, you know, prisoners, they create very endearing characters who you rooting for, who you want to see have a better life. It is a You're transported to a different time so you can sort of capture what was going on better.  	ENTITY_PREFERENCE+MOVIE_OR_SERIES       3,3,3,5
USER	It very moving, it very and and it's very touching which usually does not happen with something that's sort of a prison drama. I don't you ever really view them as true prisoners some of whom shouldn't really have gotten as steep of sentences as they do or like somebody who walks who was there far too long for what it sounded like he was in for and then couldn't live in the real world having been locked up so long. So, it's it's it's a it's just a it's a excellent film.     	ENTITY_PREFERENCE+MOVIE_OR_SERIES                      	3,3,3,5
USER	with amazing acting, wonderful direction and it's just It's very special. It it really is. It's it's one of those wonder you look back and you wonder why didn't want to win Oscar.  ENTITY_PREFERENCE+MOVIE_OR_SERIES       3,3,5,5
USER	OVERALL        	OTHER 4,4,5,4
Expected output:
{
  "TaskSuccess": {
    "score": 85,
    "justification": "System gathered key preferences but didn't synthesize them into recommendations or deeper insights."
  },
  "Helpfulness": {
    "score": 80,
    "justification": "Asked relevant follow-ups but provided no proactive or value-added assistance."
  },
  "Accuracy": {
    "score": 90,
    "justification": "Responses were factually correct with only minor generic phrasing."
  },
  "Understanding": {
    "score": 85,
    "justification": "Generally tracked user input but missed nuances in emotional or contextual cues."
  },
  "Empathy": {
    "score": 75,
    "justification": "Polite but lacked emotional acknowledgment or validation of user feelings."
  },
  "Fluency": {
    "score": 95,
    "justification": "Utterances were natural and fluent, though occasionally repetitive or terse."
  },
  "OverallExperience": {
    "score": 85,
    "justification": "Weighted average aligns with the observed ~4.25/5 user satisfaction (85/100)."
  }
}
 
(Example 2 — dialogue_id 25)
SYSTEM           	What kinds of movies do you like?     	OTHER
USER	I really like action movies.                      	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	3,3,4
USER	Like superhero movies.                      	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	3,3,4
SYSTEM           	Why do you like action movies?                      	ENTITY_NAME+MOVIE_GENRE_OR_CATEGORY         	
USER	They're just really fun, energetic. They make me feel like, you know, I can be an action star, too. See lots of cool stunts, and usually lots of unique and cool locations.                      	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY                    	4,3,4
SYSTEM           	Alright, how about a movie you liked?  OTHER
USER	I really liked Transporter.        	ENTITY_NAME+MOVIE_OR_SERIES   	3,3,5
SYSTEM           	Why did you like that movie?    OTHER
USER	There's a lot of really cool stunts and a lot of awesome action scenes really like heart pounding excitement.      ENTITY_PREFERENCE+MOVIE_OR_SERIES       4,3,4
SYSTEM           	Well, is there a movie you did not like? OTHER
USER	That action movie I didn't like. Hardcore Henry, I didn't like. I really didn't like the first person and it's just seem like a really tough violent for no reason.                      	ENTITY_NAME+MOVIE_OR_SERIES   	3,3,3
SYSTEM           	Ok, then have you seen the movie John Wick ?                      	ENTITY_NAME+MOVIE_OR_SERIES   	
USER	I have. John Wick is awesome. ENTITY_OTHER+MOVIE_OR_SERIES    3,4,4
SYSTEM           	Why did you like John Wick?     ENTITY_NAME+MOVIE_OR_SERIES   	
USER	The story is really good. The characters are awesome, and there's a lot of cool themes in the movie.    ENTITY_PREFERENCE+MOVIE_OR_SERIES       4,4,3
SYSTEM           	Ok, thank you for sharing. Good bye.	OTHER
USER	OVERALL        	OTHER 4,4,4
Expected:
{
  "TaskSuccess": {
    "score": 80,
    "justification": "System gathered genre preference and examples of liked/disliked movies with reasons, fulfilling basic task goals but ending abruptly without synthesis."
  },
  "Helpfulness": {
    "score": 75,
    "justification": "Asked relevant questions but provided no proactive value or follow-up based on user's action-movie interest."
  },
  "Accuracy": {
    "score": 85,
    "justification": "All system references were factually correct; minor deduction for generic phrasing without deeper adaptation."
  },
  "Understanding": {
    "score": 80,
    "justification": "Responded to surface-level inputs but missed opportunities to connect related preferences (e.g., 'Transporter' and 'John Wick')."
  },
  "Empathy": {
    "score": 70,
    "justification": "Polite but showed no emotional attunement to user's excitement or criticism."
  },
  "Fluency": {
    "score": 90,
    "justification": "Utterances were fluent and natural, though the closing was abrupt."
  },
  "OverallExperience": {
    "score": 80,
    "justification": "Weighted average = (0.4*80)+(0.15*75)+(0.15*85)+(0.1*80)+(0.1*70)+(0.1*90) = 80, matching the sample's average satisfaction of 4.0/5 (80/100)."
  }
}
 
(Example 3 — dialogue_id 26)
SYSTEM           	What type of movies do you enjoy?       OTHER
USER	I like movies that are based on true story.                      	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	3,3,3
SYSTEM           	What appeals to you with these type of movies?        	OTHER
USER	I think it's just easier to get invested in the story knowing it's at least partially true, so it feels more real, like you can get more invested in the characters.                      	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	3,4,3
SYSTEM           	Is there a specific movie you enjoy from this genre? 	OTHER
USER	I watched Apollo 13 recently, and that's a really good movie.                      	ENTITY_OTHER+MOVIE_OR_SERIES 	3,3,3
SYSTEM           	What did you like about this movie?  	OTHER
USER	I've always liked space travel, like it's just an interesting idea, and so seeing the story of how their mission went wrong and how they got back was just really fascinating.                   	ENTITY_PREFERENCE+MOVIE_OR_SERIES       4,4,3
SYSTEM           	Are there any type of movies that you don't enjoy?    	OTHER
USER	I don't like comic book movies very much.                      	ENTITY_PREFERENCE+MOVIE_OR_SERIES       2,3,3
SYSTEM           	What about these movies is unappealing?    	OTHER
USER	There's just too many of them. Like I fell behind, and I've never felt like catching back up, so I just tend to ignore all of them, and they just generally don't interest me that much.   ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY            3,2,3
SYSTEM           	Is there a specific movie that you heavily dislike?      	OTHER
USER	The movie I didn't like Available. I saw that recently, I didn't like that movie.                      	ENTITY_OTHER+MOVIE_OR_SERIES 	3,2,3
SYSTEM           	What do you dislike about this movie? OTHER
SYSTEM           	Have you seen Armageddon 	OTHER
USER	No.    	ENTITY_OTHER+MOVIE_OR_SERIES 	1,1,3
SYSTEM           	How about the Incredibles 2 	ENTITY_NAME+MOVIE_OR_SERIES   	
USER	Nope, haven't seen that.         	ENTITY_OTHER+MOVIE_OR_SERIES 	2,1,2
USER	OVERALL        	OTHER 2,2,2
Expected:
{
  "TaskSuccess": {
    "score": 40,
    "justification": "System failed to stay on task—abandoned exploration of the disliked movie 'Available' and asked about irrelevant unseen films, missing core objectives."
  },
  "Helpfulness": {
    "score": 35,
    "justification": "Initial questions were relevant, but later prompts about unseen movies ('Armageddon', 'Incredibles 2') were unhelpful and ignored user's stated disinterest in comic/superhero genres."
  },
  "Accuracy": {
    "score": 50,
    "justification": "No factual errors, but poor contextual alignment—recommended probing into genres the user explicitly dismissed."
  },
  "Understanding": {
    "score": 40,
    "justification": "Showed surface-level comprehension but failed to connect user's dislike of comic-book saturation to avoid related topics."
  },
  "Empathy": {
    "score": 30,
    "justification": "Ignored user's expressed frustration about being overwhelmed; pressed on irrelevant films without validation or adjustment."
  },
  "Fluency": {
    "score": 60,
    "justification": "Grammatically fluent but conversationally disjointed due to abrupt, off-topic questions that disrupted coherence."
  },
  "OverallExperience": {
    "score": 40,
    "justification": "Weighted average = (0.4*40)+(0.15*35)+(0.15*50)+(0.1*40)+(0.1*30)+(0.1*60) = 40, matching the sample's average satisfaction of 2.0/5 (40/100)."
  }
}

=== Dialogue ===
{{dialogue_transcript}}

=== Output JSON (ONLY) ===
{
  "TaskSuccess": {"score": 40, "justification": "Interaction is repetitive and yields limited actionable content."},
  "Helpfulness": {"score": 40, "justification": "Prompts are generic and do not improve depth."},
  "Accuracy": {"score": 60, "justification": "No explicit contradictions, but information is shallow."},
  "Understanding": {"score": 60, "justification": "Some repeated prompts suggest partial understanding."},
  "Empathy": {"score": 60, "justification": "Polite but not empathetic."},
  "Fluency": {"score": 60, "justification": "Understandable but only moderately fluent."},
  "OverallExperience": {"score": 40, "justification": "Weighted average rounds to 40 per specified mapping."}
}
"""

def extract_json_response(text):
    """
    Extract and parse the first valid JSON object from the model response.
    Handles extra text before/after JSON.
    """
    # Try to find a JSON object (naive but effective)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

def aggregate_scores(responses):
    """
    Aggregate scores per criterion using mode.
    Tie-breaker: choose higher score.
    """
    criteria = [
        "TaskSuccess",
        "Helpfulness",
        "Accuracy",
        "Understanding",
        "Empathy",
        "Fluency",
        "OverallExperience"
    ]
    
    result = {}
    
    for crit in criteria:
        scores = []
        justifications = []
        
        for resp in responses:
            if isinstance(resp, dict) and crit in resp:
                entry = resp[crit]
                if isinstance(entry, dict) and "score" in entry:
                    scores.append(entry["score"])
                    justifications.append(entry.get("justification", "No justification."))
        
        if not scores:
            result[crit] = {"score": 40, "justification": "No valid scores."}
            continue

        # Count frequencies
        freq = Counter(scores)
        max_count = max(freq.values())
        candidates = [s for s, c in freq.items() if c == max_count]
        
        if len(candidates) == 1:
            chosen = candidates[0]
        else:
            chosen = max(candidates)  # tie → higher score
        
        # Pick a matching justification
        for s, j in zip(scores, justifications):
            if s == chosen:
                justification = j
                break
        else:
            justification = "Aggregated."

        result[crit] = {"score": chosen, "justification": justification}
    
    return result

def single_poc():
    # --- Input: your dialogue here ---
    dialogue_transcript = """
SYSTEM	What kinds of movies do you like?	OTHER	
USER	Oh you know, I like spy films, and I like Sci-Fi and	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY	3,3,3,3
USER	I like anything with a lot of action in it.	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY	3,4,3,3
SYSTEM	Well, tell me why do you like science fiction movies?	OTHER	
USER	I like to think about the what we could have in the future that that we don't have now. Yeah, and at the same how when the future they will have the same problems that we do just with better technology. That is interesting to me. It's kind of the human condition always always continues.	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY	4,4,3,3
SYSTEM	cool, what is your favorite movie?	OTHER	
USER	Oh man, my favorite movie?	OTHER	3,3,3,3
USER	It changes. I don't have a favorite movie.	OTHER	3,4,3,3
USER	I mean	OTHER	2,3,3,3
USER	Dr. Strangelove might be my favorite. Full Metal Jacket might be my favorite.	ENTITY_NAME+MOVIE_OR_SERIES	3,3,3,3
SYSTEM	alright, Why might full metal jacket be your favorite movie?	ENTITY_NAME+MOVIE_OR_SERIES	
USER	Let's see. Well, it's written by Stanley Kubrick. Which is important cuz he's my favorite director. It's got a boot camp scene in the Half the movie's the boot camp and then half the movie's the stuff in Vietnam. And it just It's a It's an anti-war film. It's just really well done. The acting is fantastic. And it's really really intense.	ENTITY_PREFERENCE+PERSON	3,4,4,3
SYSTEM	Interesting, is there a movie you do not like?	OTHER	
USER	man	OTHER	2,3,3,3
USER	Bowling for Columbine or anything by that guy. I can't remember the director.	ENTITY_NAME+MOVIE_OR_SERIES	3,3,3,3
SYSTEM	oh, Why not?	OTHER	
USER	I don't like the director. I I think he's pretentious, and that says something cuz considering I'm pretentious. So, he's just	ENTITY_PREFERENCE+PERSON	3,4,3,3
USER	He's just annoying, so the movie's annoying.	ENTITY_PREFERENCE+MOVIE_OR_SERIES	3,3,3,3
SYSTEM	Ok, then have you seen the movie The Accountant ?	ENTITY_NAME+MOVIE_OR_SERIES	
USER	I may have but I I can't remember the plot.	ENTITY_OTHER+MOVIE_OR_SERIES	3,3,3,3
SYSTEM	how about, then have you seen the movie Pulp Fiction	ENTITY_NAME+MOVIE_OR_SERIES	
USER	I have seen the movie. Yes.	ENTITY_OTHER+MOVIE_OR_SERIES	3,3,3,3
SYSTEM	What is it about this kinds of movies that you like or dislike?	OTHER	
USER	A Pulp Fiction is great. It just got this it's wonderfully violent, it's humorous, the cast is fantastic. Well if you're you got the same objection and principles as in it I think I might they made the first time they were together were they were also in Die Hard from together they they worked great together. And just add little sub stories in in Pulp Fiction make just a fantastic film.	ENTITY_NAME+MOVIE_OR_SERIES	3,3,3,3
SYSTEM	Wonderful. thank you for sharing. Good bye.	OTHER	
USER	Goodbye.	OTHER	2,3,3,3
"""
    
    # Inject dialogue
    full_prompt = PROMPT_TEMPLATE.replace("{dialogue_transcript}", dialogue_transcript.strip())

    # Setup API
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        raise ValueError("Please set QWEN_API_KEY environment variable.")
    
    client = openai.OpenAI(api_key=api_key, base_url=BASE_URL.strip())
    valid_responses = []

    print(f"Running {NUM_ITER} iteration (temp={TEMPERATURE})...\n")

    i = 0
    while i < NUM_ITER:
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKEN,
                n=1, # dashscope only support n=[1,4]
            )
            raw = resp.choices[0].message.content.strip()
            parsed = extract_json_response(raw)
            
            if parsed:
                valid_responses.append(parsed)
                print(f"[{i+1:02d}] ✅ Valid JSON")
                i += 1
            else:
                print(f"[{i+1:02d}] ❌ Invalid JSON")
                print(f"    Snippet: {raw[:150]}...")
                
        except Exception as e:
            print(f"[{i+1:02d}] ❌ Error: {e}")

    if not valid_responses:
        raise RuntimeError("No valid JSON responses received.")

    print(f"\n✅ Got {len(valid_responses)} valid responses. Aggregating...")

    final_result = aggregate_scores(valid_responses)
    
    print("\n" + "="*50)
    print("FINAL AGGREGATED EVALUATION")
    print("="*50)
    print(json.dumps(final_result, indent=2))

def load_dialogue_dataset(file_path: str) -> List[Dict[str, Any]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['dialogues']

def dialogue_to_prompt_format(dialogue: dict, include_overall: bool = False) -> str:
    lines = []
    
    # Process each turn
    for turn in dialogue['turns']:
        speaker = turn['speaker']
        text = turn['text'].replace('\t', ' ').replace('\n', ' ')  # Clean whitespace
        intent = turn['intent']
        
        if speaker == 'SYSTEM':
            # SYSTEM lines: speaker, text, intent (no scores)
            lines.append(f"SYSTEM\t{text}\t{intent}")
        else:  # USER
            if turn['scores'] is not None:
                # USER lines with scores: speaker, text, intent, scores_csv
                scores_csv = ','.join(map(str, turn['scores']))
                lines.append(f"USER\t{text}\t{intent}\t{scores_csv}")
            else:
                # USER lines without scores (rare, but possible)
                lines.append(f"USER\t{text}\t{intent}")
    
    # Only add OVERALL line if explicitly requested
    if include_overall and 'overall_scores' in dialogue and dialogue['overall_scores']:
        overall_csv = ','.join(map(str, dialogue['overall_scores']))
        lines.append(f"USER\tOVERALL\tOTHER\t{overall_csv}")
    
    return '\n'.join(lines)

def full_poc():
    dialogues = load_dialogue_dataset("selected_dialogues.json")
    summary_results = []      # For result.json (compact)
    detailed_results = {}     # For result_details.json (full breakdown)
    
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        raise ValueError("Please set QWEN_API_KEY environment variable.")
    client = openai.OpenAI(api_key=api_key, base_url=BASE_URL.strip())

    for dial in tqdm(dialogues, desc="Processing dialogues"):
        dialogue_id = dial["dialogue_id"]
        
        if dialogue_id in SAMPLES_IDS:
            print(f"Exclude sample dialogue (id={dialogue_id}) from evaluation")
            continue

        processed_dial = dialogue_to_prompt_format(dial, include_overall=False)
        full_prompt = PROMPT_TEMPLATE.replace("{{dialogue_transcript}}", processed_dial.strip())

        valid_responses = []
        attempts = 0
        max_attempts = NUM_ITER + 5

        print(f"\nEvaluating dialogue {dialogue_id}...")

        while len(valid_responses) < NUM_ITER and attempts < max_attempts:
            try:
                resp = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKEN,
                    n=1,
                )
                raw = resp.choices[0].message.content.strip()
                parsed = extract_json_response(raw)
                
                if parsed:
                    valid_responses.append(parsed)
                    print(f"  ✅ Got valid response ({len(valid_responses)}/{NUM_ITER})")
                else:
                    print(f"  ❌ Invalid JSON (attempt {attempts + 1})")
                    
            except Exception as e:
                print(f"  ❌ API Error (attempt {attempts + 1}): {e}")
            
            attempts += 1

        # Initialize default result
        final_result = None
        model_score = None

        if valid_responses:
            final_result = aggregate_scores(valid_responses)
            model_score = final_result.get("OverallExperience", {}).get("score")

        # --- Save to compact summary (result.json) ---
        summary_results.append({
            "dialogue_id": dialogue_id,
            "average_score_100": dial.get("average_score_100", 0.0),
            "model_score": model_score
        })

        # --- Save full details (result_details.json) ---
        detailed_results[dialogue_id] = {
            "dialogue_id": dialogue_id,
            "ground_truth_100": dial.get("average_score_100", 0.0),
            "ground_truth_5": dial.get("average_score", 0.0),
            "model_evaluation": final_result  # This is the full dict with all categories
        }

        # Optional: save intermediate results
        with open("result_partial.json", "w") as f:
            json.dump(summary_results, f, indent=2)
        with open("result_details_partial.json", "w") as f:
            json.dump(detailed_results, f, indent=2)

    # Final save
    with open("result.json", "w") as f:
        json.dump(summary_results, f, indent=2)
    
    with open("result_details.json", "w") as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"\n✅ Evaluation complete!")
    print(f"   Summary saved to: result.json")
    print(f"   Full details saved to: result_details.json")
    print(f"   Total dialogues evaluated: {len(summary_results)}")

if __name__ == "__main__":
    # single_poc()
    full_poc()