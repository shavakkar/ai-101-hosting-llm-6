from core.model_loader import load_model
from core.mcp_server import run_mcp_server

model_path = r"C:/Softwares/LLMS/deepseek-r1-distill-qwen-1.5b"

if __name__ == "__main__":
    model, tokenizer = load_model(model_path)
    run_mcp_server(model, tokenizer)
