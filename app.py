from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
import requests
import os

app = Flask(__name__)

# Groq API configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ekstraksi Poin Penting</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            textarea { width: 100%; height: 200px; margin: 10px 0; }
            button { background: #4CAF50; color: white; padding: 10px 15px; border: none; cursor: pointer; }
            #result { margin-top: 20px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>Ekstraksi Poin Penting dari Teks</h1>
        <textarea id="textInput" placeholder="Masukkan teks di sini..."></textarea>
        <br>
        <button onclick="getPoints()">Dapatkan Poin Penting</button>
        <div id="result"></div>

        <script>
            async function getPoints() {
                const text = document.getElementById('textInput').value;
                if (!text.trim()) {
                    alert('Silakan masukkan teks terlebih dahulu!');
                    return;
                }
                
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = 'Memproses...';
                
                try {
                    const response = await fetch('/extract', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: text })
                    });
                    
                    const data = await response.json();
                    if (data.error) {
                        resultDiv.innerHTML = `Error: ${data.error}`;
                    } else {
                        resultDiv.innerHTML = data.points;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `Error: ${error.message}`;
                }
            }
        </script>
    </body>
    </html>
    ''')

@app.route('/extract', methods=['POST'])
def extract_points():
    try:
        data = request.get_json()
        input_text = data.get('text', '')
        
        if not input_text:
            return jsonify({'error': 'Tidak ada teks yang diberikan'}), 400

        # Prepare the prompt with Indonesian instruction
        prompt = f"beri poin penting: {input_text}"
        
        # Prepare headers and payload for Groq API
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama3-8b-8192",  # You can change to other available models
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 1024
        }
        
        # Make API request
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        # Extract the response
        result = response.json()
        points = result['choices'][0]['message']['content'].strip()
        
        return jsonify({'points': points})
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except KeyError as e:
        return jsonify({'error': f'Unexpected API response format: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)