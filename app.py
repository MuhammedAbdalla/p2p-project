from flask import Flask, render_template, request, url_for, redirect
from random import randint
import client
import worker
import threading

client_obj = None
app = Flask(__name__)

def run_flask(port):
    app.run(port=port)


@app.route('/messenger')
def messenger():

    return render_template('messenger.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    global client_obj
    msg = request.form['message']
    
    if msg == "::q::":
        print(f"disconnecting from {client_obj.address[0]}:{client_obj.address[1]}")
        client_obj.sendMessage("__INIT__", "", client_obj.worker)
        return redirect(url_for('connect'))
    else:
        client_obj.sendMessage("__P2P__", msg, client_obj.address)
    
    # Redirect to a new page with a query parameter
    return redirect(url_for('messenger'))

@app.route('/connect')
def connect():
    global client_obj
    client_obj.sendMessage("__RELOAD__", "", client_obj.worker)

    return render_template('connect.html', users=client_obj.connections)

@app.route('/process_connect', methods=['POST'])
def process_connect():
    global client_obj

    strAddr = request.form['onlineUsers'].split(':')
    client_obj.address = (strAddr[0], strAddr[1])

    # Redirect to a new page with a query parameter
    return redirect(url_for('messenger'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_username', methods=['POST'])
def process_username():
    global client_obj

    username = request.form['username']
    client_obj.username = username

    # Redirect to a new page with a query parameter
    return redirect(url_for('connect'))


if __name__ == "__main__":
    port = randint(5000, 9999)  # Choose a random port between 5000 and 9999
    flask_thread = threading.Thread(target=run_flask, args=(port,), daemon=True)
    flask_thread.start()

    client_obj = client.Client("", '127.0.0.1', port)
    client.start_client(client_obj)

    print("Main thread exits.")