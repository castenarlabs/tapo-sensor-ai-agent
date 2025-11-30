from tapo import ApiClient
import asyncio
from langchain.agents import create_agent
import os
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from tapo.requests import AlarmVolume, AlarmDuration, AlarmRingtone

os.environ["GOOGLE_API_KEY"] = "$GOOGLE_API_KEY"
model = init_chat_model("google_genai:gemini-2.5-flash-lite", temperature=0.0, max_tokens=500)
hub_ip = "$hub_ip"
tapo_email = "$tapo_email"
tapo_password = "$tapo_password"


@tool()
def main():
    """
    There is a Hub which is connected to multiple sensors. Fetch temperature and humidity from Tapo sensors.
    Returns all matching sensor readings or full list if "all".
    You should also advise on the 'humidity' OR 'temperature' levels, if asked specifically.
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
        ''' #DEBUG
        result = "\n".join(readings)
        print(f"Tool Returning: '{result}'")
        return result or "No sensor data available"
        '''
    return asyncio.run(fetch_sensors())
    ''' #DEBUG
    result = asyncio.run(fetch_sensors())
    print(f"FINAL Returning: '{result}'")
    return result
    '''

@tool()
def ring_alarm(duration_seconds: int = 2):
    """
    You will trigger the alarm  (E.g. Play Alarm, Ring Alarm, Play sounds) when you are EXPLICITLY asked to play alarm.
    You will NOT trigger the alarm if you are not asked to play alarm.
    When asked to trigger the alarm, play the alarm for the specified number of seconds.

    Args:
        duration_seconds: How long to play the alarm (default: 2 seconds)
    """
    async def trigger_alarm():
        client = ApiClient(tapo_username=tapo_email, tapo_password=tapo_password)
        hub = await client.h100(hub_ip)
        await hub.play_alarm(AlarmRingtone.Connection1, AlarmVolume.Low, AlarmDuration.Seconds, seconds=duration_seconds)
        # print(play)

        return f"Alarm played for {duration_seconds} seconds and stopped."
    return asyncio.run(trigger_alarm())


@tool()
def check_alarm_status():
    """
    You will check the status of the alarm only when explicitly asked.
    You will not check the status of the alarm if you are not asked to check the status alarm.
    You will not trigger the alarm.
    You can STOP the alarm when explicitly asked.
    """
    async def check_stop_alarm():
        client = ApiClient(tapo_username=tapo_email, tapo_password=tapo_password)
        hub = await client.h100(hub_ip)

        device_ring_status = await hub.get_device_info()
        ring_status = device_ring_status.in_alarm
        #print("Is device ringing:", ring_status)
        if ring_status:  # True
            await asyncio.sleep(2)
            await hub.stop_alarm()
            device_ring_status = await hub.get_device_info()
            ring_status = device_ring_status.in_alarm
            #print("Is device ringing after STOP Command", ring_status)
        return ring_status
    asyncio.run(check_stop_alarm())


#'''
system_prompt=(
    "You are a friendly smart home assistant that can help inform users of the temperature OR "
               "humidity of your Tapo devices. You also will trigger the alarm when explicitly asked. "
               "ALWAYS give a FINAL ANSWER summarizing ALL tools results.")
agent = create_agent(
    model= model,
    tools=[main, check_alarm_status, ring_alarm],
    system_prompt= system_prompt
)
#'''

#asyncio.run(main())
#Question to the AI
messages = [
    {"role": "system", "content": system_prompt},
    #{"role": "user", "content": "What is the temperature in the bathroom? Is it too cold? What do you think?"}
    {"role": "user", "content": "What is the temperature in the bathroom? Is it too cold? What do you think? "
                                "Can you also ring the alarm"}
    #{'role': "user", "content": "What is the status of the alarm?"},
    #{'role': "user", "content": "Ring the alarm for 2 seconds"},
    #{'role': "user", "content": "Stop the alarm"}
    ]

response = agent.invoke({"messages": messages})
print(response["messages"][-1].content)

#print(response)