from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def load_model(model_path="/models/deepseek-qwen-distill-1.5b"):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        dtype=torch.float16,
        device_map="auto"   # auto-detect CPU/GPU
    )
    return model, tokenizer
