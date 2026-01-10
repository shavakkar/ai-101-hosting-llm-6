### Trying to build a simple MCP using DEEPSEEK-QWEN-DISTILL-1.5B model


#### Path:

```
project/
│── core/
|   └── __init__.py
│   └── model_loader.py      # loads DeepSeek model from local disk
│   └── mcp_server.py        # MCP server loop
│── tools/
|   └── __init__.py
│   └── file_ops.py          # create/delete file functions
│── config/
|   └── __init__.py
│   └── tools.json           # MCP tool registry
│── main.py                  # entry point
└── __init__.py