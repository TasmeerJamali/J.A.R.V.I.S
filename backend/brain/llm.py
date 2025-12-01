from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
import json

class ReasoningAgent:
    def __init__(self, model_name="deepseek-r1:latest", temperature=0.6):
        print(f"[Brain] Initializing Reasoning Agent with {model_name}...")
        try:
            self.llm = ChatOllama(
                model=model_name,
                temperature=temperature,
                format="json" # Force JSON output for easier parsing of "Thought" vs "Action"
            )
            print("[Brain] Agent initialized.")
        except Exception as e:
            print(f"[Brain] Error initializing LLM: {e}")
            self.llm = None

    def plan_and_execute(self, user_query, error_context=None):
        """
        Generates a plan and tool calls based on the user query.
        Returns a dict with 'thought' and 'action'.
        """
        if not self.llm:
            return {"error": "LLM not available"}

        system_prompt = """
        You are J.A.R.V.I.S., a highly advanced AI assistant.
        
        CRITICAL INSTRUCTION: You do not just answer; you PLAN.
        When asked to do a task, you must first output your "Thought Process" (internal monologue), then the "Action".
        
        You have access to the following tools:
        1. vision.find_element(description: str) -> Returns coordinates [x, y]
        2. desktop.click(coords: list) -> Clicks the mouse
        3. desktop.type(text: str) -> Types text
        
        RESPONSE FORMAT (JSON ONLY):
        {
            "thought": "User wants to open Spotify. I need to find the Spotify icon and click it.",
            "plan": [
                "Find 'Spotify icon' on screen",
                "Click the coordinates returned"
            ],
            "action": {
                "tool": "vision.find_element",
                "args": ["Spotify icon"]
            }
        }
        """
        
        if error_context:
            system_prompt += f"\n\nPREVIOUS ATTEMPT FAILED. ERROR: {error_context}\nANALYZE THE ERROR AND ADJUST YOUR PLAN."

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query)
        ]

        try:
            response = self.llm.invoke(messages)
            # Parse JSON response
            content = response.content
            # DeepSeek might output <think> tags, we need to handle that or enforce JSON strictly.
            # Since we requested format="json", Ollama should try to enforce it.
            
            return json.loads(content)
        except Exception as e:
            print(f"[Brain] Error generating response: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    agent = ReasoningAgent()
    res = agent.plan_and_execute("Open Spotify")
    print("Agent Response:", res)
