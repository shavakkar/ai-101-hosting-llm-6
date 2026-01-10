import re
import json_repair
from tools import file_ops

SYSTEM_PROMPT = """
You are an MCP assistant.
Available tools: create_file, delete_file, read_file.
Respond ONLY with a single valid JSON object.
Do not include explanations, examples, or commentary.
Schema:
- create_file requires: {"filename": "<string>", "content": "<string>"}
- delete_file requires: {"filename": "<string>"}
- read_file requires: {"filename": "<string>"}
"""

DEVELOPER_PROMPT = """
So, You are an assistant.
Your responsibility is to interpret user requests and output the correct tool call.
You must always choose one of the available tools and provide valid parameters.
"""

FEW_SHOT_EXAMPLES = """
Follow these instruction structure to assist, don't deviate.

User: create a file called hello.txt
Assistant: {"tool": "create_file", "params": {"filename": "hello.txt", "content": ""}}

User: delete hello.txt
Assistant: {"tool": "delete_file", "params": {"filename": "hello.txt"}}

User: read hello.txt
Assistant: {"tool": "read_file", "params": {"filename": "hello.txt"}}
"""

# def normalize_tool(tool_name):
#     synonyms = {
#         "readme": "create_file",
#         "file": "create_file"
#     }
#     return synonyms.get(tool_name, tool_name)

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
        prompt = SYSTEM_PROMPT + "\n" + FEW_SHOT_EXAMPLES + "\n" + DEVELOPER_PROMPT
        prompt += "\nUser: " + user_input + "\nAssistant:"

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=80,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print("Raw model output:", decoded)

        # Extract first JSON block from output
        match = re.findall(r'\{.*?\}', decoded, re.DOTALL)
        if match:
            try:
                tool_call = json_repair.loads(match.group(0))
                tool_name = tool_call["tool"]
                params = tool_call["params"]
                response = route_tool_call(tool_name, params)
            except Exception as e:
                response = {"status": "error", "message": f"Failed to parse tool call: {e}"}
        else:
            response = {"status": "error", "message": "No valid JSON found"}

        print("Response:", response)
