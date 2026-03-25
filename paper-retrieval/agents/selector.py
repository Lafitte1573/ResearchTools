"""
论文筛选 Agent - 评估论文与主题相关性并提取关键信息
"""
import json
import yaml
from pathlib import Path
from tools.llm_client import system_user
from tools.arxiv_api import Paper
from rich.console import Console

console = Console()

SYSTEM_EVALUATOR = """你是一位学术论文筛选助手。
你的任务是评估论文与研究主题的相关性，并提取关键信息。
请始终以 JSON 格式返回，不要包含额外解释。"""


def _cfg():
    p = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(p.read_text())


def evaluate_paper(paper: Paper, topic: str) -> Paper:
    """评估单篇论文与目标主题的相关性"""
    prompt = f"""研究主题：{topic}

论文标题：{paper.title}
论文摘要：{paper.abstract[:2000]}

请评估该论文与研究主题的相关性，并提取关键信息，返回 JSON：
{{
  "relevance_score": 7,
  "reason": "相关性判断理由（1句话）",
  "key_points": [
    "主要观点1",
    "主要观点2",
    "核心贡献"
  ],
  "category": "该论文属于哪个子方向"
}}

评分标准（1-10）：
- 9-10: 核心相关
- 7-8: 高度相关
- 5-6: 部分相关
- 3-4: 弱相关
- 1-2: 不相关"""

    try:
        raw = system_user(SYSTEM_EVALUATOR, prompt, max_tokens=512)
        raw = _extract_json(raw)
        data = json.loads(raw)
        paper.relevance_score = float(data.get("relevance_score", 5))
        paper.key_points = data.get("key_points", [])
    except (json.JSONDecodeError, Exception):
        paper.relevance_score = 5.0
        paper.key_points = []

    return paper


def select_top_papers(papers: list[Paper], topic: str) -> list[Paper]:
    """评估并选取最相关的论文"""
    threshold = _cfg()["search"]["arxiv"].get("relevance_threshold", 5)
    top_k = _cfg()["search"]["arxiv"].get("top_k", 5)

    console.print(f"[cyan]📊 评估 {len(papers)} 篇论文...[/cyan]")

    scored = [evaluate_paper(p, topic) for p in papers]
    scored.sort(key=lambda p: p.relevance_score, reverse=True)

    selected = [p for p in scored if p.relevance_score >= threshold][:top_k]

    console.print(f"[green]✓ 筛选完成：{len(selected)} 篇[/green]")
    for p in selected:
        console.print(f"  [{p.relevance_score:.1f}] {p.title[:60]}")

    return selected


def _extract_json(text: str) -> str:
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return text.strip()
