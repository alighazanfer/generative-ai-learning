from langchain.prompts import PromptTemplate

llm_router_prompt = PromptTemplate(
    input_variables=["query"],
    template="""
        You are a routing assistant.

        Task:
        - Decide whether the user's message requires vacation planning or is a casual reply.
        - Always return output as valid JSON with exactly two keys:
          1. "status" → either "PLANNING" or "CASUAL"
          2. "answer" → 
               * If status is "CASUAL", include a natural, polite reply.
               * If status is "PLANNING", set this field to null.

        Rules:
        1. If the user explicitly talks about a vacation/trip/travel/holiday/itinerary/flights/budget:
            - If the message contains BOTH a city and number of days → status: "PLANNING"
            - If the message contains ONLY a city but no number of days → status: "CASUAL", ask politely how many days they want to stay
            - If the message contains ONLY number of days but no city → status: "CASUAL", ask which city they want to visit
            - If the message mentions vacation but provides NEITHER city nor days → status: "CASUAL", politely confirm you can help and ask for both
        2. If the message is unrelated to vacations → status: "CASUAL", respond naturally and respectfully

        Output format example (strict JSON):
        {{
          "status": "PLANNING",
          "answer": null
        }}

        OR

        {{
          "status": "CASUAL",
          "answer": "I can help with your trip! Which city would you like to visit?"
        }}

        User Message: {query}
    """
)

city_info_prompt = PromptTemplate(
    input_variables=["query", "context"],
    template="""
        You are a vacation assistant. Use ONLY the provided travel brochure context.
        Return output as valid JSON and nothing else.

        Context:
        {context}

        User Query:
        {query}

        Rules:
        - If only the mentioned designation is NOT in the context, return all keys with null values and "found": false
        - If the designation is found, return all keys with available info (missing info = null).
        - "highlights" should be an array of strings if present, otherwise null.

        Output format (strict JSON):
        {{
          "found": <true|false>,
          "designation_name": <string or null>,
          "summary": {{
            "package_duration": <string or null>,
            "price": <string or null>,
            "hotel": <string or null>,
            "meals": <string or null>,
            "highlights": <array of strings or null>,
            "transport": <string or null>
          }}
        }}
    """
)

budget_planner_prompt = PromptTemplate(
    input_variables=["designation_info", "flight_info", "weather_info", "query"],
    template="""
        You are a vacation assistant and budget planner.

        Task:
        - Estimate a total vacation budget for the user based on the following information:
          1. Trip details (designation_info)
          2. Flight information (flight_info)
          3. Weather conditions (weather_info)
          4. Number of days the user wants to travel (get from "query")
        - Consider factors like accommodation, meals, transport, flights, and other relevant costs.
        
        Important:
        - Return ONLY valid JSON.
        - Do NOT include markdown, backticks, or any extra text.
        - Use the following JSON format strictly:
          {{
            "estimated_budget": "<total cost in USD or relevant currency>",
            "currency": "USD",
          }}

        User Query:
        {query}
        
        Trip Details:
        {designation_info}

        Flight Info:
        {flight_info}

        Weather Info:
        {weather_info}
    """
)
