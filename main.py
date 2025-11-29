from langchain.agents import create_agent
import os
from langchain.chat_models import init_chat_model
import asyncio
from langchain.tools import tool
from tapo import ApiClient


os.environ["GOOGLE_API_KEY"] = "$GOOGLE_API_KEY"
model = init_chat_model("google_genai:gemini-2.5-flash-lite", temperature=0.0, max_tokens=500)
hub_ip = "$hub_ip"
tapo_email = "$tapo_email"
tapo_password = "$tapo_password"

@tool()
def main():
    """
    There is a Hub which is connected to multiple sensors. Fetch temperature and humidity from Tapo sensors.
    Args: sensor_name: Specific sensor name (e.g. "kitchen") or "all" for all sensors
    Returns all matching sensor readings or full list if "all".
    """
    # Running ASYNCIO function to fetch Sensor Data in await
    async def fetch_sensors():
        client = ApiClient(tapo_username= tapo_email, tapo_password=tapo_password)

        hub = await client.h100(hub_ip)
        #print("\nTapo Hub accessed successfully")
        #print("\nListing Child Sensors and Data:")
        children = await hub.get_child_device_list()

        readings = []
        for child in children:
            #print((getattr(child, 'device_id', None)))
            #print("\nTapo Device ID:", child.device_id,"\nName:", child.nickname)

            #Join.readings is expecting a string, but it is getting a tuple, Hence converting them to string
            reading = f"""
            Tapo Device ID: {child.device_id}
            Name: {child.nickname}
            Tapo Device Status: {str(child.status).split('.', 1)[1]}
            Tapo Humidity: {round(child.current_humidity, 2)}
            Tapo Temperature: {round(child.current_temperature, 2)}
            """

            readings.append(reading)
        return "\n".join(readings)

    return asyncio.run(fetch_sensors())
#'''
system_prompt=("You are a friendly smart home assistant that can help inform users of the temperature and "
               "humidity of your Tapo devices.")
agent = create_agent(
    model= model,
    tools=[main],

    system_prompt= system_prompt
)
#'''

#asyncio.run(main())

messages = [
    #{"messages": [{"role": "user", "content": "Fetch Bedroom temperature and humidity?"}]}
    #{"role": "user", "content": "What's the temperature & humidity in the bedroom?"},
    {"role": "user", "content": "What's the temperature in the bathroom?"}
    ]

response = agent.invoke({"messages": messages})

print(response["messages"][-1].content)








#print(response)