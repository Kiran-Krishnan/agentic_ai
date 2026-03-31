from llm import call_llm

def plan_task(user_query):
    prompt = f"""
    Break this task into steps:

    Task: {user_query}

    Output steps only.
    """

    return call_llm(prompt)