## Install Necessary Packages
1. pip install -r requirements.txt

(!) The Tapo API Client connects to your local hub, so you will need the script to run in your local network. 
However, you can always export the local network and port to a public URL.

### How to run
 
#### main.py
1. Navigate to the script directory and run `python main.py`
2. Output:
   1. ```
      LangChainAI % python main.py
      The temperature in the bathroom is 17.3 degrees Celsius. 
      This is a bit cold, so you might want to turn up the heat. 
      The alarm has been rung for 2 seconds.
      ```
      
#### local-server.py

1. Navigate to the script directory and run `local-server.py`
2. Output:
   1. ```
      LangChainAI % python local-server.py 
      INFO:     Started server process [14450]
      INFO:     Waiting for application startup.
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