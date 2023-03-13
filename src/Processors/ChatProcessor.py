import openai
import os
import tiktoken

openai.api_key = os.environ["OPENAI_API_KEY"] # Set your API key as an environment variable

class ChatProcessor:
    
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.available_tokens = 4096
        self.messages = [
              {"role": "system", "content": "You are a helpful assistant. Answer as concisely as possible."},
            ]
    
    def generate_response(self, prompt):
        self.messages.append({"role": "user", "content": prompt})
        self.last_response = None
        self.last_response_reason = None
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        token_count = 1
        for m in self.messages:
          token_count += 4
          for k, v in m.items():
            token_count += len(encoding.encode(v))
            if k == "name":
              token_count += -1
        token_count += 2
        self.available_tokens = 4096 - token_count

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            max_tokens=self.available_tokens
        )

        self.last_response = response['choices'][0]['message']['content']
        self.last_response_reason = response['choices'][0]['finish_reason']
        self.messages.append({"role": "assistant", "content": self.last_response})

        return self.last_response

