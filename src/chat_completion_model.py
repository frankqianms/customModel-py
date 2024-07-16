from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from teams.ai.models.prompt_response import PromptResponse
from teams.ai.prompts.message import Message
from teams.ai.models.prompt_completion_model import PromptCompletionModel

from local_model import LocalModel

@dataclass
class ChatCompletionModelOptions:
    api_key: str
    endpoint: str
    logRequests: Optional[bool] = True

class ChatCompletionModel(PromptCompletionModel):
    def __init__(self, options: ChatCompletionModelOptions):
        self.options = options

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
            import json
            my_local_model = LocalModel()
            res = await my_local_model.generate(json.dumps({'messages': self.message_to_dict(result.output)}), template.config)
            # if you want to call an external API, you can use the following code:
            # res = self._session.post(url=self.options.endpoint, data=request_data)
            if self.options.logRequests:
                print('\nCHAT RESPONSE:')
                print('status', res.status_code)
                print('response', res.content)
        except Exception as err:
            print(err)
            raise err
        # Decode the bytes object and parse it as JSON
        decoded_content = res.content
        # Adjust the return statement to use decoded_content
        return PromptResponse[str](
            input=last,
            message=Message(
                role=decoded_content['choices'][0]['message']['role'] if decoded_content['choices'][0]['message'].get('role') else 'assistant',
                content=decoded_content['choices'][0]['message']['content'] if decoded_content['choices'][0]['message'].get('content') else ''
            ) if decoded_content.get('choices') and decoded_content['choices'][0].get('message') else None,
        )