from flask import Flask
import threading
import bot

app = Flask(__name__)

@app.route('/')
def index():
    return "Aizen Bot Running ⚡️"

def run_bot():
    bot.run_bot()

if __name__ == '__main__':
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=5000)
