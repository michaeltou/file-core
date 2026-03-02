import traceback

import requests
import engine.util.log as log

class HttpClient:
    def __init__(self, timeout=600):
        """
        初始化 HttpClient 类。

        :param timeout: 请求超时时间，默认为 600 秒。
        """
        self.timeout = timeout

    def get(self, url, params=None, headers=None, uuid=None):
        """
        发送 GET 请求。

        :param url: 请求的 URL。
        :param params: 请求参数，字典类型，可选。
        :param headers: 请求头，字典类型，可选。
        :param uuid: 请求的唯一标识符，可选。
        :return: 响应对象，如果请求失败返回 None。
        """
        try:
            response = requests.get(
                url=url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()  # 检查请求是否成功
            return response
        except requests.RequestException as e:
            stack_trace = traceback.format_exc()
            message = 'uuid:%s,http请求处理失败,异常信息：%s' % (uuid, stack_trace)
            log.error(message)
            raise Exception(message)



    def post(self, url, request_body=None, headers=None, uuid=None):
        """
        发送 POST 请求。

        :param url: 请求的 URL。
        :param request_body: 请求体，字典或 JSON 字符串类型，可选。
        :param headers: 请求头，字典类型，可选。
        :return: 响应对象，如果请求失败返回 None。
        """
        try:
            if isinstance(request_body, dict):
                response = requests.post(
                    url=url,
                    json=request_body,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                response = requests.post(
                    url=url,
                    data=request_body,
                    headers=headers,
                    timeout=self.timeout
                )
            response.raise_for_status()  # 检查请求是否成功
            return response
        except requests.RequestException as e:
            stack_trace = traceback.format_exc()
            message = 'uuid:%s,http请求处理失败,异常信息：%s' % (uuid, stack_trace)
            log.error(message)
            raise Exception(message)


'''

# 导入 HttpClient 类
from http_client import HttpClient

# 创建 HttpClient 实例
client = HttpClient()

# 发送 GET 请求
get_url = "https://jsonplaceholder.typicode.com/todos/1"
get_response = client.get(get_url)
if get_response:
    print(get_response.json())

# 发送 POST 请求
post_url = "https://jsonplaceholder.typicode.com/posts"
post_body = {
    "title": "foo",
    "body": "bar",
    "userId": 1
}
post_response = client.post(post_url, post_body)
if post_response:
    print(post_response.json())


'''