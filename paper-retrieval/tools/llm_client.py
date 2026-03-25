"""
LLM 客户端 - 统一封装本地模型调用
"""
import yaml
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from pathlib import Path


def load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_config = load_config()
_llm_cfg = _config["llm"]

client = OpenAI(
    base_url=_llm_cfg["base_url"],
    api_key=_llm_cfg["api_key"],
)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
def chat(messages: list[dict], temperature: float = None, max_tokens: int = None) -> str:
    resp = client.chat.completions.create(
        model=_llm_cfg["model"],
        messages=messages,
        temperature=temperature or _llm_cfg["temperature"],
        max_tokens=max_tokens or _llm_cfg["max_tokens"],
    )
    return resp.choices[0].message.content.strip() if resp.choices[0].message.content else ""


def system_user(system: str, user: str, **kwargs) -> str:
    return chat([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ], **kwargs)
