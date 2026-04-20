#from llm import call_llm
#from llm import call_llm_chat
from llm_aws import generate_answer

def generate_final_answer(plan, context, risks):
    prompt = f"""
    Generate AWS terraform .tf code using the logical points from PLAN_POINTS while using RAG_CONTEXT as a baseline while addressing RISK_POINTS and following the Rules:
    Rules:
    - Logical flow should be from left to right, this is for generating AWS architecture diagram from terraform code later
    - All components or components in the terraform code should be connected each other 
    - Should be production grade AWS template
    - Proper AWS assets
    - Clearly mention data flow connections
    - Integrate security at every stage
    - Add additional components if required for Secure architecture
    - Logical integration of components
    - Proper data flow end to end
    
    PLAN_POINTS:
    {plan}
    
    RAG_CONTEXT:
    {context}
    
    RISK_POINTS:
    {risks}

    """

#    return call_llm(prompt)
    return generate_answer(prompt)
#    return call_llm_chat(prompt)