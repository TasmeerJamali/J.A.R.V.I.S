from mem0 import Memory

class MemoryModule:
    def __init__(self):
        print("[Memory] Initializing Mem0...")
        try:
            self.memory = Memory()
            print("[Memory] Mem0 initialized.")
        except Exception as e:
            print(f"[Memory] Error initializing Mem0: {e}")
            self.memory = None

    def add_memory(self, text, user_id="main_user"):
        """Adds a memory with user context."""
        if not self.memory:
            return
        
        try:
            self.memory.add(text, user_id=user_id)
            print(f"[Memory] Added: {text[:50]}...")
        except Exception as e:
            print(f"[Memory] Error adding memory: {e}")

    def query_memory(self, query_text, user_id="main_user"):
        """Retrieves relevant memories."""
        if not self.memory:
            return []
        
        try:
            results = self.memory.search(query_text, user_id=user_id)
            return results
        except Exception as e:
            print(f"[Memory] Error querying memory: {e}")
            return []

    def get_user_profile(self, user_id="main_user"):
        """Get accumulated knowledge about user"""
        if not self.memory:
            return []
        try:
            return self.memory.get_all(user_id=user_id)
        except Exception as e:
            print(f"[Memory] Error getting profile: {e}")
            return []

if __name__ == "__main__":
    mem = MemoryModule()
    mem.add_memory("User is working on the React project.")
    print("Querying 'project':", mem.query_memory("What project am I working on?"))
