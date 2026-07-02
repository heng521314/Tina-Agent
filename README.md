## Tina-Agent

> Tina-Agent是由langchain构建的agent聊天项目，支持联网搜索，工具调用，多模态等，功能开发参考`deer-flow`，目标是打造简单高效的使用体验

### 已实现功能：

- 聊天功能：支持用户自定义模型配置，兼容OpenAI格式聊天接口
- 生成建议：根据最近聊天记录，生成用户感兴趣的建议
- 自定义中间件：动态传递提示词，工具拦截，自动清理聊天上下文窗口
- 持久化保存用户聊天记录(mongoDB)
- 支持图片文件上传：用户可以上传图片文件，支持jpg、png、pdf等
- 支持上传skill压缩包，自动解压，并由agent在合适的时机调用
- 工具调用支持：内置多个工具，如读写文件，网络搜索，查询天气，执行命令，发送请求提取文本等
- 最小化开发：只保留核心功能，方便自定义扩展

**持续开发中...**

### 快速开始

1.克隆仓库

```bash
git clone https://github.com/heng521314/Tina-Agent.git
cd Tina-Agent
```

2.安装依赖

```bash
uv sync
```

3.运行项目

```bash
cd backend/app/gateway
fastapi run app.py
```

恭喜你成功运行了项目🎉

**特别感谢以下项目**

- [deer-flow](https://github.com/bytedance/deer-flow)
- [langchain](https://github.com/hwchase17/langchain)