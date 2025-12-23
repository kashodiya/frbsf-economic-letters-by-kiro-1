"""LLM service for generating insights using AWS Bedrock."""

import json
import logging
import os
from typing import Optional
import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with AWS Bedrock LLM."""
    
    def __init__(self, region: str, model_id: str, profile: Optional[str] = None):
        """
        Initialize the LLM service.
        
        Args:
            region: AWS region (e.g., 'us-east-1')
            model_id: Bedrock model ID
            profile: AWS profile name (optional)
        """
        self.region = region
        self.model_id = model_id
        self.profile = profile
        
        # Initialize Bedrock client
        try:
            session_kwargs = {'region_name': region}
            if profile:
                session_kwargs['profile_name'] = profile
            
            session = boto3.Session(**session_kwargs)
            self.client = session.client('bedrock-runtime', region_name=region)
            
            logger.info(f"Initialized Bedrock client with model {model_id} in region {region}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    async def generate_insight(self, letter_content: str, question: str) -> str:
        """
        Generate an insight/answer for a question about a letter.
        
        Args:
            letter_content: The full content of the economic letter
            question: The user's question
            
        Returns:
            The LLM's answer
        """
        try:
            prompt = self._build_prompt(letter_content, question)
            
            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            }
            
            logger.info(f"Invoking Bedrock model {self.model_id}")
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract answer from Claude response
            if 'content' in response_body and len(response_body['content']) > 0:
                answer = response_body['content'][0]['text']
            else:
                answer = "I apologize, but I couldn't generate a response. Please try again."
            
            logger.info("Successfully generated insight")
            return answer
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"AWS ClientError ({error_code}): {error_message}")
            raise Exception(f"Failed to generate insight: {error_message}")
        except BotoCoreError as e:
            logger.error(f"BotoCoreError: {e}")
            raise Exception(f"AWS service error: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating insight: {e}")
            raise Exception(f"Failed to generate insight: {str(e)}")
    
    def _build_prompt(self, letter_content: str, question: str) -> str:
        """
        Build the prompt for the LLM.
        
        Args:
            letter_content: The letter content
            question: The user's question
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert economist analyzing Federal Reserve Bank of San Francisco economic letters. 

Here is an economic letter:

<letter>
{letter_content}
</letter>

Please answer the following question about this letter:

<question>
{question}
</question>

Provide a clear, concise, and informative answer based on the content of the letter. If the letter doesn't contain enough information to fully answer the question, acknowledge this and provide what insights you can based on the available content."""

        return prompt
