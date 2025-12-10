#!/usr/bin/env python
"""
内容生成工厂脚本
"""
import sys
import os
import argparse

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db
from agents.director import DirectorAgent
from agents.actor import ActorAgent
from agents.validator import CardValidator
from services.card_service import CardService

def run_factory(batch_size=20, domains="Java, Python, AI, History, Science, Philosophy"):
    """运行内容生成工厂"""
    print(f"🏭 Starting factory run: generating {batch_size} cards...")
    print(f"📚 Domains: {domains}\n")
    
    director = DirectorAgent()
    actor = ActorAgent()
    validator = CardValidator()
    
    # 1. Director 生成选题
    print("📋 Step 1: Director generating topics...")
    topics = director.generate_topics(count=batch_size, domains=domains)
    print(f"✓ Director generated {len(topics)} topics\n")
    
    if not topics:
        print("✗ Failed to generate topics. Check your LLM API configuration.")
        return 0
    
    # 2. Actor 逐个生成内容
    print("🎨 Step 2: Actor generating cards...")
    created_count = 0
    failed_count = 0
    
    for idx, topic_data in enumerate(topics, 1):
        try:
            print(f"[{idx}/{len(topics)}] Generating: {topic_data['topic']}")
            
            # 生成内容
            payload = actor.generate_card(topic_data)
            
            if not payload:
                print(f"  ✗ Failed to generate payload")
                failed_count += 1
                continue
            
            # 验证内容
            is_valid, errors = validator.validate_card_payload(payload)
            if not is_valid:
                print(f"  ✗ Validation failed:")
                for error in errors:
                    print(f"    - {error}")
                failed_count += 1
                continue
            
            # 清理并存入数据库
            payload = validator.sanitize_payload(payload)
            card = CardService.create_card(
                topic=topic_data['topic'],
                tags=topic_data['tags'],
                complexity=topic_data['complexity'],
                payload=payload
            )
            
            created_count += 1
            print(f"  ✓ Card created: {card.id}")
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            failed_count += 1
            db.session.rollback()
    
    print(f"\n{'='*50}")
    print(f"🎉 Factory run completed!")
    print(f"  ✓ Successfully created: {created_count}/{batch_size} cards")
    if failed_count > 0:
        print(f"  ✗ Failed: {failed_count} cards")
    print(f"{'='*50}")
    
    return created_count

def list_cards():
    """列出所有卡片"""
    with app.app_context():
        cards = CardService.get_all_cards(limit=50)
        print(f"\n📚 Total cards in database: {len(cards)}\n")
        
        for card in cards:
            print(f"ID: {card.id}")
            print(f"  Topic: {card.topic}")
            print(f"  Tags: {', '.join(card.tags)}")
            print(f"  Complexity: {'⭐' * card.complexity}")
            print(f"  Created: {card.created_at}")
            print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MindSlot Content Factory')
    parser.add_argument('--generate', type=int, metavar='N',
                      help='Generate N cards')
    parser.add_argument('--domains', type=str,
                      default='Java, Python, AI, History, Science, Philosophy',
                      help='Comma-separated list of domains')
    parser.add_argument('--list', action='store_true',
                      help='List all cards in database')
    
    args = parser.parse_args()
    
    with app.app_context():
        if args.list:
            list_cards()
        elif args.generate:
            run_factory(batch_size=args.generate, domains=args.domains)
        else:
            parser.print_help()
