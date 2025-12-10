import json
from typing import Dict, List, Tuple

class CardValidator:
    """卡片内容验证器"""
    
    VALID_BLOCK_TYPES = ['chat_bubble', 'mermaid', 'markdown', 'code_snippet', 'quote']
    VALID_ROLES = ['roast_master', 'wise_sage', 'chaos_agent']
    VALID_STYLE_PRESETS = ['cyberpunk_terminal', 'paper_notes', 'comic_strip', 'zen_minimalist']
    
    @staticmethod
    def validate_card_payload(payload: Dict) -> Tuple[bool, List[str]]:
        """
        验证卡片 payload 格式
        返回：(是否通过, 错误列表)
        """
        errors = []
        
        # 检查必需字段
        required_fields = ['card_id', 'style_preset', 'title', 'hook_text', 'blocks']
        for field in required_fields:
            if field not in payload:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # 检查 style_preset
        if payload['style_preset'] not in CardValidator.VALID_STYLE_PRESETS:
            errors.append(f"Invalid style_preset: {payload['style_preset']}")
        
        # 检查 title 和 hook_text 长度
        if len(payload['title']) > 100:
            errors.append("Title too long (max 100 chars)")
        
        if len(payload['hook_text']) > 150:
            errors.append("Hook text too long (max 150 chars)")
        
        # 检查 blocks
        if not isinstance(payload['blocks'], list) or len(payload['blocks']) == 0:
            errors.append("Blocks must be a non-empty array")
        else:
            for idx, block in enumerate(payload['blocks']):
                block_errors = CardValidator._validate_block(block, idx)
                errors.extend(block_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_block(block: Dict, idx: int) -> List[str]:
        """验证单个 block"""
        errors = []
        
        # 检查 type 字段
        if 'type' not in block:
            errors.append(f"Block {idx}: Missing 'type' field")
            return errors
        
        if block['type'] not in CardValidator.VALID_BLOCK_TYPES:
            errors.append(f"Block {idx}: Invalid type '{block['type']}'")
        
        # 检查 content 字段
        if 'content' not in block:
            errors.append(f"Block {idx}: Missing 'content' field")
        
        # 检查特定类型的额外字段
        if block['type'] == 'chat_bubble':
            if 'role' in block and block['role'] not in CardValidator.VALID_ROLES:
                errors.append(f"Block {idx}: Invalid role '{block['role']}'")
        
        if block['type'] == 'code_snippet':
            if 'lang' not in block:
                errors.append(f"Block {idx}: code_snippet must have 'lang' field")
        
        # 检查 Mermaid 语法（简单检查）
        if block['type'] == 'mermaid':
            content = block.get('content', '')
            if 'graph' not in content.lower() and 'sequenceDiagram' not in content:
                errors.append(f"Block {idx}: Invalid Mermaid syntax")
        
        return errors
    
    @staticmethod
    def sanitize_payload(payload: Dict) -> Dict:
        """清理和规范化 payload"""
        # 移除可能的危险字符
        if 'title' in payload:
            payload['title'] = payload['title'].strip()
        
        if 'hook_text' in payload:
            payload['hook_text'] = payload['hook_text'].strip()
        
        # 确保 blocks 存在
        if 'blocks' not in payload:
            payload['blocks'] = []
        
        return payload
