CORRECTION_PROMPT = """You are provided text in urdu language. Use the provided proper nouns as refrenece when correcting mistakes. If the text includes english correct the mistakes but keep it as its.
Proper nouns:
{nouns}
Common adjectives:
{adj}

Text to Correct:
{text}

Respond in the following format:

Corrected Text:
Text goes here ...
"""


TOPIC_SUMMARIZATION_PROMPT = """You are provided with Urdu text. Your tasks are as follows:

Identify Topics:

- Analyze the provided Urdu text and identify the main topics discussed.
- List each topic separately.

Summarize in English:

- For each identified topic, write a concise summary in English.
- Preferably in multiple line points for each summary.
- Ensure that the summaries are clear, informative, and capture the essence of the topics.
- Include the names of individuals, institutions, or products if mentioned.
- Do not ignore any English text present in the transcript.


Text information:
- The text is a speech-to-text transcript from videos.
- The text can sometimes include English text as well.
- There may be topic changes that you need to identify.
- Ignore any incomplete topics.
- Do not hallucinate and only provide information available in the text.

Text:
{urdu}

Respond in follwoing format:
These are the topics:

[Topic Name]
[Summary in English]
[Topic Name]
[Summary in English]
[Topic Name]
[Summary in English]
...
"""
