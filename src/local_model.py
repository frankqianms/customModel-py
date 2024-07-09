# Load model directly
import json
import re
from types import SimpleNamespace
from typing import Any
from transformers import AutoTokenizer, Phi3ForCausalLM
        
roles = ['assistant', 'user', 'system']

class LocalModel:
    def __init__(self):
        # set your local model path
        self.model = Phi3ForCausalLM.from_pretrained("microsoft/phi-3-mini-4k-instruct")
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-3-mini-4k-instruct")

    def process(self, prompts: str):
        basic_prompt = next((prompt['content'] for prompt in json.loads(prompts).get('messages', []) if prompt['role'] == 'system'), '')
        user_input = next((prompt['content'] for prompt in reversed(json.loads(prompts).get('messages', [])) if prompt['role'] == 'user'), '')
        return basic_prompt + 'Now user says: ' + user_input

    async def generate(self, prompt: str, config: Any):
        prompt = self.process(prompt)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        try:
            # generate
            generate_ids = self.model.generate(inputs.input_ids, max_length=config.completion.max_tokens)
            generated_text = self.tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

            content = []
            sentences = generated_text.split("\n")
            for sentence in sentences:
                if prompt.find(sentence.strip())!=-1 or sentence.strip()=='':
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
                
            return SimpleNamespace(**{
                'status_code': 'success',
                'content': {'choices': content}
            })
        except Exception as e:
            return SimpleNamespace(**{
                'status_code': 'error',
                'content': {
                    'role': 'assistant',
                    'content': ''
                }
            })