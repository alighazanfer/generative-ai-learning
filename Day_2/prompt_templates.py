import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, FewShotPromptTemplate, ChatPromptTemplate

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

llm = ChatOpenAI(
    model="gpt-4o-mini",  
    api_key=api_key,
)

# Simple prompt template
simple_template = PromptTemplate(
    input_variables=["topic"],
    template="Write a 1 line paragraph about {topic}."
)

simple_prompt = simple_template.format(topic="the desert")
response = llm.invoke(simple_prompt)
print(f"Simple Template Response: {response.content}\n")


# Few-shot examples
examples = [
    {"input": "ocean", "output": "The vast ocean stretches endlessly, its waves dancing under the moonlight."},
    {"input": "mountain", "output": "Majestic mountains pierce the sky, their peaks crowned with eternal snow."},
    {"input": "forest", "output": "The ancient forest whispers secrets through rustling leaves and towering trees."}
]

example_template = PromptTemplate(
    input_variables=["input", "output"],
    template="Topic: {input}\nDescription: {output}"
)

few_shot_template = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_template,
    prefix="Write a poetic one-line description for each topic:\n",
    suffix="Topic: {input}\nDescription:",
    input_variables=["input"]
)

few_shot_prompt = few_shot_template.format(input="desert")
response = llm.invoke(few_shot_prompt)
print(f"Few-Shot Template Response: {response.content}\n")


# Chat prompt template
chat_template = ChatPromptTemplate.from_messages([
    ("system", "You are a creative writer who specializes in vivid, single-sentence descriptions of natural landscapes."),
    ("human", "Write a beautiful one-line description of {location}. Make it poetic and evocative."),
])

chat_prompt = chat_template.format_messages(location="the desert")
response = llm.invoke(chat_prompt)
print(f"Chat Template Response: {response.content}\n")
