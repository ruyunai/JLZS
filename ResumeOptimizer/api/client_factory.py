from typing import Optional, Dict, Any
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class APIClientFactory:
    _clients = {}

    @staticmethod
    def create_client(provider: str, api_key: str, api_base: Optional[str] = None,
                     model: Optional[str] = None) -> 'BaseAPIClient':
        cache_key = f"{provider}_{api_key[:8]}"
        if cache_key in APIClientFactory._clients:
            return APIClientFactory._clients[cache_key]

        if provider in ['siliconflow', 'deepseek', 'zhipu', 'baidu', 'openai', 'custom']:
            client = OpenAICompatibleClient(api_key, api_base, model)
        elif provider == 'spark':
            client = SparkClient(api_key, model)
        elif provider == 'hunyuan':
            client = HunyuanClient(api_key, model)
        else:
            raise ValueError(f"不支持的服务商: {provider}")

        APIClientFactory._clients[cache_key] = client
        return client

    @staticmethod
    def test_connection(provider: str, api_key: str, api_base: Optional[str] = None,
                       model: Optional[str] = None) -> Dict[str, Any]:
        try:
            client = APIClientFactory.create_client(provider, api_key, api_base, model)
            result = client.test_connection()
            return {"success": True, "message": "连接成功", "details": result}
        except Exception as e:
            return {"success": False, "message": f"连接失败: {str(e)}", "details": None}

    @staticmethod
    def clear_cache():
        APIClientFactory._clients.clear()


class BaseAPIClient:
    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model

    def chat(self, messages: list, **kwargs) -> str:
        raise NotImplementedError

    def vision_chat(self, messages: list, **kwargs) -> str:
        raise NotImplementedError

    def test_connection(self) -> Dict[str, Any]:
        raise NotImplementedError


class OpenAICompatibleClient(BaseAPIClient):
    def __init__(self, api_key: str, api_base: Optional[str] = None,
                 model: Optional[str] = None, timeout: int = 120):
        super().__init__(api_key, model)
        self.api_base = api_base or "https://api.openai.com/v1"
        self.timeout = timeout
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base,
            timeout=timeout
        )

    def chat(self, messages: list, **kwargs) -> str:
        try:
            params = {"model": self.model, "messages": messages}
            params.update(kwargs)
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
                raise Exception(f"API请求超时({self.timeout}秒)")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                raise Exception("API认证失败：请检查API Key")
            elif "429" in error_msg or "rate limit" in error_msg.lower():
                raise Exception("API请求过于频繁：请稍后重试")
            else:
                raise Exception(f"API调用失败：{error_msg}")

    def vision_chat(self, messages: list, **kwargs) -> str:
        return self.chat(messages, **kwargs)

    def test_connection(self) -> Dict[str, Any]:
        try:
            response = self.client.models.list()
            models = [m.id for m in response.data[:10]]
            return {"models_available": models}
        except Exception as e:
            raise Exception(f"API连接测试失败：{str(e)}")


class SparkClient(BaseAPIClient):
    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model)

    def chat(self, messages: list, **kwargs) -> str:
        raise NotImplementedError("讯飞星火API需要额外SDK支持")

    def vision_chat(self, messages: list, **kwargs) -> str:
        raise NotImplementedError("讯飞星火视觉API需要额外SDK支持")

    def test_connection(self) -> Dict[str, Any]:
        raise NotImplementedError("讯飞星火API需要额外SDK支持")


class HunyuanClient(BaseAPIClient):
    def __init__(self, api_key: str, model: Optional[str] = None):
        super().__init__(api_key, model)

    def chat(self, messages: list, **kwargs) -> str:
        raise NotImplementedError("腾讯混元API需要额外SDK支持")

    def vision_chat(self, messages: list, **kwargs) -> str:
        raise NotImplementedError("腾讯混元视觉API需要额外SDK支持")

    def test_connection(self) -> Dict[str, Any]:
        raise NotImplementedError("腾讯混元API需要额外SDK支持")
