import os
from openai import OpenAI

class LLMService:
    def __init__(self):
        # 支持 OpenAI 或 DeepSeek
        if os.getenv('DEEPSEEK_API_KEY'):
            self.client = OpenAI(
                api_key=os.getenv('DEEPSEEK_API_KEY'),
                base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
            )
            self.model = 'deepseek-chat'
        else:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.model = 'gpt-4o'
    
    def call(self, system_prompt, user_prompt, temperature=0.8, response_format=None):
        """调用 LLM API"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
