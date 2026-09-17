from transformers import pipeline
from typing import Any

class Assistant:
    model: Any = pipeline("text-generation",
            model="Qwen/Qwen3-0.6B",
            device="cpu",
            torch_dtype="float32",
            clean_up_tokenization_spaces=False)


    def generate_response(self, prompt: str) -> str:
        response = self.model(prompt, max_length=100, num_return_sequences=1)
        return response[0]['generated_text']