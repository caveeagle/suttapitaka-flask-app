
from flask import Flask, render_template, request, jsonify

from suttapitaka_model import suttapitaka_answer

#####################################################################
#####################################################################

app = Flask(__name__)

@app.get('/')

def index():
    return render_template('index.htm')

@app.post('/api/answer')

#####################################################################
#####################################################################

def api_answer():
    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()

    if not text:
        return jsonify({'ok': False, 'error': 'Empty input'}), 400

    try:
        result = suttapitaka_answer(text)
        return jsonify({'ok': True, 'result': result})

    except Exception as e:
        
        # In production, it’s better to log the traceback, but not expose error details to the outside!
        return jsonify({'ok': False, 'error': str(e)}), 500


#####################################################################
#####################################################################

if __name__ == '__main__':
    app.run(debug=True)
