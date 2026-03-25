"""
Paper Retrieval - 命令行入口
"""
import click
from pipeline.retrieve import run_retrieve
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
@click.option("--parse", "do_parse", is_flag=True, default=False, help="是否解析 PDF")
@click.option("--no-keywords", "use_keywords", flag_value=False, default=True, help="不使用生成的关键词进行检索")
def retrieve(topic: str, max_results: int, output_dir: str, do_parse: bool, use_keywords: bool):
    """检索论文

    指定研究主题，自动从 arXiv 检索相关论文。
    默认会先根据主题生成关键词，再进行检索。
    使用 --parse 可同时下载 PDF 并调用 MinerU 解析。
    使用 --no-keywords 可直接使用原始主题检索（不生成关键词）。

    示例：
        python main.py retrieve "LLM Agent 技术"
        python main.py retrieve "多模态大模型" -n 5 --parse
        python main.py retrieve "强化学习" --no-keywords
    """
    run_retrieve(topic, max_results, output_dir, do_parse, use_keywords)


if __name__ == "__main__":
    cli()
