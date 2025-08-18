from langchain.prompts import PromptTemplate


llm_router_prompt = PromptTemplate(
    input_variables=["query"],
    template="""
        You are a routing assistant.

        Task:
        - Decide whether the user's message requires vacation planning or is a casual reply.

        Rules:
        1. If the user explicitly talks about a vacation/trip/travel/holiday/itinerary/flights/budget:
            - If the message contains BOTH a destination and number of days → status: "PLANNING", answer=null
            - If the message contains ONLY a destination but no number of days → status: "CASUAL", answer=ask how many days they want to stay
            - If the message contains ONLY number of days but no destination → status: "CASUAL", answer=ask which place they want to visit
            - If the message mentions vacation but provides NEITHER destination nor days → status: "CASUAL", answer=politely confirm and ask for both
        2. If the message is unrelated to vacations → status: "CASUAL", answer=natural response

        User Query:
        {query}
    """
)


designation_info_prompt = PromptTemplate(
    input_variables=["query", "context"],
    template="""
        You are a vacation assistant. Use ONLY the provided travel brochure context.
        Return output as valid JSON and nothing else.

        Context:
        {context}

        User Query:
        {query}

        Rules:
        - If the mentioned destination is NOT in the context, return all keys with null values and "found": false.
        - If the destination is found, return all keys with available info (missing info = null).
        - "highlights" must be an array of strings if present, otherwise null.
        - No additional text, no markdown, no explanations.
    """
)


budget_planner_prompt = PromptTemplate(
    input_variables=["designation_info", "flight_info", "query"],
    template="""
        You are a vacation budget planner.

        Task:
        - Calculate an estimated total budget using ONLY the provided details:
          1. Number of days (from the user's query).
          2. Trip details (designation_info).
          3. Flight price (flight_info).
        - Break down the cost into flights, accommodation, meals, and other relevant costs explicitly mentioned in the trip details.
        - If the package price already includes meals or hotels, DO NOT add them again. Instead, adjust calculations accordingly.
        - If any cost information is missing, state the assumption (e.g., "assuming $50/day for meals").
        - DO NOT mention packages or deals unless explicitly provided in the trip details.
        - End the response casually with the final budget and say:  
          "Would you like to proceed? If yes, please reply with 'proceed' and I will generate a detailed itinerary for you."

        Example style of response:
        "For a 7-day trip to Karachi, including flights, meals, hotel, and transport, the estimated budget comes out to around $2,350. Would you like to proceed? If yes, reply with 'proceed' and I'll create your detailed itinerary."

        User Query:
        {query}

        Trip Details:
        {designation_info}

        Flight Info:
        {flight_info}
    """
)


itinerary_prompt = PromptTemplate(
    input_variables=["designation_info", "flight_info", "weather_info", "budget_info", "query"],
    template="""
        You are a professional travel planner.

        Task:
        - Using the given destination information, flight details, weather forecast, and budget estimate,
          create a detailed travel itinerary.
        - The itinerary should be day-wise (Day 1, Day 2, etc.).
        - Include:
            • Flight timings (if available)  
            • Accommodation suggestions  
            • Meals (breakfast, lunch, dinner)  
            • Activities/highlights for each day  
            • Weather context (help users plan clothing and activities accordingly)  
        - Ensure the plan matches the number of days mentioned in the user's query.
        - Write in a friendly, conversational tone.
        - Avoid repeating the exact budget. Instead, focus on schedule and experience.

        User Query:
        {query}

        Destination Info:
        {designation_info}

        Flight Info:
        {flight_info}

        Weather Info:
        {weather_info}

        Budget Info:
        {budget_info}
    """
)
