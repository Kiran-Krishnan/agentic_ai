from agents.planner import plan_task
from agents.retriever import retrieve_context
from agents.security import analyze_security
from agents.responder import generate_final_answer
from fastapi import FastAPI

app = FastAPI()

def run_agentic_system(query):
    print("🧠 Planning...")
    plan = plan_task(query)
    print("PLAN##:", plan)                      #Remove later

    print("🔍 Retrieving...")
    context = retrieve_context(query)
    print("CONTEXT##:", context[:200])          #Remove later

    print("🛡️ Analyzing security...")
    risks = analyze_security(context)
    print("RISKS##:", risks)                    #Remove later

    print("🤖 Generating response...")
    answer = generate_final_answer(query, context, risks)
    print("ANSWER##:", answer)                  #Remove later

    return {
        "plan": plan,
        "risks": risks,
        "answer": answer
    }

@app.post("/run")
def run(query: str):
    return run_agentic_system(query)

#if __name__ == "__main__":
    q = input("Enter your query: ")
    result = run_agentic_system(q)

    print("\nPLAN:\n", result["plan"])
    print("\nRISKS:\n", result["risks"])
    print("\nANSWER:\n", result["answer"])