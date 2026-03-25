# Paper Retrieval

学术论文检索工具 - LLM 驱动的智能论文检索系统

根据用户调研领域自动检索 arXiv 论文、下载 PDF、调用 MinerU 解析并保存为结构化 metadata.json。

## 快速开始

### 基本用法

```bash
# 智能关键词检索（推荐）- 自动生成精准的英文检索关键词
python main.py retrieve "LLM Agent 技术"

# 检索并解析 PDF 为 Markdown
python main.py retrieve "多模态大模型" --parse

# 指定检索数量和输出目录
python main.py retrieve "强化学习" -n 10 -o my_papers

# 传统模式 - 不使用关键词生成，直接用原始主题检索
python main.py retrieve "强化学习" --no-keywords
```

### 命令行参数详解

#### 必需参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `TOPIC` | 字符串 | 研究主题/领域 | `"LLM Agent 技术"` |

#### 可选参数

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--number` | `-n` | 10 | 从 arXiv 检索的最大论文数量 |
| `--output` | `-o` | `output/` | 结果输出目录路径 |
| `--parse` | - | False | 是否下载 PDF 并调用 MinerU 解析为 Markdown |
| `--no-keywords` | - | False | 禁用关键词生成功能，直接使用原始主题检索 |

### 使用示例

#### 1. 文献调研（智能关键词模式）

```bash
# 自动生成多个相关关键词进行全方位检索
python main.py retrieve "图神经网络"
```

**执行流程：**
1. LLM 分析主题 "图神经网络"
2. 生成关键词：["Graph Neural Network", "GNN", "Graph Convolutional Network", ...]
3. 使用 OR 查询在 arXiv 检索
4. 筛选最相关的 5 篇论文
5. 保存 metadata.json

#### 2. 深度分析（带 PDF 解析）

```bash
# 检索 5 篇论文并解析 PDF
python main.py retrieve "大语言模型幻觉" -n 5 --parse
```

**输出内容：**
- `metadata.json` - 包含论文元数据和完整文本
- `pdfs/*.pdf` - 下载的 PDF 文件
- `markdown/*.md` - MinerU 解析后的 Markdown 文件

#### 3. 批量检索

```bash
# 检索 50 篇论文到指定目录
python main.py retrieve "时间序列预测" -n 50 -o ts_forecasting_dataset
```

#### 4. 精确检索（传统模式）

```bash
# 使用特定术语直接检索，不经过关键词扩展
python main.py retrieve "Transformers are All You Need" --no-keywords
```

## 功能特点

- **🔑 智能关键词生成**: 根据用户输入的研究主题，自动生成 3-8 个精准的英文检索关键词
- **🔍 多关键词检索**: 使用 OR 逻辑组合关键词，在 arXiv 进行全方位检索，提高召回率
- **⭐ LLM 智能筛选**: 自动评估每篇论文与主题的相关性（1-10 分），并选取 Top-K 篇
- **📄 PDF 解析**: 支持下载 PDF 并调用 MinerU 解析为结构化的 Markdown 格式
- **⚙️ 灵活配置**: 可通过配置文件或命令行参数调整检索策略

## 输出结果

### 目录结构

```
output/
└── retrieval_主题_时间戳/
    ├── metadata.json          # 论文元数据（必选）
    ├── pdfs/                  # 下载的 PDF 文件（使用--parse 时生成）
    │   └── 2401.xxxxx.pdf
    └── markdown/              # 解析后的 Markdown（使用--parse 时生成）
        └── 2401.xxxxx.md
```

### metadata.json 格式

```json
{
  "topic": "LLM Agent 技术",
  "timestamp": "20260325_100000",
  "total_searched": 25,        // 检索到的论文总数
  "selected_count": 5,         // 筛选出的高相关论文数
  "parsed": true,              // 是否解析了 PDF
  "papers": [
    {
      "title": "论文标题",
      "abstract": "摘要内容...",
      "authors": ["作者 1", "作者 2"],
      "year": 2024,
      "arxiv_id": "2401.xxxxx",
      "url": "https://arxiv.org/abs/2401.xxxxx",
      "relevance_score": 9.5,  // 相关性评分 (1-10)
      "key_points": ["核心观点 1", "核心观点 2"],
      "category": "Agent 规划",
      "full_text": "完整论文内容...",
      "pdf_path": "pdfs/2401.xxxxx.pdf"
    }
  ]
}
```

## 环境要求

- Python 3.10+
- 本地 LLM 服务（默认：http://localhost:8000/v1）
- MinerU 服务（可选，用于 PDF 解析，默认：http://localhost:5000）

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 验证安装
python main.py --help
```
