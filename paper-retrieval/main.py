"""
Paper Retrieval - 命令行入口
"""
import click
from pathlib import Path
from pipeline.retrieve import run_retrieve
from pipeline.notion import run_notion, run_notion_from_dir
from pipeline.search import run_search
from rich.console import Console

console = Console()


@click.group()
def cli():
    """Paper Retrieval - 学术论文检索工具"""
    pass


@cli.command()
@click.argument("topic")
@click.option("-n", "--number", "max_results", default=None, type=int, help="最大检索数量")
@click.option("-o", "--output", "output_dir", default=None, help="输出目录")
@click.option("--no-keywords", "use_keywords", flag_value=False, default=True, help="不使用生成的关键词进行检索")
def retrieve(topic: str, max_results: int, output_dir: str, use_keywords: bool):
    """检索论文
    
    指定研究主题，自动从 arXiv 检索相关论文。
    默认会先根据主题生成关键词，再进行检索。
    使用 --no-keywords 可直接使用原始主题检索（不生成关键词）。

    示例：
        python main.py retrieve "LLM Agent 技术"
        python main.py retrieve "多模态大模型" -n 5
        python main.py retrieve "深度学习" --no-keywords
    """
    run_retrieve(topic, max_results, output_dir, use_keywords)


@cli.command()
@click.argument("input_json", type=click.Path(exists=True))
@click.option("-n", "--number", "max_results", default=3, type=int, help="每个标题最多搜索结果数")
@click.option("-o", "--output", "output_dir", default=None, help="输出目录")
def search(input_json: str, max_results: int, output_dir: str):
    """根据 JSON 文件搜索论文
    
    读取 JSON 文件（包含 title 字段的列表），根据标题搜索论文，
    生成 reference.bib 和 metadata.json。
    
    示例：
        python main.py search ./papers.json
        python main.py search ./papers.json -n 5
    """
    console.print("[bold cyan]🔍 开始搜索论文...[/bold cyan]")
    try:
        result = run_search(input_json, output_dir, max_results)
        if result:
            console.print(f"[green]✓ 完成！项目目录：{result}[/green]")
        else:
            console.print("[yellow]⚠️ 未找到任何论文[/yellow]")
    except Exception as e:
        console.print(f"[bold red]❌ 错误：{e}[/bold red]")
        import traceback
        traceback.print_exc()


@cli.command()
@click.argument("project_dir", type=click.Path(exists=True))
@click.option("--pymupdf", "use_mineru", flag_value=False, default=True, help="使用 PyMuPDF 代替 MinerU")
@click.option("--no-notes", "generate_notes", flag_value=False, default=True, help="不生成论文笔记")
@click.option("--force", "force_redownload", is_flag=True, default=False, help="强制重新下载 PDF")
def notion(project_dir: str, use_mineru: bool, generate_notes: bool, force_redownload: bool):
    """下载论文并生成笔记
    
    从 metadata.json 读取论文信息，下载 PDF 并生成笔记。
    
    示例：
        python main.py notion ./output/retrieval_xxx_20250409
        python main.py notion ./output/retrieval_xxx_20250409 --pymupdf
        python main.py notion ./output/retrieval_xxx_20250409 --force
    """
    console.print("[bold cyan]🚀 开始生成论文笔记...[/bold cyan]")
    try:
        result = run_notion_from_dir(project_dir, use_mineru, generate_notes, force_redownload)
        if result:
            console.print(f"[green]✓ 完成！项目目录：{result}[/green]")
        else:
            console.print("[yellow]⚠️ 流程未正常执行[/yellow]")
    except Exception as e:
        console.print(f"[bold red]❌ 错误：{e}[/bold red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    cli()
