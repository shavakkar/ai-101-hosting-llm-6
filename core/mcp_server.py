import json
from tools.file_ops import create_file, delete_file

def route_tool_call(tool_name, params):
    if tool_name == "create_file":
        return create_file(params["filename"], params.get("content", ""))
    elif tool_name == "delete_file":
        return delete_file(params["filename"])
    else:
        return {"status": "error", "message": f"Unknown tool {tool_name}"}

def run_mcp_server(model, tokenizer):
    print("MCP server running... type a command like 'create a file named test.txt'")
    while True:
        user_input = input(">> ")

        # For now, we’ll just simulate tool routing
        if "create" in user_input:
            response = route_tool_call("create_file", {"filename": "test.txt", "content": "Hello MCP!"})
        elif "delete" in user_input:
            response = route_tool_call("delete_file", {"filename": "test.txt"})
        else:
            response = {"status": "info", "message": "No matching tool."}

        print("Response:", response)
