from transformers import pipeline, AutoTokenizer, GenerationConfig
from ..Chunker.DataModels import MinimalSource
from ..Chunker.DataModels import MinimalSearchResults, MinimalAnswer
from typing import Any, List


class Assistant:
    """
    The class storing and setting up the LLM to anwser questions using sources.
    """
    model: Any = pipeline("text-generation",
                          model="Qwen/Qwen3-0.6B",
                          device="cpu",
                          dtype="float32",
                          clean_up_tokenization_spaces=False)
    tokenizer: Any = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    rules_path: str = "src/Model/rulePrompts/ruleprompt.txt"

    def generate_response(self, MSR: MinimalSearchResults) -> MinimalAnswer:
        """
        Will generate a response for a question using the sources given.
        """
        tokenizer = self.tokenizer
        Messages = [{"role": "user",
                     "content": self.BuildPrompt(MSR.question,
                                                 MSR.retrieved_sources)}]
        template = tokenizer.apply_chat_template(Messages, tokenize=False,
                                                 add_generation_prompt=True,
                                                 enable_thinking=False)
        GC = GenerationConfig
        config = GC(do_sample=False,
                    max_new_tokens=250,
                    num_return_sequences=1,
                    temperature=None,
                    top_p=None,
                    top_k=None)  # type: ignore[no-untyped-call, unused-ignore]
        config.max_length = None
        config.temperature = None
        config.top_p = None
        config.top_k = None

        response = self.model(template,
                              generation_config=config)
        Anwser = MinimalAnswer(
            retrieved_sources=MSR.retrieved_sources,
            question=MSR.question,
            question_id=MSR.question_id,
            answer=str(response[0]['generated_text'].split("</think>\n\n")[1]),
            )
        return Anwser

    def BuildPrompt(self, question: str, sources: List[MinimalSource]) -> str:
        """
        Set up the prompt for the LLM to use and set up its context.
        """
        text = ""
        rules = ""
        index = 1
        for i in sources:
            text += f"\n{i.text_value}\n"
            index += 1
            with open(self.rules_path, "r") as f:
                rules = f.read()
        return f"""
            {rules}
            ### Input Format:
            <context>
                {text}
            </context>

            <question>
                {question}
            </question>

            ### Your Response:
                """
