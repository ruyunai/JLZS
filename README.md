# ResumeOptimizer - 简历优化助手

基于 2-Agent 架构的智能简历优化工具，无需 LangGraph 依赖，轻量高效。

## 功能特性

- **双 Agent 协作**: 分析Agent + 优化Agent协同工作
- **多格式简历支持**: 支持 PDF/Word 文件上传和 Markdown 手动输入
- **行业情报搜集**: 自动联网搜索目标行业和岗位信息
- **智能优化**: 基于 AI 分析优化简历内容和格式，量化成果
- **人性化关怀**: 包含鼓励寄语、竞争力评分、职业建议、行业分析
- **灵活配置**: 支持国内主流 AI 服务商（硅基流动/DeepSeek/智谱等）
- **独立运行**: 一键打包为 exe，无需安装 Python 环境
- **U盘可移植**: 打包后的 exe 可直接复制到其他电脑运行

## 技术栈

| 组件 | 技术 |
|------|------|
| GUI 框架 | PyQt6 |
| AI API | OpenAI 兼容接口（支持硅基流动、DeepSeek等） |
| 文件解析 | pdfplumber（PDF）、python-docx（Word） |
| 文档生成 | python-docx |
| 联网搜索 | DuckDuckGo |
| 打包工具 | PyInstaller |

## 快速开始

### 环境要求

- Python 3.10+
- Windows 操作系统（为了打包 exe）

### 安装依赖

```bash
pip install openai python-docx pdfplumber markdown requests pydantic PyQt6
```

### 运行程序

```bash
python main.py
```

或者直接双击运行 `启动简历助手.bat`

## 配置说明

首次运行需要配置 API Key：

1. 点击主界面的「Agent配置」按钮
2. 选择服务商（推荐硅基流动）
3. 输入你的 API Key
4. 选择模型（**必须使用非思考模型！推荐 Qwen/Qwen2.5-72B-Instruct**）
5. 点击「保存配置」

### 重要：模型选择

| 模型 | 状态 | 说明 |
|------|------|------|
| Qwen/Qwen2.5-72B-Instruct | 推荐 | 1分钟内完成，效果好 |
| Qwen/Qwen2.5-7B-Instruct | 可用 | 速度快，成本更低 |
| deepseek-chat | 可用 | 性价比高 |
| Qwen/Qwen3.5-4B | 禁止 | 思考模型，速度极慢 |
| Qwen/Qwen3.6-27B | 禁止 | 思考模型，速度极慢 |

**注意**：不要使用带 `3.5` 或 `3.6` 的模型，它们是思考模型，会导致 10分钟以上无响应。

## 使用流程

1. **上传简历**: 拖拽 PDF/Word 文件到界面，或点击「手动输入简历 (Markdown)」
2. **补充信息**: 可选填写意向行业、岗位、薪资等
3. **开始优化**: 点击「开始优化简历」
4. **查看结果**: 生成的 Word 文档会自动保存到桌面/简历优化输出文件夹

## 打包为 exe

### 方法 1：使用批处理脚本（推荐）

1. 关闭所有正在运行的简历优化助手
2. 双击运行 `多线程修复版打包.bat`
3. 等待 5-15 分钟，打包完成后在 `dist/简历优化助手_PyQt6版/` 文件夹找到 exe

### 方法 2：手动打包

```bash
pyinstaller PyQt6专用打包.spec --clean --noconfirm
```

## U 盘可移植性

打包后的程序支持 U 盘直接迁移！

### 如何使用

1. 将整个 `dist/简历优化助手_PyQt6版/` 文件夹复制到 U 盘
2. 在目标电脑上复制该文件夹到任意位置
3. 双击运行 `简历优化助手_PyQt6版.exe` 即可

### 注意事项

- 目标电脑需要联网（调用 AI API）
- 首次在新电脑运行需要重新配置 API Key（配置保存在用户目录）
- 不需要目标电脑安装 Python 或任何依赖

## 目录结构

```
ResumeOptimizer/
├── main.py                 # 程序入口
├── app/                    # GUI 界面模块
├── agents/                 # Agent 实现
├── api/                    # API 客户端
├── utils/                  # 工具函数
├── config.json            # 默认配置（模板，不含 API Key）
├── AGENTS.md              # 技术文档
└── README.md              # 本文档
```

## 支持的 AI 服务商

- 硅基流动 (SiliconFlow) - 推荐
- DeepSeek
- 智谱AI (GLM)
- 百度千帆
- 自定义 OpenAI 兼容接口

## 开发说明

详见 AGENTS.md 了解 Agent 架构和开发指南。

## 版本历史

| 版本 | 说明 |
|------|------|
| v2.0 | 双 Agent 架构，无 LangGraph 依赖，支持 U 盘移植 |
| v1.0 | 初始版本 |

## License

MIT License
