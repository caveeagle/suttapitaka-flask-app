import os

from flask import Flask, render_template, request, jsonify, make_response

import services

from suttapitaka_model import suttapitaka_answer

#####################################################################
#####################################################################

app = Flask(
    __name__
)

@app.get('/')

def index():
    return render_template('index.htm')

#####################################################################
#####################################################################

@app.post('/api/answer')

def api_answer():
    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()

    if not text:
        return jsonify({'ok': False, 'error': 'Empty input'}), 400

    client_ip = (
        request.headers.get("X-Forwarded-For")
        or request.headers.get("X-Real-IP")
        or request.remote_addr
    )
    
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
        
    cid = request.cookies.get('cid')
    
    if not cid:
        cid = str(services.get_uid())
    
    try:
        result = suttapitaka_answer(text,cid,client_ip)
        
        resp = make_response(jsonify({'ok': True, 'result': result}))

        resp.set_cookie(
            'cid',
            cid,
            max_age=60*60*24*90,
            httponly=True,
            samesite='Lax'
        )
        
        return resp

    except Exception as e:
        
        # In production, it’s better to log the traceback, but not expose error details to the outside!
        return jsonify({'ok': False, 'error': str(e)}), 500


#####################################################################
#####################################################################

if __name__ == '__main__':
    app.run(debug=True)
