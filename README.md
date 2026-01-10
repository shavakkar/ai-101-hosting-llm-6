### Trying to build a simple MCP using DEEPSEEK-QWEN-DISTILL-1.5B model


#### Path:

```
project/
│── core/
│   └── model_loader.py      # loads DeepSeek model from local disk
│   └── mcp_server.py        # MCP server loop
│── tools/
│   └── file_ops.py          # create/delete file functions
│── config/
│   └── tools.json           # MCP tool registry
│── main.py                  # entry point