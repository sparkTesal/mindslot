import json
from services.llm_service import LLMService

DIRECTOR_SYSTEM_PROMPT = """你是 MindSlot 的内容总监 (Content Director)。你的任务是为一个沉浸式学习应用生成高质量的选题清单。

你的职责：
1. 生成多样化的话题，涵盖技术、历史、科学、文化等领域
2. 为每个话题指定合适的语气 (tone) 和呈现格式 (format)
3. 确保内容既有深度又有趣味性，避免枯燥的说教

输出格式：严格的 JSON 数组，每个对象必须包含以下字段：
- topic: 话题标题 (字符串)
- tone: 语气风格 (可选值: "Excited", "Sarcastic", "Philosophical", "Playful", "Dark_Humor")
- format: 呈现格式 (可选值: "code_comparison", "rant", "story", "debate", "meme_analysis")
- complexity: 复杂度 1-5 (1=通识, 5=硬核)
- tags: 标签数组 (例如: ["Java", "Performance", "JVM"])"""

DIRECTOR_USER_PROMPT = """请生成 {count} 个卡片选题，领域包括：{domains}

要求：
1. 话题必须具体且有争议性或反常识性
2. 60% 技术话题，30% 通识话题，10% 整活/梗文化
3. 语气要多样化，避免千篇一律
4. 每个话题必须能在 2-3 分钟内消费完

直接返回 JSON 数组，不要任何额外解释。"""

class DirectorAgent:
    def __init__(self):
        self.llm = LLMService()
    
    def generate_topics(self, count=20, domains="Java, Python, AI, History, Science"):
        """生成选题清单"""
        user_prompt = DIRECTOR_USER_PROMPT.format(count=count, domains=domains)
        
        response = self.llm.call(
            system_prompt=DIRECTOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.9
        )
        
        try:
            topics = json.loads(response)
            return topics
        except json.JSONDecodeError as e:
            print(f"Failed to parse Director response: {e}")
            print(f"Raw response: {response}")
            return []
