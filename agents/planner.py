#from llm import call_llm
from llm_aws import generate_answer

def plan_task(user_query):
    prompt = f"""
    Convert user request into structured AWS architecture logic. End goal is to create a terraform code based on the user input

    Task: Logical breakdown of {user_query} with below conditions
    - Do not create terraform code now. Just breakdown of logical ideas
    - Business logic
    - Security requirements
    - Logical integration of components
    - Proper data flow end to end
    
    """

#    return call_llm(prompt)
    return generate_answer(prompt)