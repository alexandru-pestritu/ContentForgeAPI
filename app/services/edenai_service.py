import json
import os
import httpx
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

class EdenAIService:
    def __init__(self):
        """
        Initializes the EdenAIService with the base URL and API key from environment variables.
        """
        self.base_url = "https://api.edenai.run/v2"
        self.api_key = os.getenv("EDENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing EdenAI API key in environment variables.")

    async def get_providers_and_models(self, feature_name: str, subfeature_name: str) -> dict:
        """
        Retrieves providers and models with their associated costs.

        :param feature_name: The feature name (e.g., 'text').
        :param subfeature_name: The subfeature name (e.g., 'chat').
        :return: A dictionary with providers, their models, and costs.
        """
        url = f"{self.base_url}/info/provider_subfeatures"
        params = {
            'feature__name': feature_name,
            'subfeature__name': subfeature_name
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=60.0)
                response.raise_for_status() 
        except httpx.HTTPStatusError as http_err:
            raise ValueError(f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}")
        except httpx.RequestError as req_err:
            raise ValueError(f"Request error occurred: {str(req_err)}")
        except Exception as err:
            raise ValueError(f"Unexpected error occurred: {str(err)}")

        try:
            response_json = response.json()
        except json.JSONDecodeError:
            raise ValueError("Failed to decode JSON response from EdenAI API")

        formatted_data = {}
        for provider in response_json:
            provider_name = provider['provider']['name']
            if provider_name not in formatted_data:
                formatted_data[provider_name] = []

            for pricing in provider.get('pricings', []):
                model_name = pricing.get('model_name', 'unknown')
                price = float(pricing.get('price', 0.0))
                price_unit_quantity = pricing.get('price_unit_quantity', 1)
                price_unit_type = pricing.get('price_unit_type', 'tokens')

                if price_unit_quantity == 1000:
                    price_display = f"${price:.4f} per 1K {price_unit_type}"
                elif price_unit_quantity == 1000000:
                    price_display = f"${price:.4f} per 1M {price_unit_type}"
                else:
                    price_display = f"${price:.4f} per {price_unit_quantity} {price_unit_type}"

                formatted_data[provider_name].append({
                    "model": model_name,
                    "cost": price_display
                })

        return formatted_data

    async def execute_chat_prompt(self, providers: List[str], text: str, temperature: float = 0.1, max_tokens: int = 4096) -> Dict[str, Dict[str, float]]:
        """
        Executes a chat prompt on the specified providers and returns the generated text and cost.

        :param providers: List of provider names to use.
        :param text: The input text for the chat prompt.
        :param temperature: The temperature setting for the model (default 0.1).
        :param max_tokens: The maximum number of tokens to generate (default 4096).
        :return: A dictionary with provider names as keys and a dictionary of generated text and cost as values.
        """
        url = f"{self.base_url}/text/chat"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            "providers": providers,
            "text": text,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=60.0)
                response.raise_for_status() 
        except httpx.HTTPStatusError as http_err:
            raise ValueError(f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}")
        except httpx.RequestError as req_err:
            raise ValueError(f"Request error occurred: {str(req_err)}")
        except Exception as err:
            raise ValueError(f"Unexpected error occurred: {str(err)}")

        try:
            response_json = response.json()
        except json.JSONDecodeError:
            raise ValueError("Failed to decode JSON response from EdenAI API")

        results = {}
        for provider_name, data in response_json.items():
            generated_text = data.get('generated_text', '')
            cost = data.get('cost', 0.0)
            results[provider_name] = {
                "generated_text": generated_text,
                "cost": cost
            }

        return results
