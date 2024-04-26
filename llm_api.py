import requests
import json

class llm:
    def __init__(self):
        self._URL = "https://api.awanllm.com/v1/chat/completions"
        self._MODEL_NAME = 'Meta-Llama-3-8B-Instruct'
        self._API_KEY = ''
        try:
          with open('llm_api.txt', 'r') as file:
              self._API_KEY = file.read().replace('\n','')
        except:
            raise Exception("You need to provide the LLM API key in the llm_api.txt file.")
        
        
class llmSummarizer(llm):
    def summarize(self, text:str)->str:
        # Header of the API request
        headers = {
          'Content-Type': 'application/json',
          'Authorization': f"Bearer {self._API_KEY}"
        }
        # Payload of the API request
        payload = json.dumps({
                      "model": f"{self._MODEL_NAME}",
                      "messages": [
                        {
                          "role": "expert writer",
                          "content": f"can you summarize the following text: {text}"
                        }
                      ]
                    })
        # Response of the API request 
        response = requests.request("POST", self._URL, headers=headers, data=payload)
        # Return the content of the response
        return str(json.loads(response.text)['choices'][0]['message']['content']).replace('\n',' ')
    
    
class llmSeoOptimizer(llm):
    def optimize(self, text:str)->str:
        # Header of the API request
        headers = {
          'Content-Type': 'application/json',
          'Authorization': f"Bearer {self._API_KEY}"
        }
        # Payload of the API request
        payload = json.dumps({
                      "model": f"{self._MODEL_NAME}",
                      "messages": [
                        {
                          "role": "expert digital marketer and SEO optimizer",
                          "content": f"can you optimize for SEO the following webpage: {text}"
                        }
                      ]
                    })
        # Response of the API request 
        response = requests.request("POST", self._URL, headers=headers, data=payload)
        # Return the content of the response
        return str(json.loads(response.text)['choices'][0]['message']['content']).replace('\n',' ')