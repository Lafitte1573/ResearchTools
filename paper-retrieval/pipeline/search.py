"""
论文搜索 Pipeline
根据 JSON 文件中的标题列表搜索论文
"""
import json
import yaml
from pathlib import Path
from datetime import datetime

from tools.arxiv_api import search_arxiv_single
from tools.bibtex_generator import generate_bibtex_file
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


def _cfg():
    p = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(p.read_text())


def run_search(input_json: str, output_dir: str = None, max_results: int = 3):
    """根据 JSON 文件搜索论文
    
    Args:
        input_json: 输入 JSON 文件路径
        output_dir: 输出目录
        max_results: 每个标题最多搜索结果数
    
    Returns:
        项目目录路径
    """
    with open(input_json, encoding="utf-8") as f:
        data = json.load(f)
    
    items = data if isinstance(data, list) else [data]
    
    cfg = _cfg()
    out_dir = Path(output_dir) if output_dir else Path(cfg["output"]["dir"])
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = Path(input_json).stem[:20]
    project_dir = out_dir / f"search_{safe_name}_{timestamp}"
    project_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(f"\n[bold cyan]🔍 Paper Search[/bold cyan]")
    console.print(f"[dim]输入：{input_json}[/dim]")
    console.print(f"[dim]项目数量：{len(items)}[/dim]")
    console.print(f"[dim]输出：{project_dir}[/dim]\n")
    
    all_papers = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("搜索中...", total=len(items))
        
        for item in items:
            title = item.get("title", "")
            if not title:
                progress.advance(task)
                continue
            
            papers = search_arxiv_single(title, max_results=max_results)
            
            if papers:
                all_papers.extend(papers)
                console.print(f"[green]✓ {title[:50]}... → {len(papers)} 篇[/green]")
            else:
                console.print(f"[yellow]⚠️ 未找到：{title[:50]}...[/yellow]")
            
            progress.advance(task)
    
    if not all_papers:
        console.print("[bold red]❌ 未找到任何论文[/bold red]")
        return None
    
    console.print(f"\n[green]✓ 共找到 {len(all_papers)} 篇论文[/green]")
    
    # 去重
    seen = set()
    unique_papers = []
    for p in all_papers:
        if p.arxiv_id not in seen:
            seen.add(p.arxiv_id)
            unique_papers.append(p)
    
    console.print(f"[dim]去重后：{len(unique_papers)} 篇[/dim]\n")
    
    # 生成 BibTeX
    console.print("[bold]生成 reference.bib[/bold]")
    key_map = generate_bibtex_file(unique_papers, str(project_dir / "reference.bib"))
    for paper in unique_papers:
        paper.bibtex_key = key_map.get(paper.arxiv_id, "")
    console.print(f"[green]✓ 已保存: {project_dir / 'reference.bib'}[/green]\n")
    
    # 保存 metadata
    console.print("[bold]保存 metadata.json[/bold]")
    metadata = {
        "source": input_json,
        "timestamp": timestamp,
        "total_results": len(unique_papers),
        "papers": [p.to_dict() for p in unique_papers],
    }
    
    metadata_path = project_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    console.print(f"[green]✓ 已保存: {metadata_path}[/green]\n")
    
    console.print(f"[bold green]🎉 搜索完成！共 {len(unique_papers)} 篇论文[/bold green]")
    
    return project_dir