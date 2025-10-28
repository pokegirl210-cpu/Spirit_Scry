#!/data/data/com.termux/files/usr/bin/python3

import json
import subprocess
import os
from datetime import datetime

class SpiritScry:
    def __init__(self):
        self.profile_file = "profile.json"
        self.load_profile()
        
    def load_profile(self):
        """Load the user's spiritual profile"""
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                self.profile = json.load(f)
        else:
            # Default balanced profile
            self.profile = {
                "scientific": 3,
                "mystical": 3, 
                "philosophical": 3,
                "depth": 2,
                "goal": "understanding",
                "conversation_history": []
            }
            self.save_profile()
    
    def save_profile(self):
        """Save the user's profile"""
        with open(self.profile_file, 'w') as f:
            json.dump(self.profile, f, indent=2)
    
    def update_setting(self, setting, value):
        """Update a profile setting"""
        if setting in self.profile:
            self.profile[setting] = value
            self.save_profile()
            return f"Updated {setting} to {value}"
        return "Setting not found"
    
    def build_prompt(self, user_question):
        """Build the intelligent prompt for the LLM based on user profile"""
        
        # Map depth levels to response characteristics
        depth_levels = {
            1: "simple analogies and practical wisdom",
            2: "balanced explanations with some depth", 
            3: "detailed philosophical exploration",
            4: "advanced metaphysical concepts with academic rigor",
            5: "profound, transcendent wisdom from multiple traditions"
        }
        
        # Map goals to focus areas
        goals = {
            "understanding": "focus on clear explanations and intellectual insight",
            "practice": "provide practical exercises and daily applications", 
            "inspiration": "offer poetic and uplifting perspectives",
            "counsel": "give compassionate guidance and support"
        }
        
        depth_desc = depth_levels.get(self.profile["depth"], "balanced explanations")
        goal_desc = goals.get(self.profile["goal"], "balanced guidance")
        
        # Build inclination description
        inclinations = []
        if self.profile["scientific"] >= 4:
            inclinations.append("strong scientific/rational perspective")
        if self.profile["mystical"] >= 4:
            inclinations.append("strong mystical/esoteric perspective") 
        if self.profile["philosophical"] >= 4:
            inclinations.append("strong philosophical/theoretical perspective")
            
        inclination_desc = "balanced perspective"
        if inclinations:
            inclination_desc = " and ".join(inclinations)
        
        # Build conversation context
        context = ""
        if self.profile["conversation_history"]:
            recent = self.profile["conversation_history"][-3:]  # Last 3 exchanges
            context = "Recent conversation context:\n"
            for exchange in recent:
                context += f"User: {exchange['question']}\n"
                context += f"Guide: {exchange['answer']}\n\n"
        
        prompt = f"""You are Spirit Scry, an adaptive spiritual guide. The user has a {inclination_desc}. 
The response should use {depth_desc} and {goal_desc}.

{context}
Current question: {user_question}

Provide a response that meets the user where they are spiritually, using appropriate language and concepts for their profile."""
        
        return prompt
    
    def query_llama(self, prompt):
        """Send the prompt to the local LLM and get a response"""
        try:
            # Use the existing llama.cpp setup
            llama_path = os.path.expanduser("~/llama.cpp/main")
            model_path = os.path.expanduser("~/llama.cpp/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
            
            # Run the model (this will be slow)
            result = subprocess.run(
                [llama_path, "-m", model_path, "-p", prompt, "-n", "512", "--temp", "0.7"],
                capture_output=True, text=True, timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
                
        except Exception as e:
            return f"Error querying LLM: {str(e)}"
    
    def ask_question(self, question):
        """Main function to ask a question and get a spiritual response"""
        print(f"\n🧠 Processing your question with depth level {self.profile['depth']}...")
        
        # Build the intelligent prompt
        prompt = self.build_prompt(question)
        
        # Get response from LLM
        response = self.query_llama(prompt)
        
        # Save to conversation history
        self.profile["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": response
        })
        # Keep only last 10 exchanges to manage size
        self.profile["conversation_history"] = self.profile["conversation_history"][-10:]
        self.save_profile()
        
        return response
    
    def show_profile(self):
        """Display current profile settings"""
        print("\n=== Your Spiritual Profile ===")
        print(f"Scientific Inclination: {self.profile['scientific']}/5")
        print(f"Mystical Inclination: {self.profile['mystical']}/5") 
        print(f"Philosophical Inclination: {self.profile['philosophical']}/5")
        print(f"Depth Level: {self.profile['depth']}/5")
        print(f"Primary Goal: {self.profile['goal']}")
        print("==============================")

def main():
    scry = SpiritScry()
    
    print("✨ Welcome to Spirit Scry ✨")
    print("Your adaptive spiritual guide")
    
    while True:
        print("\nOptions:")
        print("1. Ask a spiritual question")
        print("2. Adjust your profile")
        print("3. Show current profile") 
        print("4. Exit")
        
        choice = input("\nChoose an option (1-4): ").strip()
        
        if choice == "1":
            question = input("\nWhat is your spiritual question?\n> ")
            if question.lower() in ['quit', 'exit']:
                break
                
            response = scry.ask_question(question)
            print(f"\n🕯️  Spirit Scry responds:\n{response}")
            
        elif choice == "2":
            print("\nAdjust your spiritual profile:")
            print("1. Scientific inclination (1-5)")
            print("2. Mystical inclination (1-5)")
            print("3. Philosophical inclination (1-5)") 
            print("4. Depth level (1-5)")
            print("5. Primary goal")
            
            setting_choice = input("Choose setting to adjust (1-5): ").strip()
            
            if setting_choice == "1":
                value = int(input("Scientific inclination (1-5): "))
                scry.update_setting("scientific", max(1, min(5, value)))
            elif setting_choice == "2":
                value = int(input("Mystical inclination (1-5): "))
                scry.update_setting("mystical", max(1, min(5, value)))
            elif setting_choice == "3":
                value = int(input("Philosophical inclination (1-5): "))
                scry.update_setting("philosophical", max(1, min(5, value)))
            elif setting_choice == "4":
                value = int(input("Depth level (1-5): "))
                scry.update_setting("depth", max(1, min(5, value)))
            elif setting_choice == "5":
                print("Goals: understanding, practice, inspiration, counsel")
                value = input("Primary goal: ").strip()
                scry.update_setting("goal", value)
                
        elif choice == "3":
            scry.show_profile()
            
        elif choice == "4":
            print("May your path be illuminated. Farewell. ✨")
            break

if __name__ == "__main__":
    main()
