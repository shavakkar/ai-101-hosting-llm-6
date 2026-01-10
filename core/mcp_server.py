import re
import json
from tools import file_ops

SYSTEM_PROMPT = """
You are an MCP assistant. 
Respond ONLY with a single JSON tool call.

Format:
{"tool": "<tool_name>", "params": { ... }}
"""

def route_tool_call(tool_name, params):
    if tool_name == "create_file":
        return file_ops.create_file(params["filename"], params.get("content", ""))
    elif tool_name == "delete_file":
        return file_ops.delete_file(params["filename"])
    elif tool_name == "read_file":
        return file_ops.read_file(params["filename"])
    else:
        return {"status": "error", "message": f"Unknown tool {tool_name}"}

def run_mcp_server(model, tokenizer):
    print("MCP server running... type a command like 'create a file named test.txt'")
    while True:
        user_input = input(">> ")

        # Build prompt with system instruction
        prompt = SYSTEM_PROMPT + "\nUser: " + user_input + "\nAssistant:"

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            pad_token_id=tokenizer.eos_token_id  # fixes warning
        )
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print("Raw model output:", decoded)

        # Extract first JSON block from output
        match = re.search(r'\{.*\}', decoded, re.DOTALL)
        if match:
            try:
                tool_call = json.loads(match.group(0))
                tool_name = tool_call["tool"]
                params = tool_call["params"]
                response = route_tool_call(tool_name, params)
            except Exception as e:
                response = {"status": "error", "message": f"Failed to parse tool call: {e}"}
        else:
            response = {"status": "error", "message": "No valid JSON found"}

        print("Response:", response)
