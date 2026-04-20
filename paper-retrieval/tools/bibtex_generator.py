"""
BibTeX 参考文献生成工具
"""
import re
from pathlib import Path
from tools.arxiv_api import Paper


def generate_citation_key(paper: Paper) -> str:
    """
    为论文生成 BibTeX 引用键。
    
    策略：
    1. 第一作者姓氏 + 年份 + 标题关键字（如 zhao2025chart）
    2. 如果第一作者姓氏无法提取，使用标题第一个实词
    
    Args:
        paper: Paper 对象
         
    Returns:
        BibTeX 引用键字符串
    """
    year = str(paper.year)
    
    # 提取标题关键字
    stop_words = {"the", "a", "an", "of", "in", "on", "for", "and", "or", "to", "with", "by", "from", "via", "using", "based", "towards", "toward"}
    words = re.findall(r'[a-zA-Z]+', paper.title.lower())
    meaningful = [w for w in words if w not in stop_words and len(w) > 2]
    keyword = meaningful[0] if meaningful else "paper"
    
    if paper.authors:
        first_author = paper.authors[0]
        suffixes = {"jr", "sr", "ii", "iii", "iv"}
        parts = first_author.split()
        name_parts = [p for p in parts if p.lower() not in suffixes]
        if name_parts:
            last_name = name_parts[-1].lower()
            last_name = re.sub(r'[^a-z]', '', last_name)
            if last_name:
                return f"{last_name}{year}{keyword}"
    
    return f"{keyword}{year}"


def generate_unique_citation_key(paper: Paper, used_keys: set) -> str:
    """
    生成唯一的 BibTeX 引用键，确保不重复。
    
    Args:
        paper: Paper 对象
        used_keys: 已使用的引用键集合
        
    Returns:
        唯一的 BibTeX 引用键
    """
    base_key = generate_citation_key(paper)
    
    if base_key not in used_keys:
        used_keys.add(base_key)
        return base_key
    
    counter = 1
    while True:
        new_key = f"{base_key}{counter}"
        if new_key not in used_keys:
            used_keys.add(new_key)
            return new_key
        counter += 1


def paper_to_bibtex(paper: Paper, citation_key: str) -> str:
    """
    将 Paper 对象转换为 BibTeX 条目字符串。
    
    Args:
        paper: Paper 对象
        citation_key: BibTeX 引用键
        
    Returns:
        BibTeX 条目字符串
    """
    # 构建作者字符串，用 " and " 连接
    authors_str = " and ".join(paper.authors) if paper.authors else "Unknown"
    
    # 提取 arxiv_id 的纯数字部分用于 eprint
    arxiv_num = paper.arxiv_id.split('v')[0]  # 去掉版本号
    
    bibtex = f"""@article{{{citation_key},
  author       = {{{authors_str}}},
  title        = {{{paper.title}}},
  journal      = {{CoRR}},
  volume       = {{abs/{arxiv_num}}},
  year         = {{{paper.year}}},
  url          = {{{paper.url}}},
  eprinttype   = {{arXiv}},
  eprint       = {{arXiv:{arxiv_num}}},
  archivePrefix = {{arXiv}},
  primaryClass = {{cs.AI}},
}}"""
    
    return bibtex


def generate_bibtex_file(papers: list[Paper], output_path: str) -> dict[str, str]:
    """
    为论文列表生成 BibTeX 文件。
    
    Args:
        papers: Paper 对象列表
        output_path: 输出 .bib 文件路径
        
    Returns:
        {arxiv_id: citation_key} 映射字典
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    used_keys = set()
    key_map = {}  # arxiv_id -> citation_key
    bibtex_entries = []
    
    for paper in papers:
        citation_key = generate_unique_citation_key(paper, used_keys)
        key_map[paper.arxiv_id] = citation_key
        bibtex_entries.append(paper_to_bibtex(paper, citation_key))
    
    # 写入文件
    content = "\n\n".join(bibtex_entries) + "\n"
    output_path.write_text(content, encoding="utf-8")
    
    return key_map
