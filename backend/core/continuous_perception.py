import asyncio
import time
from datetime import datetime
from PIL import ImageGrab
import json
import threading
from brain.gemini_brain import GeminiBrain
from mem0 import Memory

class ContinuousPerceptionDaemon:
    """
    The 24/7 background intelligence that watches everything.
    Uses Gemini 1.5 Flash for continuous analysis and proactive decisions.
    """
    
    def __init__(self, brain_instance=None):
        print("[PERCEPTION] Initializing 24/7 Daemon (Gemini Powered)...")
        
        # Use existing brain instance or create new one
        self.brain = brain_instance if brain_instance else GeminiBrain()
        
        # Memory system
        self.memory = Memory()
        
        # World state
        self.world_state = {
            'user_activity': 'unknown',
            'focus_level': 0.0,
            'time_on_current_task': 0,
            'active_window': 'unknown',
            'user_present': True,
            'fatigue': 'low',
            'last_task_type': 'unknown'
        }
        
        # Silence tracking (for proactive interruption)
        self.seconds_since_last_speak = 0
        self.running = False
        
    async def capture_screen_context(self):
        """Use Gemini to understand what's on screen"""
        screenshot = ImageGrab.grab()
        
        prompt = """
        Analyze this screenshot. What is the user currently doing?
        Return JSON:
        {
            "active_window": "Name of active app",
            "task_type": "coding/browsing/writing/gaming/idle",
            "errors_visible": true/false,
            "focus_indicators": "high/low"
        }
        """
        
        try:
            # We use the raw model generation here for analysis
            response = self.brain.model.generate_content([prompt, screenshot])
            text = response.text
            
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            return json.loads(text)
        except Exception as e:
            print(f"[PERCEPTION] Analysis Error: {e}")
            return {'active_window': 'unknown', 'task_type': 'unknown', 'focus_indicators': 'low'}
    
    async def analyze_user_state(self, screen_context):
        """Use webcam + heuristics to determine user state"""
        # Placeholder for integration with SecurityModule
        return {
            'present': True,
            'fatigue_level': 'low',
            'idle_time': 0
        }
    
    async def build_world_model(self, screen_ctx, user_ctx):
        """Create a unified understanding of "what's happening now" """
        
        if screen_ctx.get('task_type') != self.world_state.get('last_task_type'):
            # User switched tasks
            self.world_state['time_on_current_task'] = 0
        else:
            self.world_state['time_on_current_task'] += 30  # 30 sec sampling
        
        # Update world state
        self.world_state.update({
            'user_activity': screen_ctx.get('task_type', 'unknown'),
            'focus_level': 0.9 if screen_ctx.get('focus_indicators') == 'high' else 0.5,
            'active_window': screen_ctx.get('active_window', 'unknown'),
            'user_present': user_ctx['present'],
            'fatigue': user_ctx['fatigue_level'],
            'last_task_type': screen_ctx.get('task_type', 'unknown')
        })
        
        return self.world_state
    
    async def proactive_decision_engine(self, world_state):
        """
        CRITICAL: This is where JARVIS decides if he should INTERRUPT you.
        Uses Gemini to reason.
        """
        
        prompt = f"""
        You are JARVIS, a proactive AI assistant.
        
        CURRENT WORLD STATE:
        - User Activity: {world_state['user_activity']}
        - Duration: {world_state['time_on_current_task']} seconds
        - Active Window: {world_state['active_window']}
        - Focus Level: {world_state['focus_level']}
        - Time since I last spoke: {self.seconds_since_last_speak} seconds
        
        DECISION RULES:
        1. Respect Flow: If focus is high, DO NOT interrupt unless critical.
        2. Be Helpful: If user is stuck (same task > 300s) or has errors, offer help.
        3. Be Silent: Default to doing nothing.
        
        DECISION:
        Should you:
        A) Interrupt (speak to user)
        B) Prepare (run background task)
        C) Nothing
        
        OUTPUT JSON:
        {{
          "action": "interrupt" | "prepare" | "nothing",
          "message": "Speech text (if interrupt)",
          "reasoning": "Why?"
        }}
        """
        
        try:
            response = self.brain.model.generate_content(prompt)
            text = response.text
            
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            return json.loads(text)
        except Exception as e:
            print(f"[PERCEPTION] Decision Error: {e}")
            return {'action': 'nothing', 'reasoning': 'error'}
    
    async def execute_decision(self, decision):
        """Act on the decision"""
        
        if decision.get('action') == 'interrupt':
            msg = decision.get('message')
            print(f"[PROACTIVE] Interrupting: {msg}")
            self.seconds_since_last_speak = 0
            return msg
            
        elif decision.get('action') == 'prepare':
            print(f"[PROACTIVE] Preparing resources silently...")
            return None
        
        else:
            self.seconds_since_last_speak += 30
            return None
    
    async def run_forever(self, callback=None):
        """
        THE MAIN LOOP - This is what runs 24/7 in the background
        callback: function to call if we need to speak (thread safe)
        """
        self.running = True
        print("[PERCEPTION] Starting 24/7 monitoring loop...")
        
        while self.running:
            try:
                # 1. Capture screen
                screen_context = await self.capture_screen_context()
                
                # 2. Analyze user
                user_context = await self.analyze_user_state(screen_context)
                
                # 3. Build world model
                world_state = await self.build_world_model(screen_context, user_context)
                
                # 4. Store in memory
                self.memory.add(
                    f"At {datetime.now()}: User was {world_state['user_activity']} "
                    f"on {world_state['active_window']}",
                    user_id="main_user"
                )
                
                # 5. PROACTIVE DECISION
                decision = await self.proactive_decision_engine(world_state)
                
                # 6. Execute
                message = await self.execute_decision(decision)
                
                if message and callback:
                    callback(message)
                
            except Exception as e:
                print(f"[PERCEPTION ERROR] {e}")
            
            # Sample every 30 seconds
            await asyncio.sleep(30)

if __name__ == "__main__":
    daemon = ContinuousPerceptionDaemon()
    asyncio.run(daemon.run_forever())
