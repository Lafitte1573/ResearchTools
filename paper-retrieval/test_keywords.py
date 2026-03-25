#!/usr/bin/env python3
"""
测试关键词生成功能
"""
from agents.keyword_generator import generate_keywords

def test_keyword_generation():
    """测试关键词生成"""
    topics = [
        "LLM Agent 技术",
        "多模态大模型",
        "强化学习",
    ]
    
    for topic in topics:
        print(f"\n{'='*60}")
        print(f"主题：{topic}")
        print('='*60)
        keywords = generate_keywords(topic)
        print(f"\n生成的关键词 ({len(keywords)}个):")
        for i, kw in enumerate(keywords, 1):
            print(f"  {i}. {kw}")
        print()

if __name__ == "__main__":
    test_keyword_generation()
