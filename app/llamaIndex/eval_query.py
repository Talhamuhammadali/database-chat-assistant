from phoenix.evals import (
    HALLUCINATION_PROMPT_RAILS_MAP,
    HALLUCINATION_PROMPT_TEMPLATE,
    QA_PROMPT_RAILS_MAP,
    QA_PROMPT_TEMPLATE,
    OpenAIModel,
    llm_classify,
)
from pandas import DataFrame as df

def evaluation(queries_df: df, llm):
    # Check if the application has any indications of hallucinations
    hallucination_eval = llm_classify(
        dataframe=queries_df,
        model=llm,
        template=HALLUCINATION_PROMPT_TEMPLATE,
        rails=list(HALLUCINATION_PROMPT_RAILS_MAP.values()),
        provide_explanation=True,  # Makes the LLM explain its reasoning
    )
    hallucination_eval["score"] = (
        hallucination_eval.label[~hallucination_eval.label.isna()] == "factual"
    ).astype(int)

    # Check if the application is answering questions correctly
    qa_correctness_eval = llm_classify(
        dataframe=queries_df,
        model=llm,
        template=QA_PROMPT_TEMPLATE,
        rails=list(QA_PROMPT_RAILS_MAP.values()),
        provide_explanation=True,  # Makes the LLM explain its reasoning
        concurrency=4,
    )

    qa_correctness_eval["score"] = (
        hallucination_eval.label[~qa_correctness_eval.label.isna()] == "correct"
    ).astype(int)
    return hallucination_eval, qa_correctness_eval