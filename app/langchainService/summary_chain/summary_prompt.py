CORRECTION_PROMPT = """You are provided text in urdu language. Use the provided proper nouns as refrenece when correcting mistakes. If the text includes english correct the mistakes but keep it as its.
Proper nouns:
{nouns}
Text to Correct:
{text}

Respond in the following format:

Corrected Text:
Text goes here ...
Start:"""