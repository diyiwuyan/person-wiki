"""
LLM 客户端 - 优先使用 Friday 内部接口，不可用时引导用户配置
"""
import json
import sys
from typing import Optional
from openai import OpenAI
from config import (
    FRIDAY_BASE_URL, FRIDAY_APP_ID, FRIDAY_MODEL,
    load_user_config, save_user_config
)


class LLMClient:
    """统一 LLM 调用客户端，自动检测可用接口"""

    def __init__(self):
        self.client: Optional[OpenAI] = None
        self.model: str = ""
        self.source: str = ""
        self._init_client()

    def _init_client(self):
        """初始化 LLM 客户端，优先 Friday，其次用户配置"""
        # 1. 尝试 Friday 内部接口（需要 LLM 专用 App ID）
        if FRIDAY_APP_ID and self._try_friday():
            return
        # 2. 尝试用户已保存的配置
        if self._try_user_config():
            return
        # 3. 引导用户输入配置
        self._prompt_user_config()

    def _try_friday(self) -> bool:
        """尝试连接 Friday 内部 LLM"""
        try:
            client = OpenAI(
                api_key=FRIDAY_APP_ID,
                base_url=FRIDAY_BASE_URL,
                timeout=30.0,
            )
            # 发一个轻量探测请求（Friday 对 max_tokens=5 可能返回空内容，只要不报错就算成功）
            resp = client.chat.completions.create(
                model=FRIDAY_MODEL,
                messages=[{"role": "user", "content": "请回复：OK"}],
                max_tokens=10,
            )
            # 只要 HTTP 不报错（choices 存在）就认为连接成功
            if resp and resp.choices is not None:
                self.client = client
                self.model  = FRIDAY_MODEL
                self.source = "Friday (内部)"
                print(f"✅ 已连接 Friday 内部 LLM（模型：{self.model}）")
                return True
            return False
        except Exception as e:
            print(f"⚠️  Friday 接口不可用：{e}")
            return False

    def _try_user_config(self) -> bool:
        """尝试用户已保存的自定义配置"""
        cfg = load_user_config()
        if not cfg.get("api_key"):
            return False
        try:
            client = OpenAI(
                api_key=cfg["api_key"],
                base_url=cfg.get("base_url", "https://api.openai.com/v1"),
                timeout=60.0,
            )
            resp = client.chat.completions.create(
                model=cfg.get("model", "gpt-4o-mini"),
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=5,
            )
            self.client = client
            self.model  = cfg.get("model", "gpt-4o-mini")
            self.source = f"用户自定义（{cfg.get('base_url', 'OpenAI')}）"
            print(f"✅ 已连接用户自定义 LLM（模型：{self.model}）")
            return True
        except Exception as e:
            print(f"⚠️  用户配置的 LLM 不可用：{e}")
            return False

    def _prompt_user_config(self):
        """引导用户输入 LLM 配置"""
        print("\n" + "="*60)
        print("🔧 未检测到可用的 LLM 接口，请手动配置：")
        print("="*60)
        print("支持任何 OpenAI 兼容接口（OpenAI / Azure / 本地 Ollama 等）\n")

        api_key  = input("请输入 API Key: ").strip()
        base_url = input("请输入 Base URL（直接回车使用 OpenAI 官方）: ").strip()
        model    = input("请输入模型名称（直接回车使用 gpt-4o-mini）: ").strip()

        if not base_url:
            base_url = "https://api.openai.com/v1"
        if not model:
            model = "gpt-4o-mini"

        cfg = {"api_key": api_key, "base_url": base_url, "model": model}
        save_user_config(cfg)

        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=60.0)
        self.model  = model
        self.source = f"用户自定义（{base_url}）"
        print(f"✅ 配置完成，使用模型：{self.model}")

    def chat(self, prompt: str, system: str = "", max_tokens: int = 2000) -> str:
        """发送对话请求，返回文本内容"""
        if not self.client:
            raise RuntimeError("LLM 客户端未初始化")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        if not resp or not resp.choices:
            raise RuntimeError(f"LLM 返回空响应，resp={resp}")
        content = resp.choices[0].message.content
        if content is None:
            # Friday 有时对短 prompt 返回 None，重试一次用更明确的指令
            raise RuntimeError(
                f"LLM 返回 None 内容，finish_reason={resp.choices[0].finish_reason}，"
                f"status={getattr(resp, 'status', 'N/A')}，message={getattr(resp, 'message', 'N/A')}"
            )
        return content.strip()

    def chat_json(self, prompt: str, system: str = "", max_tokens: int = 2000) -> dict:
        """发送对话请求，返回解析后的 JSON"""
        text = self.chat(prompt, system, max_tokens)
        # 提取 JSON 块（兼容 markdown 代码块包裹）
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 尝试找到第一个 { 到最后一个 } 的内容
            start = text.find("{")
            end   = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            raise


# 全局单例
_client: Optional[LLMClient] = None

def get_llm() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
