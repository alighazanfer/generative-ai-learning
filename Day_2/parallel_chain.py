import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableParallel
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

note_template = PromptTemplate(
    input_variables=["text"],
    template="Generate short and simple note from the following \n {text}."
)

quiz_template = PromptTemplate(
    input_variables=["text"],
    template="Generate 5 short questions and answer from the following \n {text}."
)

merge_note_quiz_template = PromptTemplate(
    input_variables=["note", "quiz"],
    template="Merge the provided note and quiz into single document \n {note} and {quiz}"
)

model = ChatOpenAI(
    model="gpt-4",  
    api_key=api_key,
)

parser = StrOutputParser()

parallel_chain = RunnableParallel({
    "note": note_template | model | parser,
    "quiz": quiz_template | model | parser
})

merge_chain = merge_note_quiz_template | model | parser

chain = parallel_chain | merge_chain

text = """
There’s a librarian who can remember every book as long as you stay in the library.

Each time you ask for something, she recalls what you said before and builds on it.
But the moment you leave the building, poof — her memory is wiped.

If you want her to remember next time, you’d need to write notes, store them in a box, and hand them back to her when you return.

That’s the difference between “her own memory” and real, lasting memory.
"""

# response = chain.invoke({"text": text})
# print(response)

# Streaming print
print("Please wait...")
for chunk in chain.stream({"text": text}):
    if chunk:
        print(chunk, end="", flush=True)
