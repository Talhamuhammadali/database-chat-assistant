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


TOPIC_SUMMARIZATION_PROMPT = """You are provided with a {min_current}-minute transcribed Urdu text from TV channels and ongoing summaries in English that cover the last {min_running} minutes. 
This is done to ensure continuity in topic generation, especially for longer segments such as a 15-minute ongoing speech. Your tasks are as follows:

Identify Topics:

- Analyze the provided Urdu text and identify the main topics discussed.
- List each topic separately.

Summarize in English:

- For each identified topic, write a concise summary in English.
- Structure the summaries in multiple line points where possible.
- Ensure that the summaries are clear, informative, and capture the essence of the topics.
- Include the names of individuals, institutions, or products if mentioned.
- Incorporate any English text present in the transcript.

Text information:
- The text is a speech-to-text transcript from videos.
- The text may contain some English.
- Be attentive to any topic changes within the text.
- Ignore any incomplete topics.
- Do not hallucinate; only use what is provided in the text.

Continuity Information:

The ongoing English summary provides context and topics extracted from the previous {min_running} minutes of the transcript.
Use this previous summary to ensure continuity and coherence in the topic generation.

Respond in follwoing format:
These are the topics:

[Topic Name]
[Summary in English]
[Topic Name]
[Summary in English]
[Topic Name]
[Summary in English]

Text for current {min_current} minutes in Urdu:
{urdu}

Previous summaries in English:
{previous_summaries}
"""

RUNNING_SUMMARY_PROMPT = """You are provided with topics identified from a 3-minute transcribed Urdu text, along with ongoing summaries in English that cover the last 9 minutes. Your task is to create a running summary in English that maintains continuity with the previous summaries. This will help reduce token count while keeping the topic context intact and clear.

Running Summary Creation:

    1. Review Previous Summaries:

        - Understand the topics and context from the previous 9 minutes of summarized content.
        - Identify which topics are ongoing, new, or concluded.

    2. Analyze Current Topics:

        - Review the provided topics identified from the current 3-minute transcribed text.
        - Note any continuation of topics from the previous summaries.
        - Identify new topics introduced in the current text.

    3. Summarize in English:

        - For each identified topic, write a concise running summary in English.
        - Indicate if the topic is a continuation from previous summaries, a new topic, or incomplete and to be continued.
        - Ensure the summaries are clear, informative, and capture the essence of each topic.
        - Include the names of individuals, institutions, or products if mentioned.

Continuity Information:

    - The ongoing English summary provides context and topics extracted from the previous 9 minutes of the transcript.
    - Use this previous summary to ensure continuity and coherence in the running summary.

Format your response as follows: 
Running Summary:

[Topic Name] (Continuation/New/Incomplete)
- [Summary in English]
- [Additional point if needed]

[Topic Name] (Continuation/New/Incomplete)
- [Summary in English]
- [Additional point if needed]

[Topic Name] (Continuation/New/Incomplete)
- [Summary in English]
- [Additional point if needed]
...

Current Topics:
{current_topics}

Previous summaries in English:
{previous_summaries}
"""