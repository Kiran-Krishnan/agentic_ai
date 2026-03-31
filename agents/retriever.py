from rag import retrieve

def retrieve_context(query):
    return "\n".join(retrieve(query))