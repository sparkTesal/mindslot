import os
from openai import OpenAI

class LLMService:
    def __init__(self):
        self.client = None
        self.model = None
        self.available = False
        
        # 支持 OpenAI 兼容 API（DeepSeek、ChatAnywhere 等）
        try:
            api_key = os.getenv('LLM_API_KEY') or os.getenv('DEEPSEEK_API_KEY') or os.getenv('OPENAI_API_KEY')
            base_url = os.getenv('LLM_BASE_URL') or os.getenv('DEEPSEEK_BASE_URL')
            model = os.getenv('LLM_MODEL')
            
            if api_key:
                if base_url:
                    # 使用自定义 API（DeepSeek、ChatAnywhere 等）
                    self.client = OpenAI(api_key=api_key, base_url=base_url)
                    self.model = model or 'deepseek-chat'
                    print(f"[LLMService] Using custom API: {base_url}, model: {self.model}")
                else:
                    # 使用 OpenAI 官方 API
                    self.client = OpenAI(api_key=api_key)
                    self.model = model or 'gpt-4o'
                    print(f"[LLMService] Using OpenAI API, model: {self.model}")
                self.available = True
            else:
                print("[LLMService] No API key configured. Set LLM_API_KEY environment variable.")
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
