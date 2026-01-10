import os
from openai import OpenAI

class LLMService:
    def __init__(self):
        self.client = None
        self.model = None
        self.available = False
        
        # 支持 OpenAI 或 DeepSeek
        try:
            if os.getenv('DEEPSEEK_API_KEY'):
                self.client = OpenAI(
                    api_key=os.getenv('DEEPSEEK_API_KEY'),
                    base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
                )
                self.model = 'deepseek-chat'
                self.available = True
                print("[LLMService] Using DeepSeek API")
            elif os.getenv('OPENAI_API_KEY'):
                self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                self.model = 'gpt-4o'
                self.available = True
                print("[LLMService] Using OpenAI API")
            else:
                print("[LLMService] No API key configured. Set OPENAI_API_KEY or DEEPSEEK_API_KEY environment variable.")
        except Exception as e:
            print(f"[LLMService] Failed to initialize: {e}")
    
    def is_available(self) -> bool:
        """检查 LLM 服务是否可用"""
        return self.available and self.client is not None
    
    def call(self, system_prompt, user_prompt, temperature=0.8, response_format=None):
        """调用 LLM API"""
        if not self.is_available():
            raise RuntimeError("LLM service not available. Please configure API key.")
        
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
