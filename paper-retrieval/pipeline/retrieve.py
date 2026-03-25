"""
论文检索 Pipeline
用户指定主题 → 自动检索、筛选、下载、解析
"""
import json
import yaml
from pathlib import Path
from datetime import datetime

from agents.selector import select_top_papers
from agents.keyword_generator import generate_keywords
from tools.arxiv_api import search_arxiv, search_arxiv_with_keywords, Paper
from tools.mineru_parser import download_and_parse, download_pdf
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


def _cfg():
    p = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(p.read_text())


def run_retrieve(topic: str, max_results: int = None, output_dir: str = None, do_parse: bool = False, use_keywords: bool = True):
    """执行论文检索流程
    
    Args:
        topic: 研究主题
        max_results: 最大检索数量
        output_dir: 输出目录
        do_parse: 是否解析 PDF
        use_keywords: 是否使用生成的关键词进行检索（默认 True）
    """
    cfg = _cfg()
    out_dir = Path(output_dir) if output_dir else Path(cfg["output"]["dir"])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic if c.isalnum() or c in " -").strip()[:30]
    project_dir = out_dir / f"retrieval_{safe_topic}_{timestamp}"
    project_dir.mkdir(parents=True, exist_ok=True)

    max_n = max_results or cfg["search"]["arxiv"]["max_results"]

    console.print(f"\n[bold cyan]🔍 Paper Retrieval[/bold cyan]")
    console.print(f"[dim]主题：{topic}[/dim]")
    console.print(f"[dim]输出：{project_dir}[/dim]\n")

    # Step 1: 生成关键词
    keywords = []
    if use_keywords:
        console.print("[bold]Step 1: 生成检索关键词[/bold]")
        keywords = generate_keywords(topic)
        console.print()
    
    # Step 2: 搜索论文
    console.print("[bold]Step 2: 搜索 arXiv 论文[/bold]")
    if use_keywords and keywords:
        papers = search_arxiv_with_keywords(keywords, max_results=max_n)
        console.print(f"[green]✓ 使用 {len(keywords)} 个关键词搜索到 {len(papers)} 篇论文[/green]\n")
    else:
        papers = search_arxiv(topic, max_results=max_n)
        console.print(f"[green]✓ 搜索到 {len(papers)} 篇论文[/green]\n")

    if not papers:
        console.print("[bold red]❌ 未找到相关论文[/bold red]")
        return None

    # Step 3: 评估筛选
    console.print("[bold]Step 2: 评估论文相关性[/bold]")
    selected = select_top_papers(papers, topic)
    console.print()

    # Step 4: 可选 - 解析论文
    parsed_data = {}
    if do_parse and selected:
        console.print("[bold]Step 3: 解析论文 PDF[/bold]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("解析中...", total=len(selected))
            for paper in selected:
                pdf_path = download_pdf(paper.arxiv_id, str(project_dir / "pdfs"))
                paper.pdf_path = pdf_path or ""
                full_text = download_and_parse(paper.arxiv_id, str(project_dir))
                paper.full_text = full_text
                parsed_data[paper.arxiv_id] = {
                    "full_text": full_text,
                    "pdf_path": pdf_path or "",
                }
                progress.advance(task)
        console.print(f"[green]✓ 解析完成[/green]\n")

    # Step 5: 保存 metadata
    console.print("[bold]Step 4: 保存 metadata.json[/bold]")
    metadata = {
        "topic": topic,
        "timestamp": timestamp,
        "total_searched": len(papers),
        "selected_count": len(selected),
        "parsed": do_parse,
        "papers": [p.to_dict() for p in selected],
    }

    metadata_path = project_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    console.print(f"[green]✓ 已保存: {metadata_path}[/green]\n")

    # 汇总
    console.print(f"[bold green]🎉 检索完成！共 {len(selected)} 篇论文[/bold green]")
    for p in selected:
        console.print(f"  - [{p.relevance_score:.1f}] {p.title[:70]}")

    return project_dir
