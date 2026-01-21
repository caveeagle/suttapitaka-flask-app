
from flask import Flask

app = Flask(__name__)

@app.route('/')

def index():

    return 'Hello from Flask behind Nginx'

########################################

if __name__ == "__main__":
    app.run(debug=True)    

########################################
