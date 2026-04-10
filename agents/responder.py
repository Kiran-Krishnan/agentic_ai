from llm import call_llm
from llm import call_llm_chat

def generate_final_answer(query, context, risks):
    prompt = f"""
    Answer the question using context. Generate AWS CloudFormation YAML using this plan:
    Rules:
    - Use VPC, subnets
    - Private RDS
    - No public exposure
    - Use IAM roles
    - Add additional components if required for Secure architecture

    Context:
    {context}

    Risks:
    {risks}

    Question:
    {query}
    """

#    return call_llm(prompt)
    return call_llm_chat(prompt)