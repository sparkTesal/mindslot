#!/usr/bin/env python
"""
创建演示卡片（无需 LLM API）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db
from models.card import Card
import uuid

demo_cards = [
    {
        "topic": "为什么 synchronized 以前很慢？",
        "tags": ["Java", "JVM", "并发"],
        "complexity": 4,
        "payload": {
            "card_id": "c-demo-001",
            "style_preset": "cyberpunk_terminal",
            "title": "为什么 synchronized 以前很慢？",
            "hook_text": "别被老黄历骗了，现在的锁比你想象的聪明。",
            "blocks": [
                {
                    "type": "chat_bubble",
                    "role": "roast_master",
                    "content": "还在背八股文说 synchronized 是重量级锁？JDK 6 的偏向锁都要笑死在常量池里了。"
                },
                {
                    "type": "mermaid",
                    "content": "graph TD\n    A[无锁] -->|线程A访问| B[偏向锁]\n    B -->|线程B竞争| C[轻量级锁 CAS]\n    C -->|自旋失败| D[重量级锁 OS Mutex]"
                },
                {
                    "type": "markdown",
                    "content": "**关键点：** 只有在`D`阶段，线程才会真正挂起进入内核态。前面的阶段都是用户态的自嗨，极快。"
                },
                {
                    "type": "code_snippet",
                    "lang": "java",
                    "content": "// Mark Word 就在这里\nObject header = new Object();\nsynchronized(header) {\n    // 偏向锁：只记录线程 ID\n    // 轻量级锁：CAS 修改栈帧\n    // 重量级锁：操作系统 Mutex\n}"
                },
                {
                    "type": "quote",
                    "content": "锁升级是单向的，但性能提升是指数级的。 —— JVM 优化指南"
                }
            ]
        }
    },
    {
        "topic": "Python 的 GIL 是什么鬼？",
        "tags": ["Python", "并发", "性能"],
        "complexity": 3,
        "payload": {
            "card_id": "c-demo-002",
            "style_preset": "zen_minimalist",
            "title": "Python 的 GIL 是什么鬼？",
            "hook_text": "为什么多核 CPU 只能跑单线程？",
            "blocks": [
                {
                    "type": "chat_bubble",
                    "role": "wise_sage",
                    "content": "GIL（Global Interpreter Lock）是 CPython 的全局解释器锁，同一时刻只允许一个线程执行 Python 字节码。"
                },
                {
                    "type": "mermaid",
                    "content": "sequenceDiagram\n    Thread1->>GIL: 请求锁\n    GIL-->>Thread1: 获得锁\n    Thread1->>CPU: 执行字节码\n    Thread2->>GIL: 请求锁\n    Note over Thread2: 等待中...\n    Thread1->>GIL: 释放锁\n    GIL-->>Thread2: 获得锁"
                },
                {
                    "type": "markdown",
                    "content": "**为什么要有 GIL？**\n\n1. 简化内存管理（引用计数不用加锁）\n2. C 扩展更容易编写\n3. 历史遗留问题"
                },
                {
                    "type": "code_snippet",
                    "lang": "python",
                    "content": "# 多线程无法利用多核\nimport threading\n\ndef cpu_bound():\n    return sum(range(10**7))\n\nthreads = [threading.Thread(target=cpu_bound) for _ in range(4)]\n[t.start() for t in threads]\n[t.join() for t in threads]\n# ⚠️ 性能反而更差！"
                },
                {
                    "type": "markdown",
                    "content": "**解决方案：**\n- CPU 密集型：用 `multiprocessing`\n- I/O 密集型：用 `asyncio` 或 `threading`\n- 性能关键：用 Cython 或 Rust"
                }
            ]
        }
    },
    {
        "topic": "罗马帝国灭亡的真正原因",
        "tags": ["历史", "罗马", "科学"],
        "complexity": 2,
        "payload": {
            "card_id": "c-demo-003",
            "style_preset": "paper_notes",
            "title": "罗马帝国灭亡：铅中毒假说",
            "hook_text": "用铅做水管和酒杯，罗马人慢性自杀了 500 年？",
            "blocks": [
                {
                    "type": "chat_bubble",
                    "role": "chaos_agent",
                    "content": "罗马人超爱铅：水管、酒杯、化妆品、甚至葡萄酒增甜剂都用铅。考古学家在罗马贵族骨骼里发现了超标 100 倍的铅含量。"
                },
                {
                    "type": "markdown",
                    "content": "**铅中毒的症状：**\n- 智力下降\n- 暴躁易怒\n- 不孕不育\n- 肌肉无力"
                },
                {
                    "type": "mermaid",
                    "content": "graph LR\n    A[铅水管] --> B[饮用水污染]\n    C[铅酒杯] --> D[贵族中毒]\n    B --> E[人口下降]\n    D --> E\n    E --> F[帝国衰落]"
                },
                {
                    "type": "quote",
                    "content": "罗马不是一天建成的，但可能是被铅毁掉的。 —— 考古学家推测"
                },
                {
                    "type": "markdown",
                    "content": "**争议：** 有学者认为铅中毒被夸大了，真正原因是政治腐败、军事压力和经济危机。但不管怎样，铅水管确实不是好主意。"
                }
            ]
        }
    },
    {
        "topic": "为什么删库要跑路？",
        "tags": ["数据库", "梗", "运维"],
        "complexity": 1,
        "payload": {
            "card_id": "c-demo-004",
            "style_preset": "comic_strip",
            "title": "rm -rf / 的艺术",
            "hook_text": "史上最贵的一条命令。",
            "blocks": [
                {
                    "type": "chat_bubble",
                    "role": "roast_master",
                    "content": "2017 年，某云服务商的工程师手抖执行了 `rm -rf` 删掉了生产数据库。损失：数百万美元 + 公司倒闭。"
                },
                {
                    "type": "code_snippet",
                    "lang": "bash",
                    "content": "# 史上最危险的命令\nrm -rf /\n# -r: 递归删除\n# -f: 强制删除，无需确认\n# /: 根目录\n\n# 后果：系统完全崩溃"
                },
                {
                    "type": "markdown",
                    "content": "**真实案例：**\n1. GitLab 删库事件（2017）：300GB 数据丢失\n2. Pixar 差点删掉《玩具总动员 2》\n3. 某程序员删了公司代码仓库后跑路"
                },
                {
                    "type": "mermaid",
                    "content": "graph TD\n    A[手抖执行 rm -rf] --> B{有备份吗？}\n    B -->|有| C[恢复数据，罚款]\n    B -->|没有| D[公司倒闭]\n    D --> E[跑路]"
                },
                {
                    "type": "quote",
                    "content": "没有备份，就没有发言权。 —— 运维铁律"
                }
            ]
        }
    },
    {
        "topic": "量子计算能破解所有密码吗？",
        "tags": ["量子计算", "密码学", "科技"],
        "complexity": 5,
        "payload": {
            "card_id": "c-demo-005",
            "style_preset": "cyberpunk_terminal",
            "title": "量子计算：密码学的终结者？",
            "hook_text": "Shor 算法：RSA 的噩梦。",
            "blocks": [
                {
                    "type": "chat_bubble",
                    "role": "wise_sage",
                    "content": "量子计算利用叠加态和纠缠，可以在多项式时间内分解大整数，这意味着 RSA、ECC 等公钥密码系统将被破解。"
                },
                {
                    "type": "mermaid",
                    "content": "graph TD\n    A[经典计算] -->|指数时间| B[分解大整数]\n    C[量子计算 Shor] -->|多项式时间| B\n    B --> D[破解 RSA]"
                },
                {
                    "type": "code_snippet",
                    "lang": "python",
                    "content": "# Shor 算法简化版（伪代码）\ndef shor_algorithm(N):\n    # 1. 随机选择 a < N\n    # 2. 量子计算找到周期 r\n    # 3. 如果 r 是偶数，计算 gcd(a^(r/2) ± 1, N)\n    # 4. 得到 N 的因子\n    return factors"
                },
                {
                    "type": "markdown",
                    "content": "**现实情况：**\n- 当前最大的量子计算机：~1000 量子比特\n- 破解 RSA-2048 需要：~2000 万量子比特\n- 预计时间：10-20 年后"
                },
                {
                    "type": "markdown",
                    "content": "**应对方案：**\n1. **后量子密码学**：基于格、哈希、多变量方程\n2. **量子密钥分发（QKD）**：利用量子力学的不可克隆定理\n3. NIST 已经发布了后量子密码标准"
                },
                {
                    "type": "quote",
                    "content": "量子计算既是密码学的威胁，也是密码学的未来。 —— Peter Shor"
                }
            ]
        }
    }
]

def create_demo_cards():
    """创建演示卡片"""
    with app.app_context():
        print("🎨 Creating demo cards...")
        
        for card_data in demo_cards:
            card = Card(
                topic=card_data["topic"],
                tags=card_data["tags"],
                complexity=card_data["complexity"],
                payload=card_data["payload"]
            )
            db.session.add(card)
        
        db.session.commit()
        print(f"✅ Successfully created {len(demo_cards)} demo cards!")
        
        # 列出所有卡片
        cards = Card.query.all()
        print(f"\n📚 Total cards in database: {len(cards)}\n")
        for card in cards:
            print(f"  • {card.topic} ({', '.join(card.tags)}) - {'⭐' * card.complexity}")

if __name__ == '__main__':
    create_demo_cards()
