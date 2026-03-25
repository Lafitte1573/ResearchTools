"""
MinerU PDF 解析工具
- 调用 MinerU HTTP 服务解析 PDF → Markdown
"""
import os
import requests
import yaml
from pathlib import Path
from rich.console import Console

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


def download_and_parse(arxiv_id: str, output_dir: str, force_reparse: bool = False) -> str:
    pdf_dir = os.path.join(output_dir, "pdfs")
    md_dir = os.path.join(output_dir, "markdown")
    os.makedirs(md_dir, exist_ok=True)

    md_path = os.path.join(md_dir, f"{arxiv_id}.md")
    if not force_reparse and os.path.exists(md_path) and os.path.getsize(md_path) > 500:
        return open(md_path, encoding="utf-8").read()

    pdf_path = download_pdf(arxiv_id, pdf_dir)
    if not pdf_path:
        return ""

    full_text = parse_pdf_with_mineru(pdf_path)
    if full_text:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(full_text)
    return full_text
