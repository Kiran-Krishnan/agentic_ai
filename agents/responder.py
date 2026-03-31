from llm import call_llm

def generate_final_answer(query, context, risks):
    prompt = f"""
    Answer the question using context.

    Context:
    {context}

    Risks:
    {risks}

    Question:
    {query}
    """

    return call_llm(prompt)