# 简历优化助手 - Agent系统技术文档 v7.0

## 项目概述

**核心架构**: 2-Agent + 简单Python工作流（无LangGraph依赖）

---

## 系统架构

```
用户上传简历 → Agent 1 (分析+搜索) → Agent 2 (优化+审核) → 生成DOCX
```

### Agent 1: 简历分析与行业搜索
- 解析简历文件(PDF/Word/Markdown)
- DuckDuckGo联网搜索行业信息
- 一次API调用完成分析+搜索结果整合

### Agent 2: 简历优化与质量审核
- 优化简历内容、措辞、量化成果
- 一次API调用完成优化+审核
- 包含人性化关怀寄语、行业分析、竞争力评分、职业建议

---

## 文件结构

```
ResumeOptimizer/
├── agents/
│   ├── __init__.py           # 导出 ResumeWorkflow, Agent1Analyze, Agent2Optimize
│   ├── graph.py              # ResumeWorkflow（简单Python函数，无LangGraph）
│   ├── agent1_analyze.py     # Agent 1: 简历分析 + 行业搜索
│   └── agent2_optimize.py    # Agent 2: 简历优化 + 质量审核
├── api/
│   ├── __init__.py
│   └── client_factory.py     # API客户端工厂（超时120秒）
├── utils/
│   ├── __init__.py
│   ├── config_manager.py     # 配置管理（2个Agent配置）
│   ├── docx_generator.py     # Word文档生成
│   ├── file_parser.py        # PDF/Word解析
│   ├── markdown_parser.py    # Markdown解析
│   └── prompt_filter.py      # JSON验证
├── app/
│   ├── __init__.py
│   ├── gui.py                # 主界面（QThread + 2-Agent工作流）
│   ├── config_window.py      # API配置窗口（2个Tab）
│   ├── markdown_input.py     # Markdown输入窗口
│   └── preview_window.py     # 预览窗口
├── main.py                   # 程序入口
├── 多线程修复版打包.bat       # 打包工具
├── 启动简历助手.bat           # 启动程序
├── AGENTS.md                 # 本文档
└── README.md                 # 用户文档
```

---

## Agent详细说明

### Agent 1: 简历分析与行业搜索

**文件**: `agents/agent1_analyze.py`
**配置键**: `agent1_analyze`

**流程**:
1. `_parse_resume()`: 解析PDF/Word/Markdown为文本
2. `_search_industry()`: DuckDuckGo搜索行业信息（10秒超时）
3. `_analyze_with_api()`: 一次API调用，同时完成简历分析+行业信息整合

**输入**: `resume_data` + `user_intent`
**输出**: 合并后的结构化数据

---

### Agent 2: 简历优化与质量审核

**文件**: `agents/agent2_optimize.py`
**配置键**: `agent2_optimize`

**流程**:
1. `_optimize_with_api()`: 一次API调用完成所有工作
2. 直接生成完整优化结果，包含：
   - 优化后的简历内容
   - 人性化寄语
   - 竞争力评分
   - 行业分析
   - 职业建议

**关键约束**:
- ✅ 必须有人性化寄语 (humanized_message)
- ✅ 必须评估竞争力 (overall_score)
- ✅ 必须给成长建议 (career_suggestions)
- ✅ 必须给行业分析 (industry_analysis)

---

## 工作流

**文件**: `agents/graph.py`

```python
class ResumeWorkflow:
    def __init__(self, agent1, agent2):
        self.agent1 = agent1
        self.agent2 = agent2

    def run(self, resume_data, user_intent):
        analyzed = self.agent1.process(resume_data, user_intent)
        optimized = self.agent2.process(analyzed, user_intent)
        return optimized
```

**关键改动**: 去掉了LangGraph依赖，使用简单的Python函数调用。

---

## API配置

### ⚠️ 模型选择经验（重要！）

**禁止使用思考模式（Thinking Mode）模型！** 以下模型会自动启用深度思考，导致：
- 响应时间从1分钟暴增到10分钟+
- 消耗大量token（思考过程可能占用50-100K tokens）
- 程序卡死无响应

| 模型 | 类型 | 是否可用 | 原因 |
|------|------|---------|------|
| `Qwen/Qwen3.5-4B` | 思考模型 | ❌ 禁止 | 默认启用思考模式，10分钟+无响应 |
| `Qwen/Qwen3.6-27B` | 思考模型 | ❌ 禁止 | 默认启用思考模式，10分钟+无响应 |
| `Qwen/Qwen2.5-72B-Instruct` | 非思考模型 | ✅ 推荐 | 1分钟内完成，效果好 |
| `Qwen/Qwen2.5-7B-Instruct` | 非思考模型 | ✅ 可用 | 速度快，成本更低 |
| `deepseek-chat` | 非思考模型 | ✅ 可用 | 性价比高 |

**经验总结**：
- ✅ 模型名称带 `Instruct` 的 = 非思考模型 = 可用
- ❌ 模型名称带 `3.5` 或 `3.6` 的 = 思考模型 = 禁止
- ❌ 不要尝试用 `enable_thinking: False` 关闭思考模式，这个参数会导致API卡死

### 配置键

| 配置键 | 用途 |
|--------|------|
| `agent1_analyze` | Agent 1 简历分析 |
| `agent2_optimize` | Agent 2 简历优化 |

### 推荐模型

| Agent | 推荐模型 |
|-------|---------|
| Agent 1 | Qwen/Qwen2.5-72B-Instruct |
| Agent 2 | Qwen/Qwen2.5-72B-Instruct |

### 超时设置

- API超时: 120秒（2分钟）
- DuckDuckGo搜索超时: 10秒

---

## 协作开发指南

### 修改Prompt
1. 修改对应Agent文件中的 `system_prompt` 字符串
2. 必须保持中文标签
3. 必须保留人性化功能
4. 修改后重新打包测试

### 添加新功能
1. 在对应Agent的 `process()` 方法中添加逻辑
2. 更新Prompt中的JSON格式说明
3. 更新 `_default_xxx()` 方法的返回值

### 打包
1. 关闭所有简历优化助手.exe进程
2. 删除dist和build文件夹
3. 运行"多线程修复版打包.bat"

---

## 版本历史

| 版本 | 修改内容 |
|------|---------|
| v7.0 | 优化Agent2流程为单次API调用，完善文档和.gitignore |
| v6.0 | 4Agent合并为2Agent，去掉LangGraph，修复超时问题 |
| v5.0 | 添加详细协作文档 |
| v4.0 | 精简Prompt |
| v3.0 | 添加人性化关怀功能 |
| v2.0 | 修复超时问题，添加多线程支持 |
| v1.0 | 初始版本 |

---

**文档版本**: v7.0
**最后更新**: 2026-05-31
