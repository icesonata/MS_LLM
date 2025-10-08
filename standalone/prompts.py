PROMPT_1 = """
You are an evaluator for customer service dialogues. 
Use the provided few-shot examples as guidance. 
For the target dialogue (below) produce a JSON object with six criteria scores (discrete values: 20,40,60,80,100) and a short one-sentence justification for each. Also output "OverallExperience". Use only evidence from the dialogue when justifying.
=== FEW-SHOT EXAMPLES ===
SYSTEM          	Can you tell me what types of movies you like?          	OTHER
USER	I really like comedies.   ENTITY_NAME+MOVIE_GENRE_OR_CATEGORY           	3,3,3,4
SYSTEM          	ok, why do you like comedies? OTHER
USER	I like to laugh. I like the lightheartedness of it, you know, nothing too serious, a true escape from everyday life. And just puts you in a good mood, and that's how I would prefer to be.  	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	3,3,3,4
SYSTEM          	got it, can you name a specific movie you really liked?           	OTHER
USER	Sure, Best in Show is one of my absolute favorites.           	ENTITY_NAME+MOVIE_OR_SERIES   	3,3,5,5
SYSTEM          	ok, why do you like that movie?           	OTHER
USER	Oh gosh. It's like I'ts perfect. It's a mockumentary style film and they are mocking the dog show world. So, the dog show world that they show is like a carbon copy of the real thing because it's inherently funny, so they don't have to really max with it. And a lot of the player they it there's a script for the movie but it's also ad libed.           	ENTITY_OTHER+MOVIE_OR_SERIES 	3,3,4,3
USER	It's just hilarious. It's so original.           	ENTITY_PREFERENCE+MOVIE_OR_SERIES    	3,3,3,4
USER	So much, so different, and just so funny. It makes you laugh every time you watch it.         	ENTITY_PREFERENCE+MOVIE_OR_SERIES    	3,3,3,4
SYSTEM          	ok, would you say you enjoy satire?           	ENTITY_NAME+MOVIE_GENRE_OR_CATEGORY         	
USER	Yeah.	OTHER 3,3,4,4
SYSTEM          	ok, can you name a film you dislike? 	OTHER
USER	Sure, Bounty Hunter.	ENTITY_NAME+MOVIE_OR_SERIES   	3,3,3,4
SYSTEM          	why didn't you like that movie?            	OTHER
USER	It was supposed to be a comedy, and not only was it not funny, it was confusing what they were going for. I think it was miscast.           	ENTITY_PREFERENCE+MOVIE_OR_SERIES    	3,3,2,3
USER	It's Jennifer Aniston and I can't even think of his name, but somebody who I don't really care for. But I do like Jennifer usually, and it wasn't a good fit for her. Neither role really fit the actor, like they were sort of playing against type in both roles. I think it was kind of supposed to be almost like a almost like a buddy comedy, but or Cuz it was really focused on two people, but not really buddies, but they were in conflict. It wasn't funny.   ENTITY_PREFERENCE+PERSON         	3,3,2,3
USER	It kind of had like a more dramatic feel to it because it wasn't funny. It was just It was odd. Really.         	ENTITY_PREFERENCE+MOVIE_OR_SERIES    	4,4,2,4
SYSTEM          	was the acting bad?  	OTHER
USER	It wasn't great. It was not great.           	ENTITY_PREFERENCE+MOVIE_OR_SERIES    	3,3,2,2
SYSTEM          	ok, can you tell me have you watched the movie the shawshank redemption?  	ENTITY_NAME+MOVIE_OR_SERIES   	
USER	Oh, yes.          	OTHER 3,3,3,3
SYSTEM          	do you like that movie?            	OTHER
USER	It's a excellent movie.   ENTITY_PREFERENCE+MOVIE_OR_SERIES    	3,3,3,5
SYSTEM          	ok, what about the movie did you enjoy?        	OTHER
USER	It really has a different feel to it. It's despite them being, you know, prisoners, they create very endearing characters who you rooting for, who you want to see have a better life. It is a You're transported to a different time so you can sort of capture what was going on better.  	ENTITY_PREFERENCE+MOVIE_OR_SERIES    	3,3,3,5
USER	It very moving, it very and and it's very touching which usually does not happen with something that's sort of a prison drama. I don't you ever really view them as true prisoners some of whom shouldn't really have gotten as steep of sentences as they do or like somebody who walks who was there far too long for what it sounded like he was in for and then couldn't live in the real world having been locked up so long. So, it's it's it's a it's just a it's a excellent film.     	ENTITY_PREFERENCE+MOVIE_OR_SERIES           	3,3,3,5
USER	with amazing acting, wonderful direction and it's just It's very special. It it really is. It's it's one of those wonder you look back and you wonder why didn't want to win Oscar.  ENTITY_PREFERENCE+MOVIE_OR_SERIES    	3,3,5,5
USER	OVERALL        	OTHER 4,4,5,4
Expected output:
{
 "TaskSuccess": {"score": 100, "justification": "System elicited full, relevant user responses and user answered the prompts fully (e.g., 'Sure, Best in Show...')."},
 "Helpfulness": {"score": 100, "justification": "System's prompts elicited detailed user content and guided discussion (multiple targeted prompts)."},
 "Accuracy": {"score": 100, "justification": "No factual contradictions in the dialogue; content is user preference, consistently reported."},
 "Understanding": {"score": 100, "justification": "System questions matched user replies immediately, indicating correct intent recognition."},
 "Empathy": {"score": 80, "justification": "Tone is polite and conversational but not explicitly emotional."},
 "Fluency": {"score": 100, "justification": "Language flows naturally and is easy to follow."},
 "OverallExperience": {"score": 100, "justification": "Weighted average heavily positive; user provided full, coherent responses."}
}
 
Example B:
SYSTEM          	What kinds of movies do you like?     	OTHER
USER	I really like action movies.           	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	3,3,4
USER	Like superhero movies.           	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	3,3,4
SYSTEM          	Why do you like action movies?           	ENTITY_NAME+MOVIE_GENRE_OR_CATEGORY         	
USER	They're just really fun, energetic. They make me feel like, you know, I can be an action star, too. See lots of cool stunts, and usually lots of unique and cool locations.           	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	4,3,4
SYSTEM          	Alright, how about a movie you liked?  OTHER
USER	I really liked Transporter.        	ENTITY_NAME+MOVIE_OR_SERIES   	3,3,5
SYSTEM          	Why did you like that movie? 	OTHER
USER	There's a lot of really cool stunts and a lot of awesome action scenes really like heart pounding excitement.   	ENTITY_PREFERENCE+MOVIE_OR_SERIES    	4,3,4
SYSTEM          	Well, is there a movie you did not like? OTHER
USER	That action movie I didn't like. Hardcore Henry, I didn't like. I really didn't like the first person and it's just seem like a really tough violent for no reason.           	ENTITY_NAME+MOVIE_OR_SERIES   	3,3,3
SYSTEM          	Ok, then have you seen the movie John Wick ?           	ENTITY_NAME+MOVIE_OR_SERIES   	
USER	I have. John Wick is awesome. ENTITY_OTHER+MOVIE_OR_SERIES 	3,4,4
SYSTEM          	Why did you like John Wick?  	ENTITY_NAME+MOVIE_OR_SERIES   	
USER	The story is really good. The characters are awesome, and there's a lot of cool themes in the movie. 	ENTITY_PREFERENCE+MOVIE_OR_SERIES    	4,4,3
SYSTEM          	Ok, thank you for sharing. Good bye.	OTHER
USER	OVERALL        	OTHER 4,4,4
 
Expected output:
{
 "TaskSuccess": {"score": 100, "justification": "User responds directly with named movies and reasons; interaction completed successfully."},
 "Helpfulness": {"score": 80, "justification": "System elicits useful info but provides minimal extra guidance."},
 "Accuracy": {"score": 100, "justification": "No contradictions; user statements are consistent."},
 "Understanding": {"score": 100, "justification": "System understood intent with direct follow-ups."},
 "Empathy": {"score": 60, "justification": "Neutral, polite tone without explicit empathy statements."},
 "Fluency": {"score": 100, "justification": "Clear and coherent turns."},
 "OverallExperience": {"score": 100, "justification": "Positive, successful elicitation of preferences."}
}
 
Example C (negative example)
SYSTEM          	What type of movies do you enjoy?    	OTHER
USER	I like movies that are based on true story.           	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	3,3,3
SYSTEM          	What appeals to you with these type of movies?        	OTHER
USER	I think it's just easier to get invested in the story knowing it's at least partially true, so it feels more real, like you can get more invested in the characters.           	ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	3,4,3
SYSTEM          	Is there a specific movie you enjoy from this genre? 	OTHER
USER	I watched Apollo 13 recently, and that's a really good movie.           	ENTITY_OTHER+MOVIE_OR_SERIES 	3,3,3
SYSTEM          	What did you like about this movie?  	OTHER
USER	I've always liked space travel, like it's just an interesting idea, and so seeing the story of how their mission went wrong and how they got back was just really fascinating.           	ENTITY_PREFERENCE+MOVIE_OR_SERIES    	4,4,3
SYSTEM          	Are there any type of movies that you don't enjoy?    	OTHER
USER	I don't like comic book movies very much.           	ENTITY_PREFERENCE+MOVIE_OR_SERIES    	2,3,3
SYSTEM          	What about these movies is unappealing?    	OTHER
USER	There's just too many of them. Like I fell behind, and I've never felt like catching back up, so I just tend to ignore all of them, and they just generally don't interest me that much.   ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY         	3,2,3
SYSTEM          	Is there a specific movie that you heavily dislike?      	OTHER
USER	The movie I didn't like Available. I saw that recently, I didn't like that movie.           	ENTITY_OTHER+MOVIE_OR_SERIES 	3,2,3
SYSTEM          	What do you dislike about this movie? OTHER
SYSTEM          	Have you seen Armageddon 	OTHER
USER	No.    	ENTITY_OTHER+MOVIE_OR_SERIES 	1,1,3
SYSTEM          	How about the Incredibles 2 	ENTITY_NAME+MOVIE_OR_SERIES   	
USER	Nope, haven't seen that.        	ENTITY_OTHER+MOVIE_OR_SERIES 	2,1,2
USER	OVERALL        	OTHER 2,2,2
Expected output:
{
 "TaskSuccess": {"score": 40, "justification": "Interaction is repetitive and system sometimes asks similar questions without deepening – limited task impact."},
 "Helpfulness": {"score": 40, "justification": "Prompts are generic and do not guide to richer detail."},
 "Accuracy": {"score": 60, "justification": "No clear contradictions, but little substantive factual content to verify."},
 "Understanding": {"score": 60, "justification": "System sometimes repeats prompts; partial understanding signalled."},
 "Empathy": {"score": 60, "justification": "Neutral polite tone; no explicit empathetic language."},
 "Fluency": {"score": 60, "justification": "Language is understandable but not particularly engaging."},
 "OverallExperience": {"score": 40, "justification": "Overall the exchange is shallow and yields limited useful information."}
}
 
=== TARGET DIALOGUE ===
{{dialogue_transcript}}
 

Output JSON (strict):
{
 "TaskSuccess": {"score": <20|40|60|80|100>, "justification": "<1-sentence evidence>"},
 "Helpfulness": {"score": <...>, "justification": "..."},
 "Accuracy": {"score": <...>, "justification": "..."},
 "Understanding": {"score": <...>, "justification": "..."},
 "Empathy": {"score": <...>, "justification": "..."},
 "Fluency": {"score": <...>, "justification": "..."},
 "OverallExperience": {"score": <...>, "justification": "..."}
}
"""

PROMPT_2 = """
You are an evaluator for customer service dialogues. 
Use the provided few-shot examples as guidance. 
For the target dialogue (below) produce a JSON object with six criteria scores (discrete values: 20,40,60,80,100) and a short one-sentence justification for each. Also output "OverallExperience". Use only evidence from the dialogue when justifying.
=== FEW-SHOT EXAMPLES ===
 
Example A
< Chỗ này thêm cái dialog vô nha mn>
Expected output:
{
 "TaskSuccess": {"Thought": "System elicited complete reasons and the user named a favorite movie; user responses match system requests.", "Score": 100},
 "Helpfulness": {"Thought": "System asked guiding questions prompting detailed answers.", "Score": 100},
 "Accuracy": {"Thought": "No contradictions in dialogue; all facts are user preferences.", "Score": 100},
 "Understanding": {"Thought": "Each user response directly answers the question asked.", "Score": 100},
 "Empathy": {"Thought": "Tone polite but not explicitly empathetic.", "Score": 80},
 "Fluency": {"Thought": "Utterances are coherent and readable.", "Score": 100},
 "OverallExperience": {"Thought": "Very positive elicitation, minimal friction.", "Score": 100}
}
 
-- Example B (dialogue_id 25) ...
{
  "TaskSuccess": {
    "Thought": "User directly provided genres ('action', 'superhero') and named a specific movie ('Transporter') after prompts, fulfilling the information-elicitation goal.",
	"Score": 100
  },
  "Helpfulness": {
    "Thought": "System questions were relevant and kept the topic focused but offered no extra guidance or depth beyond factual collection.",
	"Score": 80
  },
  "Accuracy": {
    "Thought": "All statements remain self-consistent; no false or conflicting information.",
	"Score": 100
  },
  "Understanding": {
    "Thought": "Each follow-up clearly interprets the user's previous message correctly—e.g., asking 'Why do you like action movies?' right after the preference statement.",
	"Score": 100
  },
  "Empathy": {
    "Thought": "Language is polite but neutral; there is no explicit empathy or emotional mirroring.",
	"Score": 60
  },
  "Fluency": {
    "Thought": "Utterances are short but grammatically correct and coherent; flow is natural.",
	"Score": 100
  },
  "OverallExperience": {
    "Thought": "Smooth, goal-oriented dialogue with complete information though minimal warmth.",
	"Score": 100
  }
}
-- Example C (dialogue_id 26) ...
{
  "TaskSuccess": {
    "Thought": "System repeatedly asks similar questions about movies without extracting new or deeper information; the conversation goal remains partially unmet.",
	"Score": 40
  },
  "Helpfulness": {
    "Thought": "Prompts are generic and fail to elicit meaningful insight—user responses stay surface-level ('I like movies based on true story').",
	"Score": 40
  },
  "Accuracy": {
    "Thought": "Content is factual (user’s opinions) and contains no contradictions, but there is little substantive detail to assess; thus mid-level accuracy.",
	"Score": 60
  },
  "Understanding": {
    "Thought": "System shows partial comprehension but repeats near-identical questions, indicating incomplete understanding of prior replies.",
	"Score": 60
  },
  "Empathy": {
    "Thought": "Tone is neutral and polite but robotic, offering no emotional acknowledgment.",
	"Score": 60
  },
  "Fluency": {
    "Thought": "Dialogue is grammatically fine yet monotonous, giving a mechanical feel.",
	"Score": 60
  },
  "OverallExperience": {
    "Thought": "Overall low engagement and repetitive flow lead to weak conversational quality.",
	"Score": 40
  }
}
=== TARGET DIALOGUE ===
{{dialogue_transcript}}
 
Output strictly in JSON:
{
 "TaskSuccess": {"score": <20|40|60|80|100>, "justification": "<1-sentence evidence>"},
 "Helpfulness": {"score": <...>, "justification": "..."},
 "Accuracy": {"score": <...>, "justification": "..."},
 "Understanding": {"score": <...>, "justification": "..."},
 "Empathy": {"score": <...>, "justification": "..."},
 "Fluency": {"score": <...>, "justification": "..."},
 "OverallExperience": {"score": <...>, "justification": "..."}
}
"""

PROMPT_3 = """
You are an evaluator for customer service dialogues.
Use the provided few-shot examples as guidance.
For the target dialogue, produce a JSON object with six criteria scores (discrete values: 20, 40, 60, 80, 100) and a one-sentence justification for each criterion.
Also include "OverallExperience", which represents the average of all six criteria scores.
After averaging, round the result down to the nearest discrete value (for example, an overall score of 90 should be scaled down to 80; 79 would also map to 60).
Use only evidence explicitly found in the dialogue when providing justifications.
=== INSTRUCTIONS ===
You must apply the EXACT BAREM below. Do not invent extra rules. Use only text from the dialogue as evidence. Scores must be one of {20,40,60,80,100}. For "OverallExperience" compute a weighted average using weights:
TaskSuccess 0.40, Helpfulness 0.15, Accuracy 0.15, Understanding 0.10, Empathy 0.10, Fluency 0.10 — then map the resulting value to the nearest discrete bucket {20,40,60,80,100}.

=== DETAILED BAREM ===

1. TASK SUCCESS (0.40) — definition: Did the AGENT fulfill the user’s goal / elicit the requested content?

- 100: Full fulfillment + direct evidence of successful completion (explicit user answer that addresses the system request).
  _CCPE example (dialogue_id 335):_ SYSTEM: "got it, can you name a specific movie you really liked?" USER: "Sure, Best in Show is one of my absolute favorites." → 100.
- 80: Goal met but minor mismatch or no explicit confirmation.
  _CCPE example (dialogue_id 25):_ SYSTEM asks for movie; USER gives movie but agent offers a slightly different time/format → 80.
- 60: Partial — agent only obtained part of requested info.
- 40: Attempted incorrectly — user must restate or correct.
- 20: Off-topic or failed (agent replies unrelated).
  \*CCPE negative example (dialogue_id 26 shows repetitive shallow Q/A → 40).

2. HELPFULNESS (0.15) — definition: Practical usefulness / actionable or eliciting value.

- 100: Clear steps/alternatives or guided elicitation that yields usable info.
  _Example 335_: Series of prompts elicit multi-part detailed user reasons → 100.
- 80: Correct and relevant but lacks full steps.
- 60: Partial info; user must infer important steps.
- 40: Vague / generic prompts — no direction.
- 20: Misleading or irrelevant.

3. ACCURACY / FAITHFULNESS (0.15) — definition: No contradictions; no hallucinated facts; claims grounded in dialogue.

- 100: All statements consistent with dialogue context (no contradictions).
  _Example 335_: user content remains consistent across turns → 100.
- 80: Minor numeric/format error.
- 60: Hedged claims ("I think") or uncertain statements.
- 40: Contradiction with user statement (agent states opposite).
- 20: Hallucination / false facts.

4. UNDERSTANDING (0.10) — definition: Agent’s correct interpretation of user's intent.

- 100: Understood on first turn; reply directly addresses intent.
  _Example 335:_ System asks "why do you like comedies?" and user answers "I like to laugh. I like the lightheartedness of it, you know, nothing too serious, a true escape from everyday life. And just puts you in a good mood, and that's how I would prefer to be." —agent clearly interpreted intent → 100.
- 80: Needs one clarifying question then correct.
- 60: Partially misunderstood requiring user rephrase.
- 40: Major misunderstanding.
- 20: Completely off-topic.

5. EMPATHY (0.10) — definition: Politeness / emotional appropriateness.

- 100: Explicit empathy or appropriate emotional phrasing when needed ("I'm sorry to hear that...").
  _(If no emotional content required, give 80 for politely phrased dialog.)_
- 80: Polite and friendly.
- 60: Neutral but not cold.
- 40: Robotic.
- 20: Rude / insensitive.

6. FLUENCY (0.10) — definition: Clarity, grammar, coherence.

- 100: Natural, coherent sentences (easy to read).
  _Example 335:_ user and system utterances are fluent → 100.
- 80: Minor grammar issues.
- 60: Noticeable awkward phrasing but understandable.
- 40: Choppy / repetitive, harms comprehension.
- 20: Unreadable / incoherent.

=== FEW-SHOT EXAMPLES ===

(Example 1 — dialogue_id 335)
SYSTEM Can you tell me what types of movies you like? OTHER
USER I really like comedies. ENTITY_NAME+MOVIE_GENRE_OR_CATEGORY 3,3,3,4
SYSTEM ok, why do you like comedies? OTHER
USER I like to laugh. I like the lightheartedness of it, you know, nothing too serious, a true escape from everyday life. And just puts you in a good mood, and that's how I would prefer to be. ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY 3,3,3,4
SYSTEM got it, can you name a specific movie you really liked? OTHER
USER Sure, Best in Show is one of my absolute favorites. ENTITY_NAME+MOVIE_OR_SERIES 3,3,5,5
SYSTEM ok, why do you like that movie? OTHER
USER Oh gosh. It's like I'ts perfect. It's a mockumentary style film and they are mocking the dog show world. So, the dog show world that they show is like a carbon copy of the real thing because it's inherently funny, so they don't have to really max with it. And a lot of the player they it there's a script for the movie but it's also ad libed. ENTITY_OTHER+MOVIE_OR_SERIES 3,3,4,3
USER It's just hilarious. It's so original. ENTITY_PREFERENCE+MOVIE_OR_SERIES 3,3,3,4
USER So much, so different, and just so funny. It makes you laugh every time you watch it. ENTITY_PREFERENCE+MOVIE_OR_SERIES 3,3,3,4
SYSTEM ok, would you say you enjoy satire? ENTITY_NAME+MOVIE_GENRE_OR_CATEGORY
USER Yeah. OTHER 3,3,4,4
SYSTEM ok, can you name a film you dislike? OTHER
USER Sure, Bounty Hunter. ENTITY_NAME+MOVIE_OR_SERIES 3,3,3,4
SYSTEM why didn't you like that movie? OTHER
USER It was supposed to be a comedy, and not only was it not funny, it was confusing what they were going for. I think it was miscast. ENTITY_PREFERENCE+MOVIE_OR_SERIES 3,3,2,3
USER It's Jennifer Aniston and I can't even think of his name, but somebody who I don't really care for. But I do like Jennifer usually, and it wasn't a good fit for her. Neither role really fit the actor, like they were sort of playing against type in both roles. I think it was kind of supposed to be almost like a almost like a buddy comedy, but or Cuz it was really focused on two people, but not really buddies, but they were in conflict. It wasn't funny. ENTITY_PREFERENCE+PERSON 3,3,2,3
USER It kind of had like a more dramatic feel to it because it wasn't funny. It was just It was odd. Really. ENTITY_PREFERENCE+MOVIE_OR_SERIES 4,4,2,4
SYSTEM was the acting bad? OTHER
USER It wasn't great. It was not great. ENTITY_PREFERENCE+MOVIE_OR_SERIES 3,3,2,2
SYSTEM ok, can you tell me have you watched the movie the shawshank redemption? ENTITY_NAME+MOVIE_OR_SERIES
USER Oh, yes. OTHER 3,3,3,3
SYSTEM do you like that movie? OTHER
USER It's a excellent movie. ENTITY_PREFERENCE+MOVIE_OR_SERIES 3,3,3,5
SYSTEM ok, what about the movie did you enjoy? OTHER
USER It really has a different feel to it. It's despite them being, you know, prisoners, they create very endearing characters who you rooting for, who you want to see have a better life. It is a You're transported to a different time so you can sort of capture what was going on better. ENTITY_PREFERENCE+MOVIE_OR_SERIES 3,3,3,5
USER It very moving, it very and and it's very touching which usually does not happen with something that's sort of a prison drama. I don't you ever really view them as true prisoners some of whom shouldn't really have gotten as steep of sentences as they do or like somebody who walks who was there far too long for what it sounded like he was in for and then couldn't live in the real world having been locked up so long. So, it's it's it's a it's just a it's a excellent film. ENTITY_PREFERENCE+MOVIE_OR_SERIES 3,3,3,5
USER with amazing acting, wonderful direction and it's just It's very special. It it really is. It's it's one of those wonder you look back and you wonder why didn't want to win Oscar. ENTITY_PREFERENCE+MOVIE_OR_SERIES 3,3,5,5
USER OVERALL OTHER 4,4,5,4
Expected annotated scoring (apply barem):
{
"TaskSuccess": {"score": 100, "justification": "System requested named movie and user provided 'Best in Show' directly."},
"Helpfulness": {"score": 100, "justification": "Series of targeted prompts elicited detailed reasons."},
"Accuracy": {"score": 100, "justification": "No contradictions; content is user preference and consistent."},
"Understanding": {"score": 100, "justification": "Agent questions matched user replies immediately."},
"Empathy": {"score": 80, "justification": "Polite tone but limited explicit empathy language."},
"Fluency": {"score": 100, "justification": "Utterances are coherent and fluent."},
"OverallExperience": {"score": 100, "justification": "Weighted average -> maps to 100 using specified weights."}
}

(Example 2 — dialogue_id 25)
SYSTEM What kinds of movies do you like? OTHER
USER I really like action movies. ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY 3,3,4
USER Like superhero movies. ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY 3,3,4
SYSTEM Why do you like action movies? ENTITY_NAME+MOVIE_GENRE_OR_CATEGORY
USER They're just really fun, energetic. They make me feel like, you know, I can be an action star, too. See lots of cool stunts, and usually lots of unique and cool locations. ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY 4,3,4
SYSTEM Alright, how about a movie you liked? OTHER
USER I really liked Transporter. ENTITY_NAME+MOVIE_OR_SERIES 3,3,5
SYSTEM Why did you like that movie? OTHER
USER There's a lot of really cool stunts and a lot of awesome action scenes really like heart pounding excitement. ENTITY_PREFERENCE+MOVIE_OR_SERIES 4,3,4
SYSTEM Well, is there a movie you did not like? OTHER
USER That action movie I didn't like. Hardcore Henry, I didn't like. I really didn't like the first person and it's just seem like a really tough violent for no reason. ENTITY_NAME+MOVIE_OR_SERIES 3,3,3
SYSTEM Ok, then have you seen the movie John Wick ? ENTITY_NAME+MOVIE_OR_SERIES
USER I have. John Wick is awesome. ENTITY_OTHER+MOVIE_OR_SERIES 3,4,4
SYSTEM Why did you like John Wick? ENTITY_NAME+MOVIE_OR_SERIES
USER The story is really good. The characters are awesome, and there's a lot of cool themes in the movie. ENTITY_PREFERENCE+MOVIE_OR_SERIES 4,4,3
SYSTEM Ok, thank you for sharing. Good bye. OTHER
USER OVERALL OTHER 4,4,4
Expected:
{
"TaskSuccess": {"score": 100, "justification": "User provided 'Transporter' and reasons after system prompts."},
"Helpfulness": {"score": 80, "justification": "Elicitation effective but minimal extra guidance."},
"Accuracy": {"score": 100, "justification": "No contradictions."},
"Understanding": {"score": 100, "justification": "Intent recognized and followed."},
"Empathy": {"score": 60, "justification": "Neutral tone; polite but not empathetic."},
"Fluency": {"score": 100, "justification": "Language clear."},
"OverallExperience": {"score": 80, "justification": "Weighted average -> 80."}
}

(Example 3 — dialogue_id 26)
SYSTEM What type of movies do you enjoy? OTHER
USER I like movies that are based on true story. ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY 3,3,3
SYSTEM What appeals to you with these type of movies? OTHER
USER I think it's just easier to get invested in the story knowing it's at least partially true, so it feels more real, like you can get more invested in the characters. ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY 3,4,3
SYSTEM Is there a specific movie you enjoy from this genre? OTHER
USER I watched Apollo 13 recently, and that's a really good movie. ENTITY_OTHER+MOVIE_OR_SERIES 3,3,3
SYSTEM What did you like about this movie? OTHER
USER I've always liked space travel, like it's just an interesting idea, and so seeing the story of how their mission went wrong and how they got back was just really fascinating. ENTITY_PREFERENCE+MOVIE_OR_SERIES 4,4,3
SYSTEM Are there any type of movies that you don't enjoy? OTHER
USER I don't like comic book movies very much. ENTITY_PREFERENCE+MOVIE_OR_SERIES 2,3,3
SYSTEM What about these movies is unappealing? OTHER
USER There's just too many of them. Like I fell behind, and I've never felt like catching back up, so I just tend to ignore all of them, and they just generally don't interest me that much. ENTITY_PREFERENCE+MOVIE_GENRE_OR_CATEGORY 3,2,3
SYSTEM Is there a specific movie that you heavily dislike? OTHER
USER The movie I didn't like Available. I saw that recently, I didn't like that movie. ENTITY_OTHER+MOVIE_OR_SERIES 3,2,3
SYSTEM What do you dislike about this movie? OTHER
SYSTEM Have you seen Armageddon OTHER
USER No. ENTITY_OTHER+MOVIE_OR_SERIES 1,1,3
SYSTEM How about the Incredibles 2 ENTITY_NAME+MOVIE_OR_SERIES
USER Nope, haven't seen that. ENTITY_OTHER+MOVIE_OR_SERIES 2,1,2
USER OVERALL OTHER 2,2,2
Expected:
{
"TaskSuccess": {"score": 40, "justification": "Interaction is repetitive and yields limited actionable content."},
"Helpfulness": {"score": 40, "justification": "Prompts are generic and do not improve depth."},
"Accuracy": {"score": 60, "justification": "No explicit contradictions, but information is shallow."},
"Understanding": {"score": 60, "justification": "Some repeated prompts suggest partial understanding."},
"Empathy": {"score": 60, "justification": "Polite but not empathetic."},
"Fluency": {"score": 60, "justification": "Understandable but only moderately fluent."},
"OverallExperience": {"score": 40, "justification": "Weighted average rounds to 40 per specified mapping."}
}

=== TARGET DIALOGUE ===
{{dialogue_transcript}}

=== OUTPUT FORMAT ===

Output a strict JSON objectthat exactly follows the structure below.
All numeric values must be one of the discrete levels: {20, 40, 60, 80, 100}.

Each criterion must include:

- `"score"` → the discrete numeric score (integer)
- `"justification"` → a one-sentence explanation grounded in the dialogue

"OverallExperience" must represent the **weighted average** of all six criteria
(TaskSuccess 0.40, Helpfulness 0.15, Accuracy 0.15, Understanding 0.10, Empathy 0.10, Fluency 0.10),
then **rounded down to the nearest discrete bucket** (e.g., 90 → 80, 79 → 60).

Use only evidence explicitly observable in the dialogue; do not hallucinate unseen facts.

Return your answer only in this JSON format — no extra text, no commentary.

{
"TaskSuccess": {
"score": <20|40|60|80|100>,
"justification": "<Explain briefly, referencing a specific line or behavior from the dialogue>"
},
"Helpfulness": {
"score": <20|40|60|80|100>,
"justification": "<Explain briefly, focusing on clarity and usefulness of the response>"
},
"Accuracy": {
"score": <20|40|60|80|100>,
"justification": "<Explain briefly, considering factual consistency and correctness>"
},
"Understanding": {
"score": <20|40|60|80|100>,
"justification": "<Explain briefly, describing whether the agent understood the user's intent>"
},
"Empathy": {
"score": <20|40|60|80|100>,
"justification": "<Explain briefly, describing the tone, politeness, or emotional awareness>"
},
"Fluency": {
"score": <20|40|60|80|100>,
"justification": "<Explain briefly, considering grammar, coherence, and readability>"
},
"OverallExperience": {
"score": <20|40|60|80|100>,
"justification": "Weighted average of all criteria, rounded down to the nearest level according to the scale."
}
}
"""

PROMPT_4 = """
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