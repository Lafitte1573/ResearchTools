"""
论文笔记生成 Agent - 将 PDF 转换为结构化笔记
支持通过图像方式读取 PDF 前10页，生成英文笔记
"""
import base64
import yaml
from pathlib import Path
from typing import Optional
from tools.llm_client import client, load_config
from rich.console import Console

console = Console()


def _cfg():
    p = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(p.read_text())


SYSTEM_NOTE_GENERATOR = """You are an expert academic research assistant specializing in creating comprehensive paper notes.

Your task is to analyze academic papers and generate structured notes in English that capture the core ideas and methodological implementations.

Guidelines:
1. Focus on core contributions, key innovations, and implementation details
2. Be concise yet comprehensive (within 3000 words)
3. Use clear section headers and bullet points for readability
4. Maintain technical accuracy while ensuring clarity
5. Highlight novel contributions and their significance

Output Format (in Markdown):
# [The paper title here]

## Core Ideas
[Summarize the main research problem, motivation, and core conceptual contributions]

## Key Innovations
[List and explain the novel contributions and what makes this work unique]

## Method & Implementation
[Detail the methodology, architecture, algorithms, and key technical implementations]

## Experimental Results
[Summarize main experimental findings, datasets used, and performance metrics]

Remember: Keep the total length within 3000 words."""


def pdf_to_images(pdf_path: str, max_pages: int = 10) -> list[str]:
    """
    将 PDF 文件转换为 base64 编码的图片列表
    
    Args:
        pdf_path: PDF 文件路径
        max_pages: 最大转换页数（默认10页）
        
    Returns:
        base64 编码的图片列表
    """
    try:
        from pdf2image import convert_from_path
        
        # 转换 PDF 为图片
        images = convert_from_path(
            pdf_path, 
            first_page=1, 
            last_page=max_pages,
            dpi=200  # 适中的分辨率，平衡质量和速度
        )
        
        # 转换为 base64 编码
        image_bases = []
        for img in images:
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            image_bases.append(img_base64)
        
        return image_bases
    
    except ImportError:
        console.print("[yellow]⚠️ 需要安装 pdf2image 和 poppler[/yellow]")
        console.print("[dim]运行: pip install pdf2image[/dim]")
        console.print("[dim]macOS: brew install poppler[/dim]")
        console.print("[dim]Linux: sudo apt-get install poppler-utils[/dim]")
        raise
    except Exception as e:
        console.print(f"[red]PDF 转图片失败: {e}[/red]")
        raise


def generate_note_from_images(
    image_bases: list[str], 
    paper_title: str = "",
    paper_authors: list[str] = None,
    paper_year: int = 0,
    arxiv_id: str = ""
) -> str:
    """
    使用多模态大模型从图片生成论文笔记
    
    Args:
        image_bases: base64 编码的图片列表
        paper_title: 论文标题
        paper_authors: 作者列表
        paper_year: 发表年份
        arxiv_id: arXiv ID
        
    Returns:
        生成的笔记内容（Markdown 格式）
    """
    cfg = _cfg()["llm"]
    
    # 构建消息内容
    content_parts = []
    
    # 添加文本提示
    paper_info = f"Paper Title: {paper_title}\n"
    if paper_authors:
        paper_info += f"Authors: {', '.join(paper_authors)}\n"
    if paper_year:
        paper_info += f"Year: {paper_year}\n"
    if arxiv_id:
        paper_info += f"arXiv ID: {arxiv_id}\n"
    
    content_parts.append({
        "type": "text",
        "text": f"{paper_info}\n\nPlease analyze the following paper pages and generate comprehensive notes according to the system instructions."
    })
    
    # 添加图片
    for img_base64 in image_bases:
        content_parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{img_base64}"
            }
        })
    
    messages = [
        {"role": "system", "content": SYSTEM_NOTE_GENERATOR},
        {"role": "user", "content": content_parts}
    ]
    
    try:
        # 调用多模态模型
        response = client.chat.completions.create(
            model=cfg.get("vision_model", cfg["model"]),  # 优先使用视觉模型
            messages=messages,
            temperature=cfg.get("temperature", 0.3),
            max_tokens=cfg.get("max_tokens", 16000),
        )
        
        note_content = response.choices[0].message.content.strip()
        return note_content
    
    except Exception as e:
        console.print(f"[red]笔记生成失败: {e}[/red]")
        raise


def generate_paper_note(
    pdf_path: str,
    paper_title: str = "",
    paper_authors: list[str] = None,
    paper_year: int = 0,
    arxiv_id: str = "",
    max_pages: int = 10
) -> str:
    """
    从 PDF 文件生成论文笔记的主函数
    
    Args:
        pdf_path: PDF 文件路径
        paper_title: 论文标题
        paper_authors: 作者列表
        paper_year: 发表年份
        arxiv_id: arXiv ID
        max_pages: 最大读取页数
        
    Returns:
        生成的笔记内容（Markdown 格式）
    """
    console.print(f"[cyan]📄 正在处理: {Path(pdf_path).name}[/cyan]")
    
    # Step 1: PDF 转图片
    console.print("[dim]  ├─ 转换 PDF 为图片...[/dim]")
    try:
        image_bases = pdf_to_images(pdf_path, max_pages=max_pages)
        console.print(f"[green]  └─ ✓ 成功转换 {len(image_bases)} 页[/green]")
    except Exception as e:
        console.print(f"[red]  └─ ✗ PDF 转图片失败: {e}[/red]")
        return ""
    
    # Step 2: 调用大模型生成笔记
    console.print("[dim]  ├─ 调用大模型生成笔记...[/dim]")
    try:
        note = generate_note_from_images(
            image_bases=image_bases,
            paper_title=paper_title,
            paper_authors=paper_authors,
            paper_year=paper_year,
            arxiv_id=arxiv_id
        )
        console.print(f"[green]  └─ ✓ 笔记生成完成 ({len(note)} 字符)[/green]")
        return note
    except Exception as e:
        console.print(f"[red]  └─ ✗ 笔记生成失败: {e}[/red]")
        return ""


if __name__ == "__main__":
    # 测试代码
    import sys
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        note = generate_paper_note(
            pdf_path=pdf_file,
            paper_title="Test Paper",
            arxiv_id="test.00000"
        )
        print("\n" + "="*80)
        print(note)
