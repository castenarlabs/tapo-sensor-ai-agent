## Tapo Sensors with AI Agents
#### A Python script that can fetch Tapo Sensors values (Temperature and Humidity) and an AI Agent that can understand and respond.


## Install Necessary Packages
1. pip install -r requirements.txt

(!) The Tapo API Client connects to your hub in the local network, so you will need the script to be able to access to your local network. 
You can always expose the local network and port to a public URL. - Ngrok for example

(i) This script was tested and ran on Python v3.13 
### How to run
1. Update the script with your credentials and variables in "Environment Setup"

#### main.py
1. Navigate to the script directory and run `python main.py`
    1. The input to the AI is in the messages variable on this script. 
2. Output:
   1. ```
      $ python main.py
      The temperature in the bathroom is 17.3 degrees Celsius. 
      This is a bit cold, so you might want to turn up the heat. 
      The alarm has been rung for 2 seconds.
      ```
      
#### local-server.py

1. Navigate to the script directory and run `local-server.py`
2. Output:
   1. ```
      $ python local-server.py 
      INFO:     Started server process [14450]
      INFO:     Waiting for clearapplication startup.
      INFO:     Application startup complete.
      INFO:     Uvicorn running on http://0.0.0.0:2024 (Press CTRL+C to quit)
      ```  
3. Send in the question to the UI via Curl
    1. ```
        curl -X POST http://localhost:2024/ -H "Content-Type: application/json" -d '[
       {"role": "user", "content": "What is the temperature in the bathroom and ring the alarm for 5 seconds?"}]'
       ```
4. Output:
   1. ```
      The temperature in the bathroom is 19.0 degrees Celsius. The alarm was played for 5 seconds and stopped.
      ```