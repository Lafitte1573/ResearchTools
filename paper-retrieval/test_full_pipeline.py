#!/usr/bin/env python3
"""
测试完整的检索流程（包括关键词生成）
"""
from agents.keyword_generator import generate_keywords
from tools.arxiv_api import search_arxiv_with_keywords, search_arxiv

def test_full_pipeline():
    """测试完整流程：主题 -> 关键词 -> 检索"""
    topic = "LLM Agent"
    
    print(f"\n{'='*80}")
    print(f"测试完整检索流程")
    print(f"{'='*80}")
    print(f"研究主题：{topic}\n")
    
    # Step 1: 生成关键词
    print("Step 1: 生成检索关键词")
    print("-" * 80)
    keywords = generate_keywords(topic)
    
    # Step 2: 使用关键词检索
    print("\nStep 2: 使用关键词检索论文")
    print("-" * 80)
    print(f"检索查询：{' OR '.join(keywords)}")
    
    papers = search_arxiv_with_keywords(keywords[:3], max_results=5)  # 只使用前 3 个关键词
    
    print(f"\n检索到 {len(papers)} 篇论文:")
    for i, paper in enumerate(papers, 1):
        print(f"\n[{i}] {paper.title}")
        print(f"    年份：{paper.year}")
        print(f"    摘要：{paper.abstract[:150]}...")
    
    print(f"\n{'='*80}")
    print("测试完成!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    test_full_pipeline()
