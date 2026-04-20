"""
论文下载与笔记生成 Pipeline
逐条读取 metadata.json，下载论文并生成笔记
"""
import json
import os
import yaml
from pathlib import Path

from tools.mineru_parser import download_pdf, download_and_parse
from agents.note_generator import generate_paper_note
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


def _cfg():
    p = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(p.read_text())


def load_metadata(metadata_path: str) -> dict:
    with open(metadata_path, encoding="utf-8") as f:
        return json.load(f)


def save_metadata(metadata: dict, metadata_path: str):
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def run_notion(metadata_path: str, use_mineru: bool = True, generate_notes: bool = True, force_redownload: bool = False):
    """执行论文下载与笔记生成
    
    Args:
        metadata_path: metadata.json 文件路径
        use_mineru: 是否使用 MinerU 解析（False 则用 PyMuPDF）
        generate_notes: 是否生成论文笔记
        force_redownload: 是否强制重新下载 PDF
    """
    metadata = load_metadata(metadata_path)
    project_dir = Path(metadata_path).parent
    
    pdf_dir = project_dir / "pdfs"
    note_dir = project_dir / "notes"
    note_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    
    papers = metadata.get("papers", [])
    if not papers:
        console.print("[yellow]⚠️ metadata.json 中没有论文数据[/yellow]")
        return
    
    console.print(f"\n[bold cyan]📥 Paper Download & Notes[/bold cyan]")
    console.print(f"[dim]项目：{project_dir.name}[/dim]")
    console.print(f"[dim]论文数量：{len(papers)}[/dim]\n")
    
    notes_config = _cfg().get("notes", {})
    max_pages = notes_config.get("max_pages", 10)
    
    updated_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("处理中...", total=len(papers))
        
        for paper in papers:
            arxiv_id = paper.get("arxiv_id", "")
            
            if not arxiv_id:
                progress.advance(task)
                continue
            
            pdf_path = paper.get("pdf_path", "")
            
            # 下载或使用已有 PDF
            if not pdf_path or not Path(pdf_path).exists() or force_redownload:
                pdf_path = download_pdf(arxiv_id, str(pdf_dir))
            
            # 更新 metadata 中的 pdf_path
            if pdf_path:
                paper["pdf_path"] = pdf_path
            
            # 生成笔记
            if generate_notes and pdf_path and Path(pdf_path).exists():
                # 检查笔记文件是否已存在
                note_file = note_dir / f"{arxiv_id}_note.md"
                if note_file.exists():
                    console.print(f"[dim]⊘ {arxiv_id}: 笔记已存在，跳过[/dim]")
                    # 如果已有笔记文件，读取并更新到 metadata
                    paper["note"] = note_file.read_text(encoding="utf-8")
                else:
                    # 生成新笔记
                    note = generate_paper_note(
                        pdf_path=pdf_path,
                        paper_title=paper.get("title", ""),
                        paper_authors=paper.get("authors", []),
                        paper_year=paper.get("year", 0),
                        arxiv_id=arxiv_id,
                        max_pages=max_pages
                    )
                    
                    if note:
                        paper["note"] = note
                        
                        # 保存单独的笔记文件
                        note_file.write_text(note, encoding="utf-8")
                        
                        updated_count += 1
                        console.print(f"[green]✓ {arxiv_id}: 笔记已生成[/green]")
                    else:
                        console.print(f"[yellow]⚠️ {arxiv_id}: 笔记生成失败[/yellow]")
            else:
                console.print(f"[yellow]⚠️ {arxiv_id}: PDF 不存在，跳过笔记生成[/yellow]")
            
            progress.advance(task)
    
    # 保存更新后的 metadata
    save_metadata(metadata, metadata_path)
    console.print(f"\n[green]✓ metadata.json 已更新（{updated_count} 篇笔记）[/green]")
    console.print(f"[dim]笔记目录：{note_dir}[/dim]")
    
    return project_dir


def run_notion_from_dir(output_dir: str, use_mineru: bool = True, generate_notes: bool = True, force_redownload: bool = False):
    """从项目目录运行 notion 流程
    
    Args:
        output_dir: 项目目录（包含 metadata.json）
        use_mineru: 是否使用 MinerU 解析
        generate_notes: 是否生成笔记
        force_redownload: 是否强制重新下载 PDF
    """
    project_dir = Path(output_dir)
    metadata_path = project_dir / "metadata.json"
    
    if not metadata_path.exists():
        console.print(f"[bold red]❌ metadata.json 不存在: {metadata_path}[/bold red]")
        return None
    
    return run_notion(str(metadata_path), use_mineru, generate_notes, force_redownload)