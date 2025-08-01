import os
import httpx
import json
from typing import Any, Dict, Optional

class FeishuAPI:
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = None

    def _get_tenant_access_token(self) -> str:
        """获取 tenant_access_token"""
        if self.tenant_access_token:
            return self.tenant_access_token
            
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = self._send_request("POST", url, headers=headers, data=json.dumps(data))
        result = response.json()
        
        if result.get("code") == 0:
            self.tenant_access_token = result["tenant_access_token"]
            return self.tenant_access_token
        else:
            raise Exception(f"获取tenant_access_token失败: {result}")

    def _send_request(self, method: str, url: str, headers: Dict[str, str] = None, 
                     data: Any = None, params: Dict[str, Any] = None) -> httpx.Response:
        """发送HTTP请求"""
        if headers is None:
            headers = {}
            
        # 添加代理支持
        proxies = {
            "http://": os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy"),
            "https://": os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"),
        }
        # 如果没有设置代理，则proxies为None
        if not proxies["http://"] and not proxies["https://"]:
            proxies = None
            
        with httpx.Client(proxies=proxies) as client:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                content=data,
                params=params,
                timeout=30
            )
            return response

    def send_message(self, receive_id_type: str, receive_id: str, msg_type: str, content: str) -> Dict[str, Any]:
        """发送消息"""
        token = self._get_tenant_access_token()
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        params = {receive_id_type: receive_id}
        data = {
            "msg_type": msg_type,
            "content": content
        }
        
        response = self._send_request("POST", url, headers=headers, params=params, data=json.dumps(data))
        return response.json()

    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """获取用户信息"""
        token = self._get_tenant_access_token()
        url = f"https://open.feishu.cn/open-apis/contact/v3/users/{user_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        response = self._send_request("GET", url, headers=headers)
        return response.json()
