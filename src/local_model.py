# Load model directly
from flask import Flask, request
import re
from typing import Any
from transformers import AutoModelForCausalLM, AutoTokenizer

local_model_app = Flask(__name__)
        
roles = ['assistant', 'user', 'system']

class LocalModel:
    def __init__(self):
        # set your local model path
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/phi-3-mini-4k-instruct")
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-3-mini-4k-instruct")

    def process(self, prompts: str):
        basic_prompt = next((prompt['content'] for prompt in prompts if prompt['role'] == 'system'), '')
        user_input = next((prompt['content'] for prompt in reversed(prompts) if prompt['role'] == 'user'), '')
        return basic_prompt + 'Now user says: ' + user_input

    async def generate(self, prompt: str, config: Any):
        prompt = self.process(prompt)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        try:
            # generate
            generate_ids = self.model.generate(inputs.input_ids, max_length=config['max_tokens'])
            generated_text = self.tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

            content = []
            sentences = generated_text.split("\n")
            for sentence in sentences:
                # sometimes the model generates empty sentences or repeat the prompt, need to filter them out
                if prompt.replace(" ", "").lower().find(sentence.replace(" ", "").lower())!=-1 \
                        or sentence.replace(" ", "").lower().find(prompt.replace(" ", "").lower())!=-1 \
                        or sentence.strip()=='':
                    continue
                role = 'assistant'  # Default role
                modified_sentence = sentence.strip()
                # Check if the sentence contains any of the roles
                for keyword in roles:
                    pattern = r'\b' + re.escape(keyword) + r'(:\s?|\b)'
                    if re.search(pattern, modified_sentence, re.IGNORECASE):
                        role = keyword
                        modified_sentence = re.sub(pattern, '', modified_sentence, flags=re.IGNORECASE).strip()
                        break
                if modified_sentence!='':
                    content.append({'message': {'role': role, 'content': modified_sentence}})
                
            return {
                "choices": content
            }
        except Exception as e:
            print(e)
            return {"choices": [{''}]}
        
local_model = LocalModel()

@local_model_app.route('/generate', methods=['POST'])
async def handle_generate():
    data = request.json
    prompt = data.get('messages')
    config = {**{k: v for k, v in data.items() if k != 'messages'}}
    result = await local_model.generate(prompt, config)
    return result

if __name__ == '__main__':
    local_model_app.run(port=3979)