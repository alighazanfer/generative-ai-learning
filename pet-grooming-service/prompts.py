from langchain.prompts import PromptTemplate


qualify_lead_prompt = PromptTemplate(
    input_variables=["query"],
    template="""
        

        User Query:
        {query}
    """,
)
