#!/usr/bin/env python3
"""
测试笔记生成功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_note_generator_import():
    """测试导入笔记生成器"""
    print("测试 1: 导入 note_generator 模块...")
    try:
        from agents.note_generator import generate_paper_note
        print("✓ 导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_pipeline_import():
    """测试 pipeline 导入"""
    print("\n测试 2: 导入 retrieve 模块...")
    try:
        from pipeline.retrieve import run_retrieve
        print("✓ 导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_paper_class():
    """测试 Paper 类是否有 note 字段"""
    print("\n测试 3: 检查 Paper 类的 note 字段...")
    try:
        from tools.arxiv_api import Paper
        paper = Paper(
            title="Test",
            abstract="Test abstract",
            authors=["Author 1"],
            year=2024,
            arxiv_id="2401.00001",
            url="http://test.com"
        )
        # 检查是否有 note 属性
        assert hasattr(paper, 'note'), "Paper 类缺少 note 属性"
        assert paper.note == "", "note 默认值应为空字符串"
        
        # 测试设置 note
        paper.note = "Test note content"
        assert paper.note == "Test note content", "note 设置失败"
        
        # 测试 to_dict 包含 note
        paper_dict = paper.to_dict()
        assert 'note' in paper_dict, "to_dict() 返回的字典缺少 note 字段"
        
        print("✓ Paper 类 note 字段正常")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """测试配置文件"""
    print("\n测试 4: 检查配置文件...")
    try:
        import yaml
        config_path = project_root / "config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        
        # 检查 LLM 配置
        assert 'vision_model' in cfg['llm'], "缺少 vision_model 配置"
        print(f"  - vision_model: {cfg['llm']['vision_model']}")
        
        # 检查 notes 配置
        assert 'notes' in cfg, "缺少 notes 配置段"
        assert 'max_pages' in cfg['notes'], "缺少 max_pages 配置"
        assert 'max_note_length' in cfg['notes'], "缺少 max_note_length 配置"
        print(f"  - max_pages: {cfg['notes']['max_pages']}")
        print(f"  - max_note_length: {cfg['notes']['max_note_length']}")
        
        print("✓ 配置文件正常")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_cli():
    """测试命令行接口"""
    print("\n测试 5: 检查 main.py 命令行参数...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(project_root / "main.py"), "retrieve", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if '--notes' in result.stdout:
            print("✓ --notes 参数已添加")
            return True
        else:
            print("✗ --notes 参数未找到")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def main():
    print("="*60)
    print("笔记生成功能测试")
    print("="*60)
    
    tests = [
        test_note_generator_import,
        test_pipeline_import,
        test_paper_class,
        test_config,
        test_main_cli,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("="*60)
    
    if all(results):
        print("\n🎉 所有测试通过！")
        print("\n使用说明:")
        print("  python main.py retrieve \"研究主题\" --notes")
        print("\n注意事项:")
        print("  1. 需要安装 pdf2image: pip install pdf2image")
        print("  2. macOS 需要安装 poppler: brew install poppler")
        print("  3. Linux 需要安装 poppler-utils: sudo apt-get install poppler-utils")
        print("  4. 确保 config.yaml 中配置了 vision_model（多模态模型）")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查上述错误信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
