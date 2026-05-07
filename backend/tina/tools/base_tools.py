import requests
from datetime import datetime
from ddgs import DDGS
from typing import Any, AnyStr
from pathlib import Path
from glob import glob
from markdownify import markdownify

UTF8 = "utf-8"


def read_file(filepath: Path) -> str:
    """base filepath read file content"""
    if not filepath.exists():
        return "file path not found."
    content = filepath.read_text(encoding=UTF8)
    return content.strip()


def write_file(filename: str, content: str | bytes) -> str:
    """write content"""
    try:
        root = Path(__file__).parent / filename
        if isinstance(content, str):
            root.write_text(content, encoding=UTF8)
        elif isinstance(content, bytes):
            root.write_bytes(content)
        return "write file"
    except Exception as e:
        raise e


def glob_file(pattern: str) -> list[AnyStr]:
    """base pattern match file"""
    return glob(pattern)


# 定义查询天气函数
def get_weather(city: str) -> str:
    """
    通过wttr.in查询用户指定的天气信息
    city: 查询的城市
    """
    print(f'查询城市: {city}')
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    # API端点，我们请求JSON格式的数据
    url = f"https://wttr.in/{city}?format=j1"

    try:
        # 发起网络请求
        response = requests.get(url, headers=headers)
        # 检查响应状态码是否为200 (成功)
        response.raise_for_status()
        # 解析返回的JSON数据
        data = response.json()

        # 提取当前天气状况
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']
        uv_index = current_condition['uvIndex']

        # 格式化成自然语言返回
        return f"{city} 当前天气:{weather_desc}，气温{temp_c}摄氏度，防晒指数{uv_index}"

    except requests.exceptions.RequestException as e:
        # 处理网络错误
        return f"错误:查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误:解析天气数据失败，可能是城市名称无效 - {e}"


# 查询当前日期时间
def get_date() -> str:
    '''query current date'''
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def run_command(command: str) -> str:
    """run external command"""
    import subprocess
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def web_search(
        query: str,
        max_results: int = 5,
) -> list[dict[str, Any]]:
    """
    base query keyword search result.
    Args:
        query: search keyword
        max_results: query max num
    Returns:
        A list of dictionaries containing the search results.
    """
    ddgs = DDGS()
    return ddgs.text(
        query=query,
        max_results=max_results,
        backend="bing"
    )


def search_image(
        query: str,
        max_results: int = 5,
        color: str | None = None
) -> list[dict[str, Any]]:
    """
   base query keyword search image.
    Args:
        query: search keyword
        max_results: query max num
        color: style, feel
    returns
        A list of dictionaries containing the search results.
    """
    ddgs = DDGS()
    return ddgs.images(
        query=query,
        page=1,
        max_results=max_results,
        backend="bing",
        color=color
    )


def send_request_response_markdown(
        url: str,
        method: str = "GET",
        **kwargs
) -> Any:
    """
    send request to url response text
    args
        url: url
        method: method (e.g., GET, POST, PUT, DELETE) default GET
        params: request parameter
        json: request body
        timeout: timeout default 5s
        kwargs: args
    """
    kwargs['headers'] = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    request = requests.request(
        method=method,
        url=url,
        **kwargs,
    )
    request.raise_for_status()
    return markdownify(request.text)


def send_request_response_bytes(
        url: str,
        method: str = "GET",
        **kwargs
) -> bytes:
    """
    send request to url
    args
        url: url
        method: method (e.g., GET, POST, PUT, DELETE) default GET
        kwargs: args
    """
    kwargs['headers'] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    request = requests.request(
        method=method,
        url=url,
        **kwargs,
    )
    request.raise_for_status()
    return request.content


def get_all_tool() -> list:
    return [
        read_file,
        write_file,
        get_date,
        get_weather,
        run_command,
        web_search,
        send_request_response_markdown
    ]
