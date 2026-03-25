"""
关键词生成 Agent - 根据研究主题生成检索关键词
"""
import json
import yaml
from pathlib import Path
from tools.llm_client import system_user
from rich.console import Console

console = Console()

SYSTEM_KEYWORD_GENERATOR = """你是一位学术论文检索专家。
你的任务是根据用户提供的研究主题，生成高质量的检索关键词。
这些关键词将用于在 arXiv 等学术数据库中检索相关论文。
请始终以 JSON 格式返回，不要包含额外解释。"""


def _cfg():
    p = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(p.read_text())


def generate_keywords(topic: str) -> list[str]:
    """根据研究主题生成检索关键词
    
    Args:
        topic: 研究主题
        
    Returns:
        关键词列表
    """
    prompt = f"""研究主题：{topic}

请为该主题生成 3-8 个精准的检索关键词（英文），用于在 arXiv 等学术数据库中检索相关论文。

要求：
1. 关键词应该是英文（arXiv 主要使用英文）
2. 包含核心概念、技术术语、相关方法等
3. 考虑同义词、近义词、上下位词
4. 按重要性降序排列

返回 JSON 格式：
{{
  "keywords": [
    "keyword1",
    "keyword2",
    "keyword3"
  ],
  "search_strategy": "简要说明检索策略"
}}

示例：
输入主题："LLM Agent 技术"
输出：
{{
  "keywords": [
    "LLM Agent",
    "Large Language Model Agent",
    "autonomous agent",
    "AI agent planning",
    "tool use LLM",
    "agent reasoning",
    "cognitive architecture"
  ],
  "search_strategy": "覆盖 LLM Agent 的核心概念、规划能力、工具使用等关键方面"
}}"""

    try:
        raw = system_user(SYSTEM_KEYWORD_GENERATOR, prompt, max_tokens=512)
        raw = _extract_json(raw)
        data = json.loads(raw)
        keywords = data.get("keywords", [])
        
        if not keywords:
            console.print(f"[yellow]⚠️  生成的关键词为空，使用原始主题[/yellow]\n")
            return [topic]
        
        console.print(f"[bold cyan]🔑 生成的关键词:[/bold cyan]")
        for i, kw in enumerate(keywords, 1):
            console.print(f"  {i}. {kw}")
        if "search_strategy" in data:
            console.print(f"[dim]检索策略：{data['search_strategy']}[/dim]\n")
        
        return keywords
        
    except Exception as e:
        error_msg = str(e)
        console.print(f"[yellow]⚠️  关键词生成失败，使用原始主题：{error_msg}[/yellow]\n")
        return [topic]


def _extract_json(text: str) -> str:
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return text.strip()
