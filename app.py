from flask import Flask, render_template
from random import randint
import client
import worker
import threading


app = Flask(__name__)

def run_flask(port):
    app.run(port=port)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    port = randint(5000, 9999)  # Choose a random port between 5000 and 9999

    flask_thread = threading.Thread(target=run_flask, args=(8000,), daemon=True)
    flask_thread.start()

    c = client.Client("client 1", "localhost", port)
    client.start_client(c, False)

    print("Main thread exits.")