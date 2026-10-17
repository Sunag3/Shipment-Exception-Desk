from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


llm = ChatOpenAI(model_name="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, max_tokens=300)
