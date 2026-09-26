from openai import AsyncOpenAI
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class LLMProcessor:
    MODELS = {
        'fast': os.getenv('TASKTICKET_AI_MODEL', 'qwen/qwen3.7-flash'),
        'smart': os.getenv('TASKTICKET_AI_MODEL', 'qwen/qwen3.7-flash'),
        'balanced': os.getenv('TASKTICKET_AI_MODEL', 'qwen/qwen3.7-flash')
    }

    def __init__(self):
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            max_retries=0,
            timeout=10,
            http_client=httpx.AsyncClient(
                timeout=10,
                headers={
                    "HTTP-Referer": "http://localhost:5000",
                    "X-Title": "TaskTicket"
                }
            )
        )

    async def process(self, 
                     prompt: str, 
                     model_type: str = 'balanced',
                     system_prompt: str = None,
                     temperature: float = 0.7,
                     max_tokens: int = 1500) -> str:
        """
        Process a prompt using the specified model type and parameters.
        
        Args:
            prompt: The user prompt to process
            model_type: 'fast', 'smart', or 'balanced'
            system_prompt: Optional system prompt to set context
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens in response
        
        Returns:
            Processed response from the LLM
        """
        try:
            model = self.MODELS.get(model_type, self.MODELS['balanced'])
            
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system", 
                    "content": system_prompt
                })
            messages.append({
                "role": "user", 
                "content": prompt
            })

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_body={"reasoning": {"enabled": False}}
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Optional AI unavailable ({type(e).__name__}); local selection remains available.")
            return ""

    async def analyze_task_completion(self, 
                                    task: Dict, 
                                    completion_history: List[Dict]) -> Dict:
        """
        Analyze task completion patterns and provide insights.
        
        Args:
            task: Current task information
            completion_history: History of task completions
            
        Returns:
            Dictionary containing analysis and suggestions
        """
        try:
            prompt = f"""Analyze this task and its completion history:

Task: {task['title']}
Recent completion history: {completion_history[-5:] if completion_history else 'No history'}

Provide insights about:
1. Completion patterns
2. Suggested modifications to make the task more achievable
3. Motivation tips based on past performance

Format response as JSON:
{{
    "patterns": "observed patterns in completion",
    "suggestions": "task modification suggestions",
    "motivation": "personalized motivation message"
}}
"""
            response = await self.process(
                prompt=prompt,
                model_type='fast',
                system_prompt="You are a task analysis AI that helps users improve task completion rates.",
                temperature=0.7
            )
            
            try:
                import json
                return json.loads(response)
            except json.JSONDecodeError:
                print("Error parsing LLM response for task analysis")
                return {
                    "patterns": "Unable to analyze patterns",
                    "suggestions": "Continue with original task format",
                    "motivation": "Keep going!"
                }

        except Exception as e:
            print(f"Error in task completion analysis: {str(e)}")
            return {
                "patterns": "Analysis unavailable",
                "suggestions": "Proceed with task as is",
                "motivation": "You can do this!"
            }
