"""
arXiv 文献搜索工具
"""
import arxiv
import yaml
from pathlib import Path
from dataclasses import dataclass, field


def _cfg():
    p = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(p.read_text())["search"]["arxiv"]


@dataclass
class Paper:
    title: str
    abstract: str
    authors: list[str]
    year: int
    arxiv_id: str
    url: str
    source: str = "arxiv"
    relevance_score: float = 0.0
    key_points: list[str] = field(default_factory=list)
    full_text: str = ""
    pdf_path: str = ""
    bibtex_key: str = ""
    note: str = ""  # 生成的论文笔记

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "abstract": self.abstract,
            "authors": self.authors,
            "year": self.year,
            "arxiv_id": self.arxiv_id,
            "url": self.url,
            "source": self.source,
            "relevance_score": self.relevance_score,
            "key_points": self.key_points,
            "full_text": self.full_text[:50000] if self.full_text else "",
            "pdf_path": self.pdf_path,
            "bibtex_key": self.bibtex_key,
            "note": self.note[:10000] if self.note else "",  # 限制笔记长度
        }


def search_arxiv(query: str, max_results: int = None) -> list[Paper]:
    cfg = _cfg()
    max_results = max_results or cfg["max_results"]

    sort_map = {
        "relevance": arxiv.SortCriterion.Relevance,
        "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
        "submittedDate": arxiv.SortCriterion.SubmittedDate,
    }
    sort_by = sort_map.get(cfg.get("sort_by", "relevance"), arxiv.SortCriterion.Relevance)

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=sort_by,
    )

    papers = []
    client = arxiv.Client()
    for result in client.results(search):
        papers.append(Paper(
            title=result.title,
            abstract=result.summary,
            authors=[a.name for a in result.authors],
            year=result.published.year,
            arxiv_id=result.entry_id.split("/")[-1],
            url=result.entry_id,
        ))
    return papers


def search_arxiv_with_keywords(keywords: list[str], max_results: int = None) -> list[Paper]:
    """使用多个关键词进行检索
    
    Args:
        keywords: 关键词列表
        max_results: 最大检索数量
        
    Returns:
        论文列表
    """
    if not keywords:
        return []
    
    # 构建 OR 查询：将所有关键词用 OR 连接
    # 同时搜索标题和摘要
    query_parts = []
    for kw in keywords:
        # 对每个关键词，搜索标题和摘要
        query_parts.append(f'(all:"{kw}")')
    
    combined_query = " OR ".join(query_parts)
    
    return search_arxiv(combined_query, max_results)


def search_arxiv_single(query: str, max_results: int = 3) -> list[Paper]:
    """根据标题精确搜索单篇论文
    
    Args:
        query: 论文标题（支持模糊搜索）
        max_results: 最大结果数
        
    Returns:
        论文列表
    """
    client = arxiv.Client()
    
    search = arxiv.Search(
        query=f'ti:"{query}"',
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    
    papers = []
    for result in client.results(search):
        papers.append(Paper(
            title=result.title,
            abstract=result.summary,
            authors=[a.name for a in result.authors],
            year=result.published.year,
            arxiv_id=result.entry_id.split("/")[-1],
            url=result.entry_id,
        ))
    
    if not papers:
        search = arxiv.Search(
            query=f'all:"{query}"',
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        for result in client.results(search):
            papers.append(Paper(
                title=result.title,
                abstract=result.summary,
                authors=[a.name for a in result.authors],
                year=result.published.year,
                arxiv_id=result.entry_id.split("/")[-1],
                url=result.entry_id,
            ))
    
    return papers[:max_results]
