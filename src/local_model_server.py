from aiohttp import web
import re
from typing import Any
from transformers import AutoModelForCausalLM, AutoTokenizer, Phi3ForCausalLM

roles = ['assistant', 'user', 'system']

class LocalModel:
    def __init__(self):
        self.model = Phi3ForCausalLM.from_pretrained("microsoft/phi-3-mini-4k-instruct")
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-3-mini-4k-instruct")

    def process(self, prompts: str):
        basic_prompt = next((prompt['content'] for prompt in prompts if prompt['role'] == 'system'), '')
        user_input = next((prompt['content'] for prompt in reversed(prompts) if prompt['role'] == 'user'), '')
        return basic_prompt + 'Now user says: ' + user_input

    async def generate(self, prompt: str, config: Any):
        prompt = self.process(prompt)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        try:
            generate_ids = self.model.generate(inputs.input_ids, do_sample=True, max_length=config['max_tokens'], temperature=config['temperature'], top_p=config['top_p'])
            generated_text = self.tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

            # Model will generate multiple sentences, we need to split them and assign roles. Only return the sentences that are not in the prompt
            content = []
            sentences = generated_text.split("\n\n")
            for sentence in sentences:
                if prompt.replace(" ", "").lower().find(sentence.replace(" ", "").lower())!=-1 \
                        or sentence.replace(" ", "").lower().find(prompt.replace(" ", "").lower())!=-1 \
                        or sentence.strip()=='':
                    continue
                role = 'assistant'
                modified_sentence = sentence.strip()
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

async def handle_generate(request):
    data = await request.json()
    prompt = data.get('messages')
    config = {**{k: v for k, v in data.items() if k != 'messages'}}
    result = await local_model.generate(prompt, config)
    return web.json_response(result)

app = web.Application()
app.add_routes([web.post('/generate', handle_generate)])

if __name__ == '__main__':
    web.run_app(app, port=3979)