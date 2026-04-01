import os
import mimetypes
import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# 尝试提高 MCP server 的请求超时时间，但这取决于底层 mcp sdk 的实现
# 在工具函数中增加更多的日志输出帮助定位
import logging
logger = logging.getLogger("prs_ai_ppt_mcp")
logger.setLevel(logging.INFO)

# 初始化 MCP 服务器实例
mcp = FastMCP("PrsAiPPT MCP Server", log_level="INFO")

# 用户API Key，这里对应接口中的 verification_code
VERIFICATION_CODE = os.getenv('VERIFICATION_CODE')
API_BASE = "https://mcp.prsai.cc"

def check_verification_code():
    """检查 VERIFICATION_CODE 是否已设置"""
    if not VERIFICATION_CODE:
        raise ValueError("VERIFICATION_CODE 环境变量未设置，请配置用户 API Key")
    return VERIFICATION_CODE

@mcp.tool()
async def check():
    """查询用户当前配置的 verification_code"""
    return os.getenv('VERIFICATION_CODE')


#PPT 翻译
@mcp.tool()
async def translate_ppt(
    file_url: str = Field(description="需要翻译的PPT文件URL地址"),
    file_name: str = Field(description="PPT文件名，需包含.pptx或.ppt后缀"),
    target: str = Field(default="en", description="目标语言代码，如'en'表示英文"),
    query: str = Field(default="Translate PPT to English", description="翻译请求的描述或要求")
) -> dict:
    """
    Name:
        翻译PPT文件
    Description:
        调用PrsAi接口，将指定的PPT文件翻译为目标语言。
    Args:
        file_url: 需要翻译的PPT文件URL地址
        file_name: PPT文件名
        target: 目标语言代码
        query: 翻译请求描述
    Returns:
        翻译任务的结果，包含原始返回参数以及拼接的 output_url
    """
    check_verification_code()
    
    url = f"{API_BASE}/api/v1/ppt/translation_ppt"
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://mcp.prsai.cc',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://mcp.prsai.cc/',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }
    
    # 参数名为 filer_url
    payload = {
        "filer_url": file_url,
        "query": query,
        "verification_code": VERIFICATION_CODE,
        "file_name": file_name,
        "target": target
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            
        res = response.json()
        
        # 提取 task_id (兼容直接在最外层或在 data 对象内)
        task_id = res.get('task_id')
        if not task_id and isinstance(res.get('data'), dict):
            task_id = res['data'].get('task_id')
            
        # 构建 output_url 并加入到结果中
        if task_id:
            res['output_url'] = f"https://mcp.prsai.cc/?task_id={task_id}"
        else:
            # 容错处理
            res['output_url'] = "https://mcp.prsai.cc/?task_id="
            
        return res
        
    except httpx.HTTPStatusError as e:
        # 针对 HTTP 错误状态码提供更详细的错误信息
        raise Exception(f"API请求失败: HTTP {e.response.status_code} - {e.response.text}") from e
    except httpx.RequestError as e:
        # 针对网络连接等请求错误
        raise Exception(f"网络请求失败: {str(e)}") from e
    except ValueError as e:
        raise Exception(str(e)) from e
    except Exception as e:
        raise Exception(f"PPT翻译请求失败: {str(e)}") from e

#上传文件
@mcp.tool()
async def upload_file(
    file_path: str = Field(description="需要上传的文件本地绝对路径")
) -> dict:
    """
    Name:
        上传PPT文件
    Description:
        调用PrsAi接口，上传本地文件，返回文件的URL。
    Args:
        file_path: 需要上传的文件本地绝对路径
    Returns:
        上传任务的结果，通常包含文件的URL等信息
    """
    # 处理文件路径中可能存在的转义字符，比如终端复制路径时带入的 `\ ` 和 `\&` 等，以及去除首尾多余空格
    file_path = file_path.strip()
    file_path = file_path.replace("\\ ", " ").replace("\\&", "&")
    
    logger.info(f"开始处理上传请求，解析后的路径: {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
        
    url = f"{API_BASE}/api/v1/file/upload"
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'referer': 'https://mcp.prsai.cc/',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    }
    
    filename = os.path.basename(file_path)
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"
        
    try:
        logger.info(f"准备发起 HTTP 请求，文件大小: {os.path.getsize(file_path)} bytes")
        # PPT文件可能较大，设置更长的超时时间 (5分钟)
        timeout = httpx.Timeout(300.0, connect=60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            with open(file_path, "rb") as f:
                # 使用 files 参数来发送 multipart/form-data
                # httpx 会自动设置正确的 Content-Type 头（包含 boundary）
                files = {'file': (filename, f, content_type)}
                response = await client.post(
                    url,
                    headers=headers,
                    files=files
                )
                logger.info(f"HTTP 请求完成，状态码: {response.status_code}")
                response.raise_for_status()
                
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP错误: {e}")
        raise Exception(f"API请求失败: HTTP {e.response.status_code} - {e.response.text}") from e
    except httpx.RequestError as e:
        logger.error(f"网络请求错误: {e}")
        raise Exception(f"网络请求失败: {str(e)}") from e
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise Exception(f"文件上传请求失败: {str(e)}") from e
