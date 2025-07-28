from flask import Flask, render_template, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract_points', methods=['POST'])
def extract_points():
    try:
        data = request.get_json()
        user_text = data.get('text', '')
        
        if not user_text:
            return jsonify({'error': 'No text provided'}), 400
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }
        
        content = f"beri poin penting: {user_text}"
        
        data = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, data=json.dumps(data), timeout=30)
        response.raise_for_status()
        
        ai_response = response.json()
        points = ai_response['choices'][0]['message']['content']
        
        return jsonify({'points': points})
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'API connection error'}), 500
    except KeyError:
        return jsonify({'error': 'Invalid API response'}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)