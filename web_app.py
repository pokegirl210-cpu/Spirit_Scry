#!/data/data/com.termux/files/usr/bin/python3

from flask import Flask, render_template, request, jsonify
import json
import subprocess
import os
from datetime import datetime
import threading

app = Flask(__name__)

class SpiritScry:
    def __init__(self):
        self.profile_file = "profile.json"
        self.load_profile()
    
    def load_profile(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                self.profile = json.load(f)
        else:
            self.profile = {
                "scientific": 3, "mystical": 3, "philosophical": 3,
                "depth": 2, "goal": "understanding",
                "conversation_history": []
            }
            self.save_profile()
    
    def save_profile(self):
        with open(self.profile_file, 'w') as f:
            json.dump(self.profile, f, indent=2)
    
    def build_prompt(self, user_question):
        depth_levels = {
            1: "simple analogies and practical wisdom",
            2: "balanced explanations with some depth", 
            3: "detailed philosophical exploration",
            4: "advanced metaphysical concepts",
            5: "profound wisdom from multiple traditions"
        }
        
        goals = {
            "understanding": "focus on clear explanations",
            "practice": "provide practical exercises", 
            "inspiration": "offer poetic perspectives",
            "counsel": "give compassionate guidance"
        }
        
        depth_desc = depth_levels.get(self.profile["depth"], "balanced explanations")
        goal_desc = goals.get(self.profile["goal"], "balanced guidance")
        
        inclinations = []
        if self.profile["scientific"] >= 4: inclinations.append("scientific perspective")
        if self.profile["mystical"] >= 4: inclinations.append("mystical perspective") 
        if self.profile["philosophical"] >= 4: inclinations.append("philosophical perspective")
            
        inclination_desc = "balanced perspective"
        if inclinations: inclination_desc = " and ".join(inclinations)
        
        context = ""
        if self.profile["conversation_history"]:
            recent = self.profile["conversation_history"][-3:]
            context = "Recent conversation:\n"
            for exchange in recent:
                context += f"User: {exchange['question']}\nGuide: {exchange['answer']}\n"
        
        prompt = f"""You are Spirit Scry, an adaptive spiritual guide. The user has a {inclination_desc}. 
Respond with {depth_desc} and {goal_desc}.

{context}
Current question: {user_question}

Provide a response that meets the user where they are spiritually."""
        
        return prompt
    
    def query_llama(self, prompt):
        try:
            llama_path = os.path.expanduser("~/elchymin_temple/llama.cpp/main")
            model_path = os.path.expanduser("~/elchymin_temple/llama.cpp/Meta-Llama-3-8B-Instruct-Q3_K_M.gguf")
            
            result = subprocess.run(
                [llama_path, "-m", model_path, "-p", prompt, "-n", "512", "--temp", "0.7"],
                capture_output=True, text=True, timeout=300
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def ask_question(self, question):
        prompt = self.build_prompt(question)
        response = self.query_llama(prompt)
        
        self.profile["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": response
        })
        self.profile["conversation_history"] = self.profile["conversation_history"][-10:]
        self.save_profile()
        
        return response

scry = SpiritScry()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spirit Scry</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: #0f0f23; 
                color: #e0e0e0; 
                margin: 0; 
                padding: 20px;
                background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="30" r="0.5" fill="white" opacity="0.3"/><circle cx="80" cy="60" r="0.3" fill="white" opacity="0.2"/><circle cx="40" cy="80" r="0.4" fill="white" opacity="0.4"/></svg>');
            }
            .container { max-width: 800px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .header h1 { color: #8a2be2; font-size: 2.5em; margin: 0; }
            .header p { color: #b19cd9; font-style: italic; }
            .chat-area { 
                background: rgba(255,255,255,0.05); 
                border-radius: 10px; 
                padding: 20px; 
                margin-bottom: 20px;
                max-height: 400px;
                overflow-y: auto;
            }
            .message { margin-bottom: 15px; }
            .user { color: #64b5f6; }
            .assistant { color: #81c784; }
            .input-area { display: flex; gap: 10px; }
            input, textarea, button, select { 
                padding: 10px; 
                border: 1px solid #333; 
                border-radius: 5px; 
                background: #1a1a2e; 
                color: white;
            }
            button { background: #8a2be2; cursor: pointer; }
            button:hover { background: #7b1fa2; }
            .profile-section { 
                background: rgba(255,255,255,0.05); 
                padding: 15px; 
                border-radius: 10px; 
                margin-bottom: 20px;
            }
            .slider-container { margin-bottom: 10px; }
            .slider-label { display: flex; justify-content: space-between; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✨ Spirit Scry ✨</h1>
                <p>Your adaptive spiritual guide</p>
            </div>
            
            <div class="profile-section">
                <h3>Spiritual Profile</h3>
                <div class="slider-container">
                    <div class="slider-label">
                        <span>Scientific</span>
                        <span id="scientific-value">3</span>
                    </div>
                    <input type="range" id="scientific" min="1" max="5" value="3" onchange="updateProfile()">
                </div>
                <div class="slider-container">
                    <div class="slider-label">
                        <span>Mystical</span>
                        <span id="mystical-value">3</span>
                    </div>
                    <input type="range" id="mystical" min="1" max="5" value="3" onchange="updateProfile()">
                </div>
                <div class="slider-container">
                    <div class="slider-label">
                        <span>Philosophical</span>
                        <span id="philosophical-value">3</span>
                    </div>
                    <input type="range" id="philosophical" min="1" max="5" value="3" onchange="updateProfile()">
                </div>
                <div>
                    <label>Depth: </label>
                    <select id="depth" onchange="updateProfile()">
                        <option value="1">Simple</option>
                        <option value="2" selected>Balanced</option>
                        <option value="3">Detailed</option>
                        <option value="4">Advanced</option>
                        <option value="5">Profound</option>
                    </select>
                    
                    <label>Goal: </label>
                    <select id="goal" onchange="updateProfile()">
                        <option value="understanding">Understanding</option>
                        <option value="practice">Practice</option>
                        <option value="inspiration">Inspiration</option>
                        <option value="counsel">Counsel</option>
                    </select>
                </div>
            </div>
            
            <div class="chat-area" id="chat">
                <div class="message assistant">Welcome, seeker. What wisdom do you seek today?</div>
            </div>
            
            <div class="input-area">
                <input type="text" id="question" placeholder="Ask your spiritual question..." style="flex: 1;" onkeypress="if(event.key=='Enter') askQuestion()">
                <button onclick="askQuestion()">Ask</button>
            </div>
        </div>

        <script>
            function updateProfile() {
                const profile = {
                    scientific: parseInt(document.getElementById('scientific').value),
                    mystical: parseInt(document.getElementById('mystical').value),
                    philosophical: parseInt(document.getElementById('philosophical').value),
                    depth: parseInt(document.getElementById('depth').value),
                    goal: document.getElementById('goal').value
                };
                
                document.getElementById('scientific-value').textContent = profile.scientific;
                document.getElementById('mystical-value').textContent = profile.mystical;
                document.getElementById('philosophical-value').textContent = profile.philosophical;
                
                fetch('/update_profile', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(profile)
                });
            }
            
            function askQuestion() {
                const question = document.getElementById('question').value;
                if (!question) return;
                
                const chat = document.getElementById('chat');
                chat.innerHTML += `<div class="message user">${question}</div>`;
                chat.scrollTop = chat.scrollHeight;
                
                document.getElementById('question').value = '';
                
                fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                })
                .then(response => response.json())
                .then(data => {
                    chat.innerHTML += `<div class="message assistant">${data.response}</div>`;
                    chat.scrollTop = chat.scrollHeight;
                });
            }
            
            fetch('/get_profile')
                .then(response => response.json())
                .then(profile => {
                    document.getElementById('scientific').value = profile.scientific;
                    document.getElementById('mystical').value = profile.mystical;
                    document.getElementById('philosophical').value = profile.philosophical;
                    document.getElementById('depth').value = profile.depth;
                    document.getElementById('goal').value = profile.goal;
                    updateProfile();
                });
        </script>
    </body>
    </html>
    '''

@app.route('/get_profile')
def get_profile():
    return jsonify(scry.profile)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.json
    scry.profile.update(data)
    scry.save_profile()
    return jsonify({"status": "updated"})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')
    response = scry.ask_question(question)
    return jsonify({"response": response})

if __name__ == '__main__':
    print("✨ Spirit Scry Web Server Starting...")
    print("📱 Open your browser to: http://127.0.0.1:5000")
    print("💫 To access from other devices: http://[YOUR-PHONE-IP]:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
