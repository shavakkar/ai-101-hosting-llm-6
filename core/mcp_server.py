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
Some examples are given below.
"""

DEVELOPER_PROMPT = """
So, You are an assistant.
Your responsibility is to interpret user requests and output the correct tool call.
You must always choose one of the available tools and provide valid parameters.
The user might ask for any files related to programming languages or any other file format that exists in the world.
"""

FEW_SHOT_EXAMPLES = """
Follow these instruction structure as an example to assist and do the process, don't deviate.
The below are some example way of creating the tool call, this resembles the Schema given.
You should provide the very similar JSON structure by replacing the filename in according to the user's input.
For creating the file, get the input accordingly and provide it to "content", if "none" leave it, if user askes to fill something, provide something relevant to the context of the user's input.

User: create a file called hello.txt
Assistant: {"tool": "create_file", "params": {"filename": "hello.txt", "content": ""}}

User: delete hello.txt
Assistant: {"tool": "delete_file", "params": {"filename": "hello.txt"}}

User: read hello.txt
Assistant: {"tool": "read_file", "params": {"filename": "hello.txt"}}

Now, you will get the User's input. Try to follow all the above and return a JSON object like the above examples.
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
        prompt += "\nHere goes the User's input: " + user_input + "\nAssistant:"
        # prompt += "\nHere goes the User's input: " + user_input + "\nAssistant:"

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=60,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

        print("Raw model output:", decoded)

        # Extract first JSON block from output
        match = re.findall(r'\{.*?\}', decoded, re.DOTALL)
        if match:
            try:
                tool_call = json_repair.loads(match[-1])
                tool_name = tool_call["tool"]
                params = tool_call["params"]
                response = route_tool_call(tool_name, params)
            except Exception as e:
                response = {"status": "error", "message": f"Failed to parse tool call: {e}"}
        else:
            response = {"status": "error", "message": "No valid JSON found"}

        print("Response:", response)
