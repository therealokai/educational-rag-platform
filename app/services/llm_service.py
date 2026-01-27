from langchain_openai import ChatOpenAI
from app.core.config import settings
from openai import OpenAI

class LLMService:
    def __init__(self, model_name=None, temperature: float = 0.7):
        self.model_name = model_name if model_name else settings.MODEL_NAME
        self.temperature = temperature

    def get_agent_llm(self):
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=settings.OPENAI_API_KEY
        )
    def get_llm(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self.client
    
    def predict_messages(self, prompt,system_prompt = None, base_64_image = None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if base_64_image:
            prompt = [
                { "type": "input_text", "text": prompt },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base_64_image}",
                },
            ]
            messages.append({"role": "user", "content": prompt})
        else:
            messages.append({"role": "user", "content": prompt})
        llm = self.get_llm()
        response = llm.responses.create(
            model=self.model_name,
            input=messages,
            temperature=self.temperature
        )
        return response.output_text
