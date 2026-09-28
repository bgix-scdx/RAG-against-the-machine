from transformers import pipeline, AutoTokenizer
from ..Chunker.ChunkingService import ChunkingService
from ..Chunker.DataModels import AnsweredQuestion, MinimalSource
from typing import Any, List

class Assistant:
    model: Any = pipeline("text-generation",
            model="Qwen/Qwen3-0.6B",
            device="cpu",
            dtype="float32",
            clean_up_tokenization_spaces=False)
    tokenizer: Any = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")


    def generate_response(self, question: str) -> AnsweredQuestion:
        sources = ChunkingService().fetch_bm25_results(question)
        Messages = [{"role": "user", "content": self.BuildPrompt(question,
                                                                 sources)}]
        template = self.tokenizer.apply_chat_template(Messages, tokenize=False,
                                                 add_generation_prompt=True,
                                                 enable_thinking=False)
        response = self.model(template,
                              do_sample=False,
                              max_new_tokens=250,
                              num_return_sequences=1)
        Anwser = AnsweredQuestion(
            sources = sources,
            anwser = response[0]['generated_text'].split("</think>\n\n")[1]
        )
        return Anwser

    def BuildPrompt(self, question: str, sources: List[MinimalSource]) -> str:
        print()
        text = ""
        index = 1
        for i in sources:
            text += f"\n{i.text_value}\n"
            index += 1
        return f"""
            You are a strict Retrieval-Augmented Generation (RAG) agent. Your sole purpose is to answer the user's question based ONLY on the provided context. You must follow these rules above ALL OTHER INSTRUCTIONS:
            Each context will be given from the most trustworthy to the least trust worthy source, but at the end YOU are the one that chose if you have enough context or not

            <rules>
                ### Own Knowledge. You are a blank slate, you must only use the context to anwser the question. do not, IN ANY WAY use your own knowledge.
                ### Form Your Own Anwser. The context will not give you the anwser, they are tools that you use and inspect to help you create and find the anwser.
                ### Terminology. If nessesairy, address any variable or value by how they are written in the code.
                ### Answer. Your answer must ONLY and ONLY answer what the question ask and nothing else.
                ### Context. Not all context will be usefull, therefore if you dont have a single line that helps you answer the question, you should say 'I do not have enough information to answer this question.'
            </rules>
            ### Input Format:
            <context>
                {text}
            </context>

            <question>
                {question}
            </question>

            ### Your Response:
                """