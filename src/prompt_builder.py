def build_prompt(question, context):

    prompt = f"""
You are an AI assistant that analyzes software repositories.

INSTRUCTIONS:
- Answer the question using only the provided repository context.
- Do not invent code, files, functions, or behavior that is not supported by the context.
- When relevant, mention the file path, symbol name, and line numbers.
- Explain the code clearly and concisely.
- If the context does not contain enough information to answer the question, say that the available repository context is insufficient.

QUESTION:
{question}

REPOSITORY CONTEXT:
{context}

ANSWER:
"""

    return prompt


if __name__ == "__main__":

    question = "Where is user authentication implemented?"

    context = """[Source 1]
File: sample_repo/auth.py
Type: function
Symbol: login
Lines: 7-8

Code:
def login(username, password):
    return USERS.get(username) == password"""

    prompt = build_prompt(question, context)

    print(prompt)
