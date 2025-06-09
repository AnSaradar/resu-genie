from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
import cohere
import logging
import json
import re

class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.3):
        
        self.api_key = api_key
        
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)

        self.enums = CoHereEnums

        self.logger = logging.getLogger(__name__)
    

    def set_generation_model(self, model_id : str):
        self.generation_model = model_id

    def set_embedding_model(self, model_id : str, embedding_size : int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
    
    def generate_text(self, prompt : str, chat_history : list = [], max_output_tokens : int = None,
                      temperature : float = None) -> str:

        if not self.client:
            self.logger.error("CoHere client not initialized.")
            return None

        if not self.generation_model_id:
            self.logger.error("CoHere Embedding model not set")
            return None
        

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens

        temperature = temperature if temperature else self.default_generation_temperature
        
        response  = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = self.construct_prompt(prompt = prompt, role = CoHereEnums.USER.value),
            temperature = temperature,
            max_tokens = max_output_tokens
        )

        if not response or not response.text:
            self.logger.error("CoHere Client : Failed to generate text.")
            return None

        return response.text

    def generate_json_response(self, prompt: str, chat_history: list = [], max_output_tokens: int = None,
                              temperature: float = None) -> dict:
        """Generate a structured JSON response using enhanced prompting for CoHere"""
        
        if not self.client:
            self.logger.error("CoHere client not initialized.")
            raise Exception("CoHere client not initialized")

        if not self.generation_model_id:
            self.logger.error("CoHere generation model not set")
            raise Exception("Generation model not set")

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        
        # Enhance the prompt to ensure JSON output
        enhanced_prompt = f"""{prompt}

IMPORTANT: You must respond ONLY with valid JSON. Do not include any text before or after the JSON object. Your response should start with {{ and end with }}.

Example format:
{{
  "score": 8,
  "message": "Your evaluation message here",
  "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
}}"""

        try:
            response = self.client.chat(
                model=self.generation_model_id,
                chat_history=chat_history,
                message=self.construct_prompt(prompt=enhanced_prompt, role=CoHereEnums.USER.value),
                temperature=temperature,
                max_tokens=max_output_tokens
            )

            if not response or not response.text:
                self.logger.error("CoHere Client: Failed to generate JSON response.")
                raise Exception("Failed to generate response from CoHere")

            json_text = response.text.strip()
            self.logger.info(f"CoHere JSON response: {json_text}")

            # Extract JSON from response if there's extra text
            json_match = re.search(r'\{.*\}', json_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)

            try:
                return json.loads(json_text)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response from CoHere: {json_text}")
                raise Exception(f"Invalid JSON response from CoHere: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error generating JSON response with CoHere: {str(e)}")
            raise e

    def embed_text(self, text : str, document_type : str = None):

        if not self.client:
            self.logger.error("CoHere client not initialized.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("CoHere Embedding model not set.")
            return None
        
        input_type = CoHereEnums.DOCUMENT.value 
        if document_type == DocumentTypeEnum.QUERY:
            input_type = CoHereEnums.QUERY.value

        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [self.process_text(text)],
            input_type = input_type,
            embedding_types = ['float'],

        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("CoHere Client : Failed to embed text.")
            return None

        return response.embeddings.float[0]
        


    def construct_prompt(self, prompt : str, role : str):
        return {
            "role" : role,
            "content" : self.process_text(text = prompt),
        }

    def process_text(self, text : str):
        return text[:self.default_input_max_characters].strip()


