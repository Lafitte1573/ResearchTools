"""
PDF 解析工具
- 调用 MinerU HTTP 服务解析 PDF → Markdown
- 或使用 PyMuPDF (fitz) 做轻量级纯文本提取
"""
import os
import re
import requests
import yaml
from pathlib import Path
from rich.console import Console

try:
    import fitz
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

console = Console()


def _cfg():
    p = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(p.read_text())


def _mineru_url() -> str:
    try:
        return _cfg().get("mineru", {}).get("url", "http://localhost:5000")
    except Exception:
        return "http://localhost:5000"


def download_pdf(arxiv_id: str, pdf_dir: str) -> str | None:
    pdf_dir = Path(pdf_dir)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    filepath = pdf_dir / f"{arxiv_id}.pdf"

    if filepath.exists() and filepath.stat().st_size > 1000:
        return str(filepath)

    url = f"https://arxiv.org/pdf/{arxiv_id}"
    try:
        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return str(filepath)
    except Exception as e:
        console.print(f"[yellow]PDF 下载失败 [{arxiv_id}]: {e}[/yellow]")
        return None


def parse_pdf_with_mineru(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        return ""

    try:
        with open(pdf_path, "rb") as f:
            files = {"pdf": (os.path.basename(pdf_path), f, "application/pdf")}
            resp = requests.post(f"{_mineru_url()}/parse/pdf", files=files, timeout=1200)

        if resp.status_code != 200:
            return ""

        result = resp.json()
        if result.get("success") and result.get("markdown"):
            return result["markdown"]
        return ""
    except requests.ConnectionError:
        return ""
    except Exception:
        return ""


def parse_pdf_with_pymupdf(pdf_path: str) -> str:
    if not HAS_FITZ:
        console.print("[yellow]PyMuPDF 未安装，请运行: pip install pymupdf[/yellow]")
        return ""
    
    if not os.path.exists(pdf_path):
        return ""
    
    try:
        doc = fitz.open(pdf_path)
        md_parts = []
        
        for page_num, page in enumerate(doc, 1):
            blocks = page.get_text("blocks")
            page_headings = []
            page_body = []
            
            for block in blocks:
                block_text = block[4].strip()
                if not block_text:
                    continue
                
                if _is_likely_heading(block_text):
                    page_headings.append(block_text)
                else:
                    cleaned = _clean_block_text(block_text)
                    if cleaned:
                        page_body.append(cleaned)
            
            if page_headings:
                for h in page_headings:
                    md_parts.append(f"## {h}\n")
            
            for b in page_body:
                md_parts.append(f"{b}\n\n")
            
            if page_num < len(doc):
                md_parts.append("---\n\n")
        
        doc.close()
        return "".join(md_parts)
    except Exception as e:
        console.print(f"[yellow]PyMuPDF 解析失败: {e}[/yellow]")
        return ""


def _is_likely_heading(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    if len(text) > 150:
        return False
    if '\n' in text and len(text.split('\n')) > 3:
        return False
    return True


def _clean_block_text(text: str) -> str:
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def download_and_parse(arxiv_id: str, output_dir: str, force_reparse: bool = False, use_mineru: bool = True) -> str:
    pdf_dir = os.path.join(output_dir, "pdfs")
    md_dir = os.path.join(output_dir, "markdown")
    os.makedirs(md_dir, exist_ok=True)

    md_path = os.path.join(md_dir, f"{arxiv_id}.md")
    if not force_reparse and os.path.exists(md_path) and os.path.getsize(md_path) > 500:
        return open(md_path, encoding="utf-8").read()

    pdf_path = download_pdf(arxiv_id, pdf_dir)
    if not pdf_path:
        return ""

    if use_mineru:
        full_text = parse_pdf_with_mineru(pdf_path)
    else:
        full_text = parse_pdf_with_pymupdf(pdf_path)
    
    if full_text:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(full_text)
    return full_text


if __name__ == "__main__":
    print(download_and_parse("2305.16705", "output"))