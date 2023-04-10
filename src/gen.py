import os
from Processors import ChatProcessor
import pyperclip

my_name = 'Matt Wallace'

# Get the contents of the system clipboard
clipboard_data = pyperclip.paste()

# default empty string
reply = ''

whoami = ("For this request, write in the voice of an experienced CTO, "
          "prefer concise language, avoid unnecessary words, but do add context where it may be needed.\n\n")

prompt_files = {
    'prompt': '/Users/matt/.kmgpt',
    'reply': '/Users/matt/.kmgpt_reply',
    'log': '/Users/matt/code/kmgpt/gpt.log'
}

def read_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read().strip()
    return ''

def build_final_prompt(prompt, reply, clipboard_data):
    final_prompt = ''
    if prompt in twostage_prompts:
        if prompt == 'Ad Hoc':
            final_prompt = twostage_prompts[prompt] + reply if reply else '' + "\n\n" + clipboard_data
        else:
            final_prompt = whoami + twostage_prompts[prompt] + (reply if reply else '') + "\n\n" + clipboard_data
    elif prompt in code_prompts:
        final_prompt = code_prompts[prompt] + "\n\n" + clipboard_data
    elif prompt in writing_prompts:
        final_prompt = whoami + writing_prompts[prompt] + "\n\n" + clipboard_data
    return final_prompt

# Read prompt and reply files
prompt = read_file(prompt_files['prompt'])
reply = read_file(prompt_files['reply'])

# Build final prompt
final_prompt = build_final_prompt(prompt, reply, clipboard_data)

# Generate response from text using ChatProcessor
chat_processor = ChatProcessor()
response = chat_processor.generate_response(final_prompt)
print(f"Response to prompt {final_prompt} was:\n\n{response}")

if prompt in code_prompts:
    response = response.strip('`')

# Save in clipboard
pyperclip.copy(response)

# Log the response
with open(prompt_files['log'], 'a') as f:
    f.write('Tokens: ' + str(chat_processor.available_tokens) + "\n" + prompt + response)
