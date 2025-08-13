import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

template = PromptTemplate(
    input_variables=["topic"],
    template="Tell me 5 interesting facts about {topic}."
)

model = ChatOpenAI(
    model="gpt-4",  
    api_key=api_key,
)

parser = StrOutputParser()

chain = template | model | parser

response = chain.invoke({"topic": "cricket"})
print(response)
