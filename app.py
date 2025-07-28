from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import json
import os

load_dotenv()

app = Flask(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

def extract_text_from_webpage(url):
    """Extract text content from a webpage"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
            
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

    except Exception as e:
        return f"Error extracting content from webpage: {str(e)}"

@app.route('/extract_url', methods=['POST'])
def extract_url():
    url = request.json.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        content = extract_text_from_webpage(url)
            
        return jsonify({
            'url': url,
            'content': content
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to process URL: {str(e)}'}), 500

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