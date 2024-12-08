import streamlit as st
from groq import Groq
import json
from rdflib import Graph

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"], 
)
MODEL = 'llama-3.3-70b-versatile'

# Function to execute SPARQL queries
def execute_sparql_query(sparql_query):
    """Execute a SPARQL query on an RDF ontology file."""
    try:
        g = Graph()
        g.parse("DNO_LK.rdf", format="xml")
        result = g.query(sparql_query)
        return json.dumps({"result": [row.asdict() for row in result]})
    except Exception as e:
        return {"error": f"SPARQL execution failed: {str(e)}"}

# Function to run the conversation
def run_conversation(user_query):
    """Converts user query into SPARQL, executes it, and returns results."""
    # Provide ontology context
    ontology_context = """
    This ontology is designed for managing the digital nomad lifestyle. 

    PREFIX : <http://www.example.com/digitalnomad#>

    ### Classes
    - **Location**: Represents geographical or functional locations.
    - Subclasses:
        - `City`: Urban areas like Colombo, Kandy, Galle, Jaffna, and Ella.
        - `Country`: IslandCountry (e.g., Sri Lanka).
        - `CoworkingSpace`: Examples include Hatch Colombo and Colombo Cooperative.

    - **Climate**: Represents the type of climate in a location.
    - Subclasses:
        - `TropicalClimate`: Specific to Sri Lanka's monsoon climate.

    - **CostOfLiving**: Represents the cost of living in a location.
    - Subclasses:
        - `VeryLowCost`: Example: Jaffna.
        - `LowCost`: Example: Kandy, Galle.
        - `MediumCost`: Example: Colombo.

    - **Accommodation**: Represents places to stay for digital nomads.
    - Subclasses:
        - `Hotel`: High-end accommodations (e.g., Shangri-La Colombo, Earl's Regency).
        - `Hostel`: Budget-friendly options (e.g., Colombo City Hostel, Kandy Backpackers Hostel).
        - `ServicedApartment`: Mid-range options (e.g., Colombo Residencies).
        - `Homestay`: Local, authentic stays (e.g., Ella's Cozy Homestay).

    - **WorkRequirement**: Captures the necessities for working as a digital nomad.
    - Subclasses:
        - `InternetSpeed`: Categories include Slow, Moderate, and Fast.
        - `TimeZoneCompatibility`: Example: Sri Lanka's UTC+5:30.

    - **TravelOption**: Represents transportation options.
    - Subclasses:
        - `Train`: Example: Colombo Fort Railway Station.
        - `Bus`: Example: Private Intercity AC Bus (Colombo-Kandy).
        - `DomesticFlight`: Example: Colombo to Jaffna.

    - **HealthAndSafety**: Ensures health and safety for digital nomads.
    - Subclasses:
        - `Vaccination`: Recommendations include Hepatitis A and Typhoid for Sri Lanka.
        - `LocalLaw`: Example: ETA (Electronic Travel Authorization) for tourists in Sri Lanka.
        - `EmergencyService`: Example: "119 Police Emergency" in Sri Lanka.

    - **Preference**: Represents nomad preferences.
    - Subclasses:
        - `Budget`: Categories include VeryLowCost, LowCost, MediumCost.
        - `ClimatePreference`: Example: Preference for Tropical Climate.
        - `WorkHours`: Typical working hours like 9 AM - 5 PM.

    ### Object Properties
    - **hasClimate**: Links a location to its climate.
    - Example: Colombo `hasClimate` Tropical Monsoon Climate.

    - **hasCostOfLiving**: Links a location to its cost of living.
    - Example: Colombo `hasCostOfLiving` MediumCost.

    - **locatedIn**: Links a city or coworking space to its parent location.
    - Example: Colombo `locatedIn` Sri Lanka.

    - **offersInternetSpeed**: Links coworking spaces to available internet speeds.
    - Example: Hatch Colombo `offersInternetSpeed` Fast Internet.

    - **hasAccommodation**: Links a city to its accommodations.
    - Example: Colombo `hasAccommodation` Shangri-La Colombo.

    - **hasTravelOption**: Links a city to its travel options.
    - Example: Colombo `hasTravelOption` Train, DomesticFlight.

    - **enforcesLocalLaw**: Links a country to its local law requirements.
    - Example: Sri Lanka `enforcesLocalLaw` ETA for Tourists.

    - **requiresVaccination**: Links a country to its vaccination recommendations.
    - Example: Sri Lanka `requiresVaccination` Hepatitis A and Typhoid.

    - **hasEmergencyService**: Links a city to its emergency services.
    - Example: Colombo `hasEmergencyService` 119 Police Emergency.

    ### Data Properties
    - **hasName**: Associates an entity with a human-readable name.
    - Example: Hatch Colombo `hasName` "Hatch Colombo".

    - **hasCostValue**: Indicates the cost associated with living or accommodation.
    - Example: MediumCost in Colombo `hasCostValue` 1500.

    - **hasInternetSpeedValue**: Represents internet speed in Mbps.
    - Example: Fast Internet `hasInternetSpeedValue` 50.

    - **hasTimeZoneDifference**: Represents the time zone difference.
    - Example: Sri Lanka's UTC+5:30 is `hasTimeZoneDifference` 5.

    - **hasWorkHour**: Represents typical work hours in a location.
    - Example: Work hours in Sri Lanka are `hasWorkHour` 9 AM - 5 PM.
    """

    # Prepare the conversation for the LLM
    messages = [
        {
            "role": "system",
            "content": (
                """
                You are an Digital Nomad Lifestyle Manager ontology assistant. Always convert user queries into VALID SPARQL queries and execute them using the
                'execute_sparql_query' tool. Do not skip tool usage. If unsure, still use the tool with your best guess.
                """
            ),
        },
        {"role": "user", "content": f"Ontology context: {ontology_context}"},
        {"role": "user", "content": f"User query: {user_query}"},
    ]



    # Function call definition for SPARQL query execution
    tools = [
        {
            "type": "function",
            "function": {
                "name": "execute_sparql_query",
                "description": "Execute a SPARQL query against the ontology.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sparql_query": {
                            "type": "string",
                            "description": """The SPARQL query to execute.
                            e.g- 
                                PREFIX : <http://www.example.com/digitalnomad#> (PREFIX line should be same)
                                SELECT ?coworkingSpace ?internetSpeed
                                WHERE {
                                ?coworkingSpace a :CoworkingSpace .
                                ?coworkingSpace :offersInternetSpeed ?speed .
                                ?speed :hasInternetSpeedValue ?internetSpeed .
                                FILTER (?internetSpeed >= 50)
                                }
                            """,
                        },
                    },
                    "required": ["sparql_query"],
                },
            },
        }
    ]

    # Generate SPARQL query using LLM
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=	8000,
    )

    # st.write("Initial LLM response:", response)

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        messages.append(response_message)
        for tool_call in tool_calls:
            function_args = json.loads(tool_call.function.arguments)
            sparql_query = function_args.get("sparql_query")

            st.write("SPARQL Query -> ", sparql_query)
            print(sparql_query)

            # Execute SPARQL query
            function_response = execute_sparql_query(sparql_query)

            st.write("Function Responses -> ", function_response)

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": "execute_sparql_query",
                    "content": str(function_response)
                }
            )
        # Generate augmented chat reply
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        return second_response.choices[0].message.content

# Streamlit UI
st.title("Nomad LK Assistant 🏕️")
st.write(
    "This application converts natural language queries into SPARQL queries, "
    "executes them on a \"NomadLK ontology\", and provides the results."
)

user_query = st.text_input("Enter your query (e.g., 'Which cities have high-speed internet?')")
if st.button("Run Query"):
    if user_query:
        st.write("Processing your query...")
        result = run_conversation(user_query)
        st.write("### Response:")
        st.write(result)
    else:
        st.error("Please enter a query.")