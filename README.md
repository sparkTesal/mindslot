# MindSlot 文档索引

本文档目录包含了 MindSlot 项目的所有文档，按类别组织以便查找。

## 📚 文档结构

```
docs/
├── guides/          # 项目指南文档
├── design/          # 设计文档
├── development/     # 开发文档
└── reports/         # 报告文档
```

---

## 📖 文档分类

### 📘 项目指南 (guides/)

项目使用指南和说明文档。

| 文档 | 说明 | 用途 |
|------|------|------|
| [README.md](guides/README.md) | 项目主文档 | 项目介绍、技术栈、完整代码实现、API 文档 |
| [QUICKSTART.md](guides/QUICKSTART.md) | 快速启动指南 | 5 步快速启动教程，适合新手 |
| [PROJECT_STRUCTURE.md](guides/PROJECT_STRUCTURE.md) | 项目结构说明 | 代码组织结构、数据流、扩展点 |

**推荐阅读顺序**：
1. 新用户 → 先看 `QUICKSTART.md`
2. 了解项目 → 阅读 `README.md`
3. 开发扩展 → 参考 `PROJECT_STRUCTURE.md`

---

### 🎨 设计文档 (design/)

产品设计和架构设计文档。

| 文档 | 说明 | 用途 |
|------|------|------|
| [design.md](design/design.md) | MVP 设计文档 | 系统架构、技术栈、数据模型、开发路线图 |
| [Project MindSlot 核心理念与设计纲领.md](design/Project%20MindSlot%20核心理念与设计纲领.md) | 核心理念文档 | 产品愿景、心理学机制、内容策略、推荐系统 |

**适用场景**：
- 理解产品设计思路
- 了解架构决策
- 规划新功能

---

### 💻 开发文档 (development/)

开发相关的技术文档。

| 文档 | 说明 | 用途 |
|------|------|------|
| [prompts.md](development/prompts.md) | LLM 提示词库 | 所有 Agent 的 Prompt 模板，用于内容生成 |
| [FILES_CREATED.md](development/FILES_CREATED.md) | 文件清单 | 项目文件列表和说明 |

**适用场景**：
- 调整 LLM 生成内容风格 → 修改 `prompts.md`
- 了解项目文件组织 → 查看 `FILES_CREATED.md`

---

### 📊 报告文档 (reports/)

项目运行和测试报告。

| 文档 | 说明 | 用途 |
|------|------|------|
| [DEMO_REPORT.md](reports/DEMO_REPORT.md) | 演示报告 | 项目运行演示的详细报告 |
| [TEST_RESULTS.md](reports/TEST_RESULTS.md) | 测试结果 | 环境配置、API 测试结果 |
| [SUMMARY.md](reports/SUMMARY.md) | 项目总结 | 项目完成情况总结 |
| [运行成功.md](reports/运行成功.md) | 运行成功报告 | 项目搭建和运行成功的确认报告 |

**适用场景**：
- 验证项目是否正常运行
- 查看测试结果
- 了解项目完成情况

---

## 🚀 快速导航

### 我想...

- **快速开始使用项目** → [QUICKSTART.md](guides/QUICKSTART.md)
- **了解项目整体架构** → [design.md](design/design.md)
- **查看完整代码实现** → [README.md](guides/README.md)
- **调整内容生成风格** → [prompts.md](development/prompts.md)
- **了解项目文件结构** → [PROJECT_STRUCTURE.md](guides/PROJECT_STRUCTURE.md)
- **理解产品设计理念** → [Project MindSlot 核心理念与设计纲领.md](design/Project%20MindSlot%20核心理念与设计纲领.md)
- **查看测试结果** → [TEST_RESULTS.md](reports/TEST_RESULTS.md)

---

## 📝 文档维护

文档按以下原则组织：

1. **guides/** - 面向用户和开发者的使用指南
2. **design/** - 面向产品和技术决策者的设计文档
3. **development/** - 面向开发者的技术文档
4. **reports/** - 项目执行过程中的报告和记录

---

**最后更新**: 2025-01-10  
**文档版本**: v1.0
