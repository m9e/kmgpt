import os
import pwd
from Processors import ChatProcessor
import pyperclip

# Get the current user's full name and home directory
user_info = pwd.getpwuid(os.getuid())
full_name = user_info.pw_gecos.split(',')[0]
home_dir = user_info.pw_dir

# Get the contents of the system clipboard
clipboard_data = pyperclip.paste()

# default empty string
reply = ''

whoami = ("For this request, write in the voice of an experienced CTO, "
          "prefer concise language, avoid unnecessary words, but do add context where it may be needed.\n\n")

writing_prompts = {
    "SuccinctAnecdote": "Take this text, and write a short and succint anecdote, referencing a historical, scientific, or other cultural detail. Try to be brief, but don't leave out interesting details for brevity\n\n",
   	"Expand": "Expand the following text. Use concise language, an academic but enthusiastic tone, avoid unnecessary words.\n\n",
   	"AS-IS": "",  # eg, the whole prompt is in the clipboard
    "Educate": "Respond to the following conversationally in that voice, intending to primarily inform, but amuse and encourage as appropriate for the context: \n\n"
}

twostage_prompts = {
    "Email Response": f"This text represents an email, or a chain of emails. There is probably a name, date and time, and the body. There may be extraneous characters from signatures. For context, my previous emails in the thread are labelled as from {full_name}. You will compose a reply from me, in context, but in particular to the last message. Do not use a salutation, and generate a body only with no sign-off. Otherwise, use formatting, tone, style, and vocabulary appropriate for a business response, and the gist of the reply should be: ",
    "Ad Hoc": f"",
}

code_prompts = {
	"Code From Description": "Please write code from the below descripiton. Default to python if the description does not specify a language. Answer ONLY with code without preamble, or formatting. If you have explanatory comments, print them as code comments prefixed with # or the appropriate symbol for the language.",
	"Explain Code": "Explain this code, and output as a single code comment; do not answer with code",
    "Annotate Code": "Rewrite this code with explanatory comments that explains the code",
    "Sumalysis": "Summarize the following text as succintly as possible, while not losing important context. Then, list key concepts and entities from the text (significant people, concepts, events, etc). List each concept or entity. For each concept/entity, write a paragraph of background information WITHOUT drawing on the text for that background info; use the text only to determine the list of concepts, then provide background information independently from the text.",
	"Summarize": "Summarize this text as succintly as possible, while not losing important context\n\n",
	"Analysis": "Analyze the following content. Do not summarize, but Try to detect factual errors, logical fallacies, omissions of important context. Then also provide a rating on a scale from 1-100, with 100 being the highest, of each of these: the vocabulary range of the author; the likelihood that English is their first language; their emotional sentiment at the time of writing. In providing the numbers, do the best you can but do not provide any explanation; place the ratings each on a new line.\n",
	"Research": "Analyze the following content. Detect key concepts and entities. List each concept or entity, and for each concept or entity, provide a paragraph of background information. DO NOT draw the background information from the text provided, use the text only to determine the list of concepts. For example, if the text were to discuss Abraham Lincoln, you would write 1-4 sentences to form the most concise microbiography of Lincoln you could; if it mentioned Petit Palais, you would write 1-4 sentences to describe the Petit Palais museum in France and include its location, year of founding, typical exhibits, normal hours. Be as concise as possible.\n",
}

prompt_files = {
    'prompt': os.path.join(home_dir, '.kmgpt'),
    'reply': os.path.join(home_dir, '.kmgpt_reply'),
    'log': os.path.join(home_dir, 'code/kmgpt/gpt.log')
}

# Ensure log file dir exists and use homedir if not
log_dir = os.path.join(home_dir, 'code/kmgpt')
log_file = os.path.join(log_dir, 'gpt.log')

# Check if the log directory exists, if not, use '~/gpt.log' instead
if not os.path.exists(log_dir):
    log_file = os.path.join(home_dir, 'gpt.log')

prompt_files['log'] = log_file


def read_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read().strip()
    return ''


def build_final_prompt(prompt, reply, clipboard_data):
    final_prompt = ''
    if prompt in twostage_prompts:
        if prompt == 'Ad Hoc':
            final_prompt = twostage_prompts[prompt] + \
                reply if reply else '' + "\n\n" + clipboard_data
        else:
            final_prompt = whoami + \
                twostage_prompts[prompt] + \
                (reply if reply else '') + "\n\n" + clipboard_data
    elif prompt in code_prompts:
        final_prompt = code_prompts[prompt] + "\n\n" + clipboard_data
    elif prompt in writing_prompts:
        final_prompt = whoami + \
            writing_prompts[prompt] + "\n\n" + clipboard_data
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
    f.write('Tokens: ' + str(chat_processor.available_tokens) +
            "\n" + prompt + response)
