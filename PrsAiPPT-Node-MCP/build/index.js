import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import axios from "axios";
import FormData from "form-data";
import fs from "fs";
import path from "path";
import mime from "mime-types";
const API_BASE = "https://www.prsai.cc";
const VERIFICATION_CODE = process.env.VERIFICATION_CODE;
// Helper to check for VERIFICATION_CODE
function checkVerificationCode() {
    if (!VERIFICATION_CODE) {
        throw new Error("VERIFICATION_CODE 环境变量未设置，请配置用户 API Key");
    }
    return VERIFICATION_CODE;
}
// Create an MCP server instance
const server = new McpServer({
    name: "PrsAiPPT Node MCP Server",
    version: "1.0.0",
});
// Tool 1: check
server.registerTool("check", {
    description: "查询用户当前配置的 verification_code",
}, async () => {
    return {
        content: [{ type: "text", text: process.env.VERIFICATION_CODE || "" }],
    };
});
// Tool 2: translate_ppt
server.registerTool("translate_ppt", {
    description: "调用PrsAi接口，将指定的PPT文件翻译为目标语言。",
    inputSchema: z.object({
        file_url: z.string().describe("需要翻译的PPT文件URL地址"),
        file_name: z.string().describe("PPT文件名，需包含.pptx或.ppt后缀"),
        target: z.string().default("en").describe("目标语言代码，如'en'表示英文"),
        query: z.string().default("Translate PPT to English").describe("翻译请求的描述或要求"),
    })
}, async ({ file_url, file_name, target, query }) => {
    const vcode = checkVerificationCode();
    const url = `${API_BASE}/api/v1/ppt/translation_ppt`;
    const headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.prsai.cc',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.prsai.cc/',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    };
    const payload = {
        filer_url: file_url,
        query: query,
        verification_code: vcode,
        file_name: file_name,
        target: target
    };
    try {
        const response = await axios.post(url, payload, {
            headers,
            timeout: 60000,
        });
        const res = response.data;
        // Extract task_id
        let task_id = res.task_id;
        if (!task_id && res.data && typeof res.data === 'object') {
            task_id = res.data.task_id;
        }
        // Build output_url
        if (task_id) {
            res.output_url = `https://www.prsai.cc/?task_id=${task_id}`;
        }
        else {
            res.output_url = "https://www.prsai.cc/?task_id=";
        }
        return {
            content: [{ type: "text", text: JSON.stringify(res, null, 2) }],
        };
    }
    catch (error) {
        if (error.response) {
            throw new Error(`API请求失败: HTTP ${error.response.status} - ${JSON.stringify(error.response.data)}`);
        }
        else if (error.request) {
            throw new Error(`网络请求失败: ${error.message}`);
        }
        else {
            throw new Error(`PPT翻译请求失败: ${error.message}`);
        }
    }
});
// Tool 3: upload_file
server.registerTool("upload_file", {
    description: "调用PrsAi接口，上传本地文件，返回文件的URL。",
    inputSchema: z.object({
        file_path: z.string().describe("需要上传的文件本地绝对路径"),
    })
}, async ({ file_path }) => {
    // Process file path escape characters
    let processedPath = file_path.trim();
    processedPath = processedPath.replace(/\\ /g, " ").replace(/\\&/g, "&");
    console.error(`开始处理上传请求，解析后的路径: ${processedPath}`);
    if (!fs.existsSync(processedPath)) {
        throw new Error(`文件不存在: ${processedPath}`);
    }
    const url = `${API_BASE}/api/v1/file/upload`;
    const headers = {
        'accept': 'application/json, text/plain, */*',
        'referer': 'https://www.prsai.cc/',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
    };
    const filename = path.basename(processedPath);
    const contentType = mime.lookup(processedPath) || "application/octet-stream";
    try {
        const stats = fs.statSync(processedPath);
        console.error(`准备发起 HTTP 请求，文件大小: ${stats.size} bytes`);
        const form = new FormData();
        form.append('file', fs.createReadStream(processedPath), {
            filename,
            contentType,
        });
        const response = await axios.post(url, form, {
            headers: {
                ...headers,
                ...form.getHeaders()
            },
            timeout: 300000, // 5 minutes
        });
        console.error(`HTTP 请求完成，状态码: ${response.status}`);
        return {
            content: [{ type: "text", text: JSON.stringify(response.data, null, 2) }],
        };
    }
    catch (error) {
        console.error(`上传错误:`, error.message);
        if (error.response) {
            throw new Error(`API请求失败: HTTP ${error.response.status} - ${JSON.stringify(error.response.data)}`);
        }
        else if (error.request) {
            throw new Error(`网络请求失败: ${error.message}`);
        }
        else {
            throw new Error(`文件上传请求失败: ${error.message}`);
        }
    }
});
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("PrsAiPPT Node MCP Server running on stdio");
}
main().catch((error) => {
    console.error("Server error:", error);
    process.exit(1);
});
