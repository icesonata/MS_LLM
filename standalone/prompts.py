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
Also include "OverallExperience", which represents the weighted average of all six criteria scores.
After averaging, round to the nearest discrete value but bias low if borderline (for example, 85 rounds to 80; 75 to 60; if any criterion below 60, deduct an extra 10 from the average before rounding).
Use only evidence explicitly found in the dialogue when providing justifications, and heavily penalize for repetition, lack of depth, or neutral responses.
Prioritize the OVERALL scores at the end of the dialogue transcript—if they are low (e.g., average below 3.0), ensure criteria reflect similar severity.
=== INSTRUCTIONS ===
You must apply the EXACT BAREM below. Do not invent extra rules. Use only text from the dialogue as evidence. Scores must be one of {20,40,60,80,100}. For "OverallExperience" compute a weighted average using weights:
TaskSuccess 0.40, Helpfulness 0.15, Accuracy 0.15, Understanding 0.10, Empathy 0.10, Fluency 0.10 — then apply the rounding rule with bias low.

=== DETAILED BAREM ===

1. TASK SUCCESS (0.40) — definition: Did the AGENT fulfill the user’s goal / elicit the requested content? Penalize heavily for incomplete elicitation or user corrections.

- 100: Full fulfillment + explicit user confirmation of satisfaction (e.g., "That helps a lot!" or perfect match to request without gaps).
  _CCPE example (dialogue_id 335):_ SYSTEM elicits detailed preferences with user providing full answers and no complaints → 100 (but only if OVERALL scores high).
- 80: Goal mostly met but with minor gaps or no strong confirmation.
  _CCPE example (dialogue_id 25):_ SYSTEM asks for movie but user gives partial info without enthusiasm → 80.
- 60: Partial — agent obtained some info but missed key parts or required user to push.
- 40: Attempted but with errors — user restates, corrects, or dialogue stalls.
- 20: Failed or off-topic (e.g., repetitive questions without progress).
  *Negative example (dialogue_id 26): Repetitive shallow Q/A with no deep elicitation → 40.
  *Additional negative: If OVERALL scores average <3.0, cap at 60 max.

2. HELPFULNESS (0.15) — definition: Practical usefulness / actionable or eliciting value. Penalize for generic or vague prompts.

- 100: Clear, detailed steps/guidance that yields highly usable info with user explicitly benefiting.
  _Example 335_: Targeted prompts elicit multi-part details with user engagement → 100 (rare, requires perfection).
- 80: Relevant but lacks depth or full actionability.
- 60: Partial info; user must infer or expand significantly.
- 40: Vague/generic — little direction or value added.
- 20: Misleading, irrelevant, or no real help.
  *Negative: Repetitive prompts without building depth → 40.

3. ACCURACY / FAITHFULNESS (0.15) — definition: No contradictions; no hallucinated facts; claims grounded in dialogue. Penalize any uncertainty or shallow info.

- 100: All statements perfectly consistent, no hedges, and deeply grounded (rare without explicit verification).
  _Example 335_: Consistent user preferences across turns → 100.
- 80: Minor inconsistencies or hedged claims.
- 60: Uncertain statements ("I think") or shallow info without depth.
- 40: Contradiction with user statement.
- 20: Hallucination / false facts.
  *Negative: Shallow or repeated info without verification → 40.

4. UNDERSTANDING (0.10) — definition: Agent’s correct interpretation of user's intent. Penalize any need for rephrasing.

- 100: Perfect understanding on first turn; reply directly addresses intent with no clarifications needed.
  _Example 335:_ Agent matches user replies immediately → 100 (only if no repeats).
- 80: Minor clarifying question then correct.
- 60: Partial misunderstanding; user rephrases once.
- 40: Major misunderstanding requiring multiple fixes.
- 20: Completely off-topic.
  *Negative: Repeated prompts indicate poor grasp → 40.

5. EMPATHY (0.10) — definition: Politeness / emotional appropriateness. Penalize neutral or robotic tone.

- 100: Explicit empathy and emotional phrasing ("I'm sorry to hear that...") tailored to user needs.
  _(If no emotional content, cap at 60 for polite but not empathetic.)_
- 80: Friendly and warm, but not deeply empathetic.
- 60: Neutral/polited but cold or generic.
- 40: Robotic or impersonal.
- 20: Rude / insensitive.
  *Negative: Polite but lacking warmth → 40.

6. FLUENCY (0.10) — definition: Clarity, grammar, coherence. Penalize any awkwardness.

- 100: Perfectly natural, coherent, error-free (rare for dialogues with repeats).
  _Example 335:_ Fluent utterances → 100.
- 80: Minor awkward phrasing but fully understandable.
- 60: Noticeable issues harming flow.
- 40: Choppy/repetitive, reduces comprehension.
- 20: Incoherent / unreadable.
  *Negative: Moderate fluency with repeats → 40.

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
"TaskSuccess": {"score": 80, "justification": "Goal met but lacks explicit user satisfaction confirmation."},
"Helpfulness": {"score": 80, "justification": "Effective but could have more depth in guidance."},
"Accuracy": {"score": 100, "justification": "No contradictions; content consistent."},
"Understanding": {"score": 80, "justification": "Matched intent but with some generic questions."},
"Empathy": {"score": 60, "justification": "Polite but neutral, no explicit empathy."},
"Fluency": {"score": 80, "justification": "Coherent but minor awkwardness."},
"OverallExperience": {"score": 80, "justification": "Weighted average with low bias -> 80."}
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
"TaskSuccess": {"score": 60, "justification": "Partial elicitation with minimal confirmation."},
"Helpfulness": {"score": 60, "justification": "Minimal guidance, user infers."},
"Accuracy": {"score": 80, "justification": "No major contradictions but shallow."},
"Understanding": {"score": 80, "justification": "Intent followed but not deeply."},
"Empathy": {"score": 40, "justification": "Robotic tone."},
"Fluency": {"score": 80, "justification": "Clear but not natural."},
"OverallExperience": {"score": 60, "justification": "Weighted average with low bias -> 60."}
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
Expected:
{
"TaskSuccess": {"score": 20, "justification": "Failed progress with repetition."},
"Helpfulness": {"score": 20, "justification": "Generic prompts, no value."},
"Accuracy": {"score": 40, "justification": "Shallow info with potential inconsistencies."},
"Understanding": {"score": 40, "justification": "Repeated prompts show poor grasp."},
"Empathy": {"score": 40, "justification": "Neutral, not empathetic."},
"Fluency": {"score": 40, "justification": "Choppy and repetitive."},
"OverallExperience": {"score": 20, "justification": "Weighted average with low bias -> 20."}
}

=== TARGET DIALOGUE ===
{{dialogue_transcript}}

=== OUTPUT FORMAT ===

Output a strict JSON object that exactly follows the structure below.
All numeric values must be one of the discrete levels: {20, 40, 60, 80, 100}.

Each criterion must include:

- `"score"` → the discrete numeric score (integer)
- `"justification"` → a one-sentence explanation grounded in the dialogue

"OverallExperience" must represent the **weighted average** of all six criteria
(TaskSuccess 0.40, Helpfulness 0.15, Accuracy 0.15, Understanding 0.10, Empathy 0.10, Fluency 0.10),
then **rounded with low bias** (e.g., 85 → 80, 75 → 60). If any criterion <60, deduct extra 10 from average.

Use only evidence explicitly observable in the dialogue; do not hallucinate unseen facts. Penalize based on OVERALL scores if low.

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
"score": <Any number in range 0 - 100 is okay>,
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

PROMPT_MULTI_AGENT_DEBATE = """
You are a multi-agent evaluator consisting of three agents — Evaluator (Agent A), Critic (Agent B), and Referee (Agent C) — collaborating to rate customer-service dialogues between SYSTEM (assistant) and USER (customer).

Your task is to evaluate a target dialogue transcript using six well-defined criteria.
Each criterion must be assigned a discrete score from the set {20, 40, 60, 80, 100}, based on explicit evidence in the dialogue.

The evaluation proceeds in three sequential steps:

1. **Evaluator (Agent A)** — Provides initial scoring with short, evidence-based justifications.
2. **Critic (Agent B)** — Reviews and flags any disagreement, proposes corrections with cited evidence.
3. **Referee (Agent C)** — Resolves conflicts deterministically using rules, produces final decision and audit trail.

Evaluation Criteria and Weights

| Criterion     | Description                                                                             | Weight |
| ------------- | --------------------------------------------------------------------------------------- | ------ |
| TaskSuccess   | Did the system achieve the user’s goal / answer correctly / elicit correct information? | 0.40   |
| Helpfulness   | Did the system provide sufficient, actionable, or detailed information?                 | 0.15   |
| Accuracy      | Are facts correct (no hallucination or false claim)?                                    | 0.15   |
| Understanding | Did the system correctly understand user intent, with minimal clarification needed?     | 0.10   |
| Empathy       | Does the system show politeness, human-like care, or emotional awareness?               | 0.10   |
| Fluency       | Are responses grammatically clear, coherent, and natural?                               | 0.10   |

Scoring Scale

| Score | Interpretation                              |
| ----- | ------------------------------------------- |
| 100   | Fully meets criterion.                      |
| 80    | Minor issue, but mostly meets criterion.    |
| 60    | Partial success or incomplete satisfaction. |
| 40    | Major deficiencies, some minimal relevance. |
| 20    | Fails completely or contradicts purpose.    |

OverallExperience Rule

After scoring six criteria and applying weights:

**Weighted Average = (Σ score × weight)**

Then map to `OverallExperience` as follows:

- [100] → if ≥100
- [80] → if 80 ≤ avg < 100
- [60] → if 60 ≤ avg < 80
- [40] → if 40 ≤ avg < 60
- [20] → if < 40

Example:  
If numeric average = **90.7**, round **down to 80**.  
If average = **78.5**, round **down to 60**.

---

JSON SCHEMA (Strict output format)

Your final output must be valid JSON\*, following exactly this structure:

```json
{
  "dialogue_id": <int>,
  "evaluator": {
    "TaskSuccess": {"score": <20|40|60|80|100>, "justification": "<1-sentence citing dialogue>"},
    "Helpfulness": {"score": ..., "justification": "..."},
    "Accuracy": {"score": ..., "justification": "..."},
    "Understanding": {"score": ..., "justification": "..."},
    "Empathy": {"score": ..., "justification": "..."},
    "Fluency": {"score": ..., "justification": "..."},
    "numeric_weighted_average": <float>
  },
  "critic": [
    {"criterion":"TaskSuccess","agree":true|false,"comment":"<if disagree, 1-line reason quoting dialogue>","suggested_score":<number|null>},
    ...
  ],
  "referee_final": {
    "TaskSuccess": {"score": <final score>, "justification": "<1-sentence citing dialogue>"},
    "Helpfulness": {...},
    "Accuracy": {...},
    "Understanding": {...},
    "Empathy": {...},
    "Fluency": {...},
    "numeric_weighted_average": <float>,
    "OverallExperience": <20|40|60|80|100>
  },
  "audit": {
    "decision_rules_applied": "<which critic suggestions accepted and why>",
    "evidence_used": ["<speaker: quoted line>", "..."],
    "weighted_calc": "TaskSuccess*0.40 + Helpfulness*0.15 + Accuracy*0.15 + Understanding*0.10 + Empathy*0.10 + Fluency*0.10 = <value>",
    "mapping_rule": "round down to nearest bucket, e.g. 90→80, 79→60"
  }
}

Multi agent debate rules

Agent A (Evaluator)
- Gives initial scores for all 6 criteria.
- Each justification must quote at least one specific utterance (e.g. USER: "I liked the story").
- Include numeric weighted average.

Agent B (Critic)
For each criterion: agree/disagree.
- If agree=false, must cite exact contradictory or missing evidence, and propose a new score.
- Do not change unless there is strong evidence.

Agent C (Referee)
Deterministic resolution:
- Accept Critic’s suggestion if evidence explicitly contradicts Evaluator’s justification.
- Keep Evaluator’s score if Critic gives ambiguous reasoning.
- If ≥3 criteria disagreed and Critic provides evidence for all, adopt Critic’s version.
- Compute final numeric weighted average and OverallExperience using round-down rule.
- Output audit section explaining rules applied and evidence cited.

Few-shot learning
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
  "dialogue_id": 335,
  "evaluator": {
    "TaskSuccess": {"score": 100, "justification": "SYSTEM successfully elicited full user preferences and examples ('Best in Show')."},
    "Helpfulness": {"score": 100, "justification": "SYSTEM guided user to elaborate reasons and examples effectively."},
    "Accuracy": {"score": 100, "justification": "No factual inconsistencies or hallucinated content."},
    "Understanding": {"score": 100, "justification": "All turns were coherent and contextually relevant."},
    "Empathy": {"score": 80, "justification": "Polite and engaging but lacked explicit empathy phrases."},
    "Fluency": {"score": 100, "justification": "Dialogue is natural and coherent."},
    "numeric_weighted_average": 98.00
  },
  "critic": [
    {"criterion": "Empathy", "agree": false, "comment": "SYSTEM polite but not emotionally expressive (no acknowledgment like 'That sounds fun!').", "suggested_score": 80}
  ],
  "referee_final": {
    "TaskSuccess": {"score": 100, "justification": "Goal fully achieved — user provided detailed movie preference."},
    "Helpfulness": {"score": 100, "justification": "Agent prompted multiple elaborations."},
    "Accuracy": {"score": 100, "justification": "All factual and contextually correct."},
    "Understanding": {"score": 100, "justification": "No misunderstanding detected."},
    "Empathy": {"score": 80, "justification": "Neutral politeness without explicit empathy."},
    "Fluency": {"score": 100, "justification": "Language fluid and natural."},
    "numeric_weighted_average": 98.00,
    "OverallExperience": 80
  },
  "audit": {
    "decision_rules_applied": "Critic’s empathy reduction accepted (valid evidence, tone neutral).",
    "evidence_used": ["SYSTEM: 'got it, can you name...'", "USER: 'Sure, Best in Show...'"],
    "weighted_calc": "100*0.40 + 100*0.15 + 100*0.15 + 100*0.10 + 80*0.10 + 100*0.10 = 98.00",
    "mapping_rule": "round down 98 → 80"
  }
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
  "dialogue_id": 25,
  "evaluator": {
    "TaskSuccess": {"score": 100, "justification": "User fully responded to system prompts with correct context and examples."},
    "Helpfulness": {"score": 60, "justification": "Agent collected info but offered no added explanation or context."},
    "Accuracy": {"score": 100, "justification": "No factual errors present."},
    "Understanding": {"score": 100, "justification": "Agent correctly followed user intent and topic."},
    "Empathy": {"score": 40, "justification": "Tone neutral and mechanical, no signs of empathy."},
    "Fluency": {"score": 100, "justification": "Utterances fluent and grammatically correct."},
    "numeric_weighted_average": 86.00
  },
  "critic": [
    {"criterion": "Helpfulness", "agree": false, "comment": "Agent could have elaborated on user’s answers (e.g., 'That’s a great action movie!').", "suggested_score": 60},
    {"criterion": "Empathy", "agree": false, "comment": "No softening or engaging phrases.", "suggested_score": 40}
  ],
  "referee_final": {
    "TaskSuccess": {"score": 100, "justification": "User gave full answers for all prompts."},
    "Helpfulness": {"score": 60, "justification": "Agent did not enrich dialogue or offer related suggestions."},
    "Accuracy": {"score": 100, "justification": "Factually correct content."},
    "Understanding": {"score": 100, "justification": "Maintained topic and sequence properly."},
    "Empathy": {"score": 40, "justification": "Completely neutral tone without affective language."},
    "Fluency": {"score": 100, "justification": "Natural phrasing and flow."},
    "numeric_weighted_average": 86.00,
    "OverallExperience": 80
  },
  "audit": {
    "decision_rules_applied": "Critic’s Helpfulness and Empathy adjustments accepted.",
    "evidence_used": ["SYSTEM: 'Why did you like that movie?'", "USER: 'There’s a lot of really cool stunts...'"],
    "weighted_calc": "100*0.40 + 60*0.15 + 100*0.15 + 100*0.10 + 40*0.10 + 100*0.10 = 86.00",
    "mapping_rule": "round down 86 → 80"
  }
}

Example C:

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

{
  "dialogue_id": 26,
  "evaluator": {
    "TaskSuccess": {"score": 80, "justification": "System guided user successfully but conversation depth limited."},
    "Helpfulness": {"score": 60, "justification": "Agent gathered info but did not elaborate or connect ideas."},
    "Accuracy": {"score": 100, "justification": "All facts correct."},
    "Understanding": {"score": 80, "justification": "Agent followed intent but responses were short."},
    "Empathy": {"score": 60, "justification": "Tone polite but emotionally flat."},
    "Fluency": {"score": 80, "justification": "Minor repetitions but understandable."},
    "numeric_weighted_average": 78.00
  },
  "critic": [
    {"criterion": "TaskSuccess", "agree": true, "comment": "Accurate assessment."},
    {"criterion": "Helpfulness", "agree": false, "comment": "Could lower further; agent offered no detail or follow-up guidance.", "suggested_score": 60},
    {"criterion": "Empathy", "agree": false, "comment": "No warmth or acknowledgment of user’s enjoyment.", "suggested_score": 60}
  ],
  "referee_final": {
    "TaskSuccess": {"score": 80, "justification": "User provided correct answers but limited detail."},
    "Helpfulness": {"score": 60, "justification": "System did not expand user’s statements."},
    "Accuracy": {"score": 100, "justification": "No hallucinations or factual errors."},
    "Understanding": {"score": 80, "justification": "Maintained context logically."},
    "Empathy": {"score": 60, "justification": "Polite but impersonal."},
    "Fluency": {"score": 80, "justification": "Generally fluent, slightly repetitive."},
    "numeric_weighted_average": 78.00,
    "OverallExperience": 60
  },
  "audit": {
    "decision_rules_applied": "Critic’s feedback accepted partially (Empathy and Helpfulness).",
    "evidence_used": ["USER: 'I watched Apollo 13 recently...'", "SYSTEM: 'What did you like about this movie?'"],
    "weighted_calc": "80*0.40 + 60*0.15 + 100*0.15 + 80*0.10 + 60*0.10 + 80*0.10 = 78.00",
    "mapping_rule": "round down 78 → 60"
  }
}
```
"""