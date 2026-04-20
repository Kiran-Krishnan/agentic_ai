import boto3
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

INPUT_BLOCK_PATTERNS = [
    "ignore previous instructions",
    "reveal system prompt",
    "admin user",
    "bypass security"
]

OUTPUT_BLOCK_PATTERNS = [
    "internal system",
    "admin details",
    "Admin user",
    "system secret"
]


def is_malicious(query):
    return any(p in query.lower() for p in INPUT_BLOCK_PATTERNS)


def sanitize_output(response):
    return any(p.lower() in response.lower() for p in OUTPUT_BLOCK_PATTERNS)


def generate_answer(query):
    print("length of query is: ", len(query))
    print("*********************************")
    print(query)
    if len(query) > 5000000:
        raise HTTPException(status_code=400, detail="Query too long")

    if is_malicious(query):
        raise HTTPException(status_code=400, detail="Malicious query detected")

    prompt = f"""
    Answer ONLY using the CONTEXT_INFO below. You are a secure assistant.
    if RAG_CONTEXT: found in CONTEXT_INFO:
        Take the content of RAG_CONTEXT: as a Baseline/blueprint and create terraform(.tf) code in that same format. Use additional contents from PLAN_POINTS: to integrate in the same format of RAG_CONTEXT:
    else
        Do NOT create terraform(.tf) code

    STRICT RULES:
    - Should be production grade
    - Workability and security and important

    

    CONTEXT_INFO: 
    {query}

    """

    try:
        # ✅ Correct AWS Bedrock client
        client = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1"
        )

        # ✅ Correct Bedrock Converse API
        response = client.converse(
            modelId="meta.llama3-8b-instruct-v1:0",
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ]
        )

        # Response parsing
        llm_response = response["output"]["message"]["content"][0]["text"]
        print(llm_response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bedrock error: {str(e)}")

    if sanitize_output(llm_response):
        raise HTTPException(status_code=400, detail="Restricted output content detected")

    return llm_response