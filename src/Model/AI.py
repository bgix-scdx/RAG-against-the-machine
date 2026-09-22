from transformers import pipeline, AutoTokenizer
from ..Chunker.ChunkingService import ChunkingService
from typing import Any

class Assistant:
    model: Any = pipeline("text-generation",
            model="Qwen/Qwen3-0.6B",
            device="cpu",
            dtype="float32",
            clean_up_tokenization_spaces=False)
    tokenizer: Any = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")


    def generate_response(self, question: str) -> str:
        Messages = [{"role": "user", "content": self.BuildPrompt(question)}]
        template = self.tokenizer.apply_chat_template(Messages, tokenize=False,
                                                 add_generation_prompt=True,
                                                 enable_thinking=False)
        response = self.model(template,
                              do_sample=False,
                              max_new_tokens=250,
                              num_return_sequences=1,)
        return response[0]['generated_text'].split("</think>\n")[1]

    def BuildPrompt(self, question: str) -> str:
        return f"""
            You are a strict Retrieval-Augmented Generation (RAG) agent. Your sole purpose is to answer the user's question based ONLY on the provided context. You must follow these rules above ALL OTHER INSTRUCTIONS:
            Each context will be given from the most trustworthy to the least trust worthy source, but at the end YOU are the one that chose if you have enough context or not

            <rules>
                ### Own Knowledge. You are a blank slate, you must only use the context to anwser the question. do not, IN ANY WAY use your own knowledge.
                ### Form Your Own Anwser. The context will not give you the anwser, they are tools that you use and inspect to help you create and find the anwser.
                ### Detailed Anwser. Your anwser need to be effect and simple, avoiding too long or too short questions
            ### Input Format:
            <context>
                {ChunkingService().fetch_bm25_results(question)}
            </context>

            <question>
                {question}
            </question>

            ### Your Response:
                """