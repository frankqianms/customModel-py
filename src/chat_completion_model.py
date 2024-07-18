from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

import requests
from teams.ai.models.prompt_response import PromptResponse
from teams.ai.prompts.message import Message
from teams.ai.models.prompt_completion_model import PromptCompletionModel

from local_model_server import LocalModel

@dataclass
class ChatCompletionModelOptions:
    api_key: str
    endpoint: str
    logRequests: Optional[bool] = True

class ChatCompletionModel(PromptCompletionModel):
    def __init__(self, options: ChatCompletionModelOptions):
        self.options = options
        # Create client
        self._session = requests.Session()
        self._session.headers.update({
            'Authorization': f"Bearer {options.api_key}",
            'Content-Type': 'application/json',
            # 'User-Agent': '@microsoft/teams-ai-v1'
        })
        self._session.verify = True  # Ensures SSL verification is enabled
        # Custom validation for status codes
        self._session.hooks['response'].append(self._validate_status)
    
    def _validate_status(self, r, *args, **kwargs):
        if not (r.status_code < 400 or r.status_code == 429):
            r.raise_for_status()

    def message_to_dict(self, messages):
        # Implement the conversion logic based on the structure of the Message class
        result = []
        for message in messages:
            result.append({
                'content': message.content,
                'role': message.role,
                # Add other relevant fields
            })
        return result
    
    async def complete_prompt(self, context, memory, functions, tokenizer, template) -> Dict[str, Any]:
        max_input_tokens = template.config.completion.max_input_tokens
        result = await template.prompt.render_as_messages(context, memory, functions, tokenizer, max_input_tokens)
        if result.too_long:
            return {
                'status': 'too_long',
                'error': 'The generated prompt length was too long'
            }
        last: Optional[Dict[str, Any]] = result.output[-1] if result.output and result.output[-1].role == 'user' else None
        res = None
        if self.options.logRequests:
            print('\nCHAT PROMPT:')
            print(self.message_to_dict(result.output))
        try:
            # call the local llm to generate the response
            completion_config_dict = asdict(template.config.completion)
            import json
            request_data = json.dumps({
                'messages': self.message_to_dict(result.output),  # Assuming message_to_dict properly serializes each message
                **completion_config_dict
            })
            res = self._session.post(url=self.options.endpoint, data=request_data)
            if self.options.logRequests:
                print('\nCHAT RESPONSE:')
                print('status', res.status_code)
                print('response', res.content)
        except Exception as err:
            print(err)
            raise err
        # Decode the bytes object and parse it as JSON
        decoded_content = json.loads(res.content.decode('utf-8'))
        # Adjust the return statement to use decoded_content
        return PromptResponse[str](
            input=last,
            message=Message(
                role=decoded_content['choices'][0]['message']['role'] if decoded_content['choices'][0]['message'].get('role') else 'assistant',
                content=decoded_content['choices'][0]['message']['content'] if decoded_content['choices'][0]['message'].get('content') else ''
            ) if decoded_content.get('choices') and decoded_content['choices'][0].get('message') else None
        )