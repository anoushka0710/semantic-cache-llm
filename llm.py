import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def call_llm(query: str, model: str) -> str:
    try:
        res = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": query}],
        )
        return res.choices[0].message.content

    except Exception as e:
        
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": query}],
        )
        return res.choices[0].message.content + " (fallback used)"