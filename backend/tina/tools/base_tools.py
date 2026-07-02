import requests
from ddgs import DDGS
from typing import Any
from pathlib import Path
from datetime import datetime
from langchain.tools import tool, BaseTool
from markdownify import markdownify
from backend.tina.skills import load_skills
from backend.tina.util.logger import Logger

UTF8 = "utf-8"
logger = Logger(__name__)


def run_cmd(command: list[str]) -> str:
    import subprocess

    result = subprocess.run(
        command, text=True, capture_output=True, check=True, shell=True
    )
    return result.stdout.strip()


@tool
def read_file(filepath: Path | str = "") -> str:
    """base filepath read file content"""
    logger.info("调用read_file工具")
    content: str = ""
    try:
        if isinstance(filepath, Path):
            content = filepath.read_text(encoding=UTF8)
        elif isinstance(filepath, str):
            with open(filepath, "r", encoding=UTF8) as f:
                content = f.read()
        return content.strip()
    except Exception as e:
        return f"读取{filepath}失败：{e}"


@tool
def write_file(filename: str, content: str | bytes) -> str:
    """write content"""
    logger.info("调用write_file工具")
    try:
        root = Path(__file__).parent / filename
        if isinstance(content, str):
            root.write_text(content, encoding=UTF8)
        elif isinstance(content, bytes):
            root.write_bytes(content)
        return f"write file {filename} success"
    except Exception as e:
        return f"write file {filename} fail：{e}"


@tool
def edit_file(path: Path, old_text: str, new_text: str) -> str:
    """
    Edit the file and replace old content with new content.
    """
    if not path.exists():
        return f"未发现文件"
    try:
        text = path.read_text(encoding=UTF8)
        if old_text in text:
            content = text.replace(old_text, new_text)
            path.write_text(content, encoding=UTF8)
            return "edit file complete"
    except Exception as e:
        return f"edit file fail: {e}"


# 定义查询天气函数
@tool
def get_weather(city: str) -> str:
    """
    Use wttr.in to check the weather information for a specified city.
    """
    logger.info(f"调用weather工具: {city}")
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
        current_condition = data["current_condition"][0]
        weather_desc = current_condition["weatherDesc"][0]["value"]
        temp_c = current_condition["temp_C"]
        uv_index = current_condition["uvIndex"]

        # 格式化成自然语言返回
        return f"{city} 当前天气:{weather_desc}，气温{temp_c}摄氏度，防晒指数{uv_index}"

    except requests.exceptions.RequestException as e:
        # 处理网络错误
        return f"错误:查询天气时遇到网络问题 - {e}"
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误:解析天气数据失败，可能是城市名称无效 - {e}"


# get current time
@tool
def get_date() -> str:
    """query current datetime"""
    logger.info("调用get_date工具")
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")


@tool
def glob(pattern: list[str]) -> str:
    """
    Use ripgrep to find code snippets or keywords, with support for regular expressions; it’s best to provide the absolute path to the file.
    e.g. ['rg','-i' 'hello', 'base_tools.py']
    """
    try:
        result = run_cmd(pattern)
        return result
    except Exception as e:
        logger.info(f"error: {e}")


@tool
def run_command(command: list[str]) -> str:
    """
    Execute external commands,Support native terminal commands; when using PowerShell, the prefix "powershell" must be added.
    e.g. ['powershell', 'ls'], ['node','-v']
    """
    logger.info("调用run_command工具")
    try:
        result = run_cmd(command)
        return result
    except Exception as e:
        return f"error：{e}"


@tool
def web_search(
    keyword: str,
    max_results: int = 5,
) -> list[dict[str, Any]]:
    """
    Search the internet using keywords
    Args:
        keyword: search keyword
        max_results: query max num
    Returns:
        A list of dictionaries containing the search results.
    """
    ddgs = DDGS()
    return ddgs.text(query=keyword.strip(), max_results=max_results, backend="bing")


@tool
def search_image(
    query: str, max_results: int = 5, color: str | None = None
) -> list[dict[str, Any]]:
    """
    Search the images using keywords
     Args:
         query: search keyword
         max_results: query max num
         color: style, feel
     returns
         A list of dictionaries containing the search results.
    """
    ddgs = DDGS()
    return ddgs.images(
        query=query, page=1, max_results=max_results, backend="bing", color=color
    )


@tool
def send_request(url: str, method: str = "GET", **kwargs) -> Any:
    """
    Send a network request to the specified URL and obtain the response.
    args
        url: url
        method: method (e.g., GET, POST, PUT, DELETE) default GET
        kwargs: args
    """
    kwargs["headers"] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    request = requests.request(
        method=method,
        url=url,
        **kwargs,
    )
    request.raise_for_status()
    return markdownify(request.text)


@tool
def load_skill(skill_name: str) -> str:
    """
    load the full content of a skill into the agents context
    args:
        skill_name: The name of the skill to load (e.g "web-design")
    """
    # 加载所有skill
    logger.info("调用load_skill工具")
    skills = load_skills()
    for skill in skills:
        if skill.name == skill_name:
            return f"Loaded skill: {skill_name}\n\n{skill.content}"
    available = ", ".join([s.name for s in skills])
    return f"{skill_name} not Found. available skills: {available}"


def get_all_tool() -> list[BaseTool]:
    return [
        read_file,
        write_file,
        get_date,
        edit_file,
        glob,
        get_weather,
        run_command,
        web_search,
        send_request,
        load_skill,
    ]
