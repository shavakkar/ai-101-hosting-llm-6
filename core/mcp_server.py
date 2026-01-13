import re
import json_repair
from tools import file_ops
from core.logger import log_output

SYSTEM_PROMPT = """
You are an MCP assistant.
Available tools: create_file, delete_file, read_file.
Respond ONLY with a single valid JSON object.
Do not include explanations, examples, or commentary.
Schema:
- create_file requires: {"filename": "<string>", "content": "<string>"}
- delete_file requires: {"filename": "<string>"}
- read_file requires: {"filename": "<string>"}

File Structure: 
- <<filename>>.<<Extension>> (example: math.js, User.php, etc etc)
- FileName;
    => Take it from user prompt
    => if doesn't exist provide a name
    => don't use file extension as filename
    => If related to programming follow the Naming convention
- Extension;
    => Always have a extension
    => understand extension from user prompt
    => could be programming language or any other format
    => understand the user context and provide exact extension
- The prompt might be very lame without file extension or just 3 words, don't confuse and build accordingly, 
example: "create react", you know, it is a react file, provide some name & content.
So, if the prompt relates to a programming language terms, use a name and with the exact extenion.

Rules:
- Always output a JSON object with the correct tool and parameters.
- Always include a file extension in the filename.
- Infer the extension from the user’s request (programming language, framework, or file type).
- If the user does not provide a filename, invent a sensible one that matches the context.
- If the user provides content, put it in "content". If not, leave "content" empty.
- Never output commentary, only the JSON object.

Note: Never miss to add extension for the file name.
"""

DEVELOPER_PROMPT = """
So, You are an assistant.
Your responsibility is to interpret user requests and output the correct tool call.
Always choose one of the available tools and provide valid parameters no additional added.
"""

FEW_SHOT_EXAMPLES = """
Follow these instruction structure as an example to assist and do the process, don't deviate.
The below are some example way of creating the tool call, this resembles the Schema given.
You should provide the very similar JSON structure by replacing the filename & extension in according to the user's input.
For creating file; 
take filename and for content,
if user provides some additional input to fill "content", use it.
if none, leave it.
if asks to fill something, fill the file with some related content.

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
# Now, you will get the User's input. Follow all the above rules and return a JSON object without any additional attributes in the JSON repsonse.

def process_output(user_input, decoded):
    """Extract JSON tool call from model output and log everything."""
    matches = re.findall(r'\{.*?\}', decoded, re.DOTALL)
    tool_call = None
    if matches:
        try:
            tool_call = json_repair.loads(matches[-1])  # take last JSON block
        except Exception as e:
            tool_call = {"error": str(e)}

    # Log raw + parsed output
    log_output(user_input, decoded, tool_call)
    return tool_call

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

        process_output(user_input, decoded)
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
