from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from tapo import ApiClient
from tapo.requests import AlarmVolume, AlarmDuration, AlarmRingtone
import os
import asyncio
from fastapi import FastAPI
import uvicorn


#Environment setup
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "$GOOGLE_API_KEY")
hub_ip = os.getenv("HUB_IP", "$hub_ip")
tapo_email = os.getenv("TAPO_EMAIL", "$tapo_email")
tapo_password = os.getenv("TAPO_PASSWORD", "$tapo_password")

model = init_chat_model("google_genai:gemini-2.5-flash-lite", temperature=0.0, max_tokens=1000)

# Define tools using @tool decorator
@tool()
def main():
    """
    Fetch temperature and humidity from Tapo sensors.
    Returns all matching sensor readings.
    """
    async def fetch_sensors():
        client = ApiClient(tapo_username=tapo_email, tapo_password=tapo_password)
        hub = await client.h100(hub_ip)
        children = await hub.get_child_device_list()

        readings = []
        for child in children:
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

@tool()
def ring_alarm(duration_seconds: int = 2):
    """
    Trigger the alarm for the specified number of seconds.
    """
    async def trigger_alarm():
        client = ApiClient(tapo_username=tapo_email, tapo_password=tapo_password)
        hub = await client.h100(hub_ip)
        await hub.play_alarm(
            AlarmRingtone.Connection1,
            AlarmVolume.Low,
            AlarmDuration.Seconds,
            seconds=duration_seconds
        )
        return f"Alarm played for {duration_seconds} seconds and stopped."

    return asyncio.run(trigger_alarm())

@tool()
def check_alarm_status():
    """
    Check alarm status and stop it if it’s ringing.
    """
    async def check_stop_alarm():
        client = ApiClient(tapo_username=tapo_email, tapo_password=tapo_password)
        hub = await client.h100(hub_ip)
        device_ring_status = await hub.get_device_info()
        ring_status = device_ring_status.in_alarm

        if ring_status:
            await asyncio.sleep(2)
            await hub.stop_alarm()
            device_ring_status = await hub.get_device_info()
            ring_status = device_ring_status.in_alarm
        return f"Alarm is {'ringing' if ring_status else 'stopped'}."

    return asyncio.run(check_stop_alarm())

# Create agent
system_prompt = (
    "You are a friendly smart home assistant that can help inform users of the temperature OR "
    "humidity of your Tapo devices. You also will trigger the alarm when explicitly asked. "
    "You shall provide a clear summary of ALL tool results when asked explicitly."
    "ALWAYS give a FINAL ANSWER summarizing ALL tools results based on what was asked."
)

agent = create_agent(
    model=model,
    tools=[main, ring_alarm, check_alarm_status],
    system_prompt=system_prompt,
)

# Create FastAPI app
api_app = FastAPI(
    title="Tapo Smart Home AI Agent",
    description="LangChain agent for Tapo sensors and alarm, exposed via LangServe",
    version="1.0.0"
)

#POST Request for FAST_API
@api_app.post("/")

async def chat(messages: list[dict]):
    langchain_messages = []
    for msg in messages:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))

    # Invoke agent
    result = await agent.ainvoke({"messages": langchain_messages})
    #Print  messages content only
    #print(result)

    content = result["messages"][-1].content
    # return result #To see full content
    return content


if __name__ == "__main__":
    uvicorn.run(api_app, host="0.0.0.0", port=2024)
