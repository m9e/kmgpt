import openai
import json
import os
import tiktoken

openai.api_key = os.environ["OPENAI_API_KEY"] # Set your API key as an environment variable
# token count where we begin to distill interactions
#TOKEN_THRESHOLD = 2500
TOKEN_THRESHOLD = 100

# token count under which we don't distill a given message
#MSG_THRESHOLD = 100
MSG_THRESHOLD = 30

class ChatProcessor:
    
    def __init__(self, model="gpt-3.5-turbo", temperature=0.0):
        self.model = model
        self.temperature = temperature
        self.available_tokens = 4096

        # does not affect manual calls to reduce()
        self.reduction_enabled = False

        self.multi = False
        self.reducer_messages = None
        self.reducer_prompt = f"The text below is a message I received from ChatGPT in another chat. I want to use it in the chat history. I want to be able to send this text back to ChatGPT, but I want to minimize the number of tokens. Please distill this message into the smallest possible form that ChatGPT would interpret in a syntactically and semantically identical way. It will not be human read, and so any format that minimizes the number of tokens is acceptable. If it lowers the number of tokens, feel free to remove punctuation, new lines, articles of speech and anything else that does not impact the ability of ChatGPT to interpret the distilled version identically. The message: "
        self.start_messages = [
              {"role": "system", "content": "You are a helpful assistant. Answer as concisely as possible."},
            ]
        self.messages = self.start_messages

    def strtokens(self, text):
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return 4 + len(encoding.encode(text))

    def tokens(self, messages):
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        token_count = 1
        for m in messages:
          token_count += 4
          for k, v in m.items():
            token_count += self.strtokens(v)
            if k == "name":
              token_count += -1
        token_count += 2
        return token_count

    def reduce(self):
      token_count = self.tokens(self.messages)
      if token_count > TOKEN_THRESHOLD:
          print(f"token count of {token_count} exceeds {TOKEN_THRESHOLD}, must reduce")
          # Save the introduction
          new_messages = [self.start_messages[0]]
  
          # Message distiller block
          for m in self.messages[1:]:
              mtokens = 0
              for k, v in m.items():
                  mtokens += self.strtokens(v)
                  if k == "name":
                      mtokens -= 1
  
              if mtokens > MSG_THRESHOLD:
                  self.reducer_messages = [
                      {"role": "system", "content": "You distill text to optimize token counts. Avoid losing meaningful context while distilling."},
                  ]
                  message_str = "\n\n".join([f"{k}: {v}" for k, v in m.items()])
                  self.reducer_messages.append({"role": "user", "content": self.reducer_prompt + "\n\n" + message_str})
  
                  tc = self.tokens(self.reducer_messages)
                  response = openai.ChatCompletion.create(
                      temperature=self.temperature,
                      model=self.model,
                      messages=self.reducer_messages,
                      max_tokens=self.available_tokens
                  )
                  self.last_response = response['choices'][0]['message']['content']
                  new_messages.append({"role": m["role"], "content": self.last_response})
              else:
                  new_messages.append(m)

          print("Distilled\n%s\n\nto\n\n%s" % (str(self.messages), str(new_messages)))

          print("Reduced %d tokens to %d" % (token_count, self.tokens(new_messages)))
  
          self.messages = new_messages

               
      
    def generate_response(self, prompt):
        self.messages.append({"role": "user", "content": prompt})
        self.last_response = None
        self.last_response_reason = None

        if self.reduction_enabled:
          self.reduce()

        token_count = self.tokens(self.messages)

        response = openai.ChatCompletion.create(
            temperature=self.temperature,
            model=self.model,
            messages=self.messages,
            max_tokens=(4096 - token_count)
        )

        self.last_response = response['choices'][0]['message']['content']
        self.last_response_reason = response['choices'][0]['finish_reason']
        self.messages.append({"role": "assistant", "content": self.last_response})
        token_count = self.tokens(self.messages)
        self.available_tokens = 4096 - token_count

        return self.last_response


    def dump_state(self):
      with open('state.json', 'w') as f:
        f.write(json.dumps(self.messages))

    def restore_state(self):
      try:
        with open('state.json', 'r') as f:
          data = f.read()
          self.messages = json.loads(data)
      except Exception as e:
        print(f"Exception occurred restoring state: {str(e)}")



