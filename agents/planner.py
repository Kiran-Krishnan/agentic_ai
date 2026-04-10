from llm import call_llm

def plan_task(user_query):
    prompt = f"""
    Convert user request into structured AWS architecture JSON.

    Task: {user_query}

    Output JSON with:
    - services
    - network type
    - security requirements
    """

    return call_llm(prompt)