from gevent import monkey #for server instance
monkey.patch_all() #for server instance
from flask import Flask, request, render_template, send_file, after_this_request
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler
import os
import time

app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent') # for local instance
#socketio = SocketIO(app, async_mode='eventlet') # for server instance with eventlet/gunicorn

from rad import main as handle_entry

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
    else:
        print(f"Error: {path} does not exist") #debug

def handle_entry_callback(pdf_path, filename):
    print(f"Received pdf_path: {pdf_path}")

    @after_this_request
    def send_pdf(response):
        if pdf_path is not None:
            # Emit a custom event to indicate that a download has started
            socketio.emit('download_started', {'message': 'Download started'})

            # Wait for the file to be ready
            while not os.path.exists(pdf_path):
                time.sleep(1)

            # Check if the file exists before trying to open it
            if not os.path.exists(pdf_path):
                print(f"Error: {pdf_path} does not exist")
                return "Error: handle_entry did not return a valid PDF path"

            print(f"File exists: {os.path.exists(pdf_path)}")

            # Schedule the file to be deleted after 15 minutes
            scheduler = BackgroundScheduler()
            scheduler.add_job(func=delete_file, args=[pdf_path], trigger="interval", seconds=900)
            scheduler.start()

            return send_file(pdf_path, as_attachment=True, download_name=f'{filename}.pdf', mimetype='application/pdf')
        else:
            return "Error: handle_entry did not return a valid PDF path"

    return send_pdf

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        name = request.form.get('name')  
        print(f"Calling handle_entry with url={url}, name={name}") #debug
        if url is None or name is None:
            return "Error: Missing URL or name"
        try:
            # Emit the 'download_started' event
            socketio.emit('download_started', {'message': 'Download started'})

            result = handle_entry(url, name, socketio, lambda pdf_path: handle_entry_callback(pdf_path, name))
            if result is not None:
                return result
        except AssertionError:
            return "Error! Unable to find comic. Are you sure the URL to the comic is correct?"

    return render_template('index.html')

#if __name__ == '__main__': # you need this to run locally
#    socketio.run(app, debug=False)

#if __name__ == '__main__': # to run on server via gunicorn/eventlet
    #app.run(debug=False)
    #eventlet.wsgi.server(eventlet.listen(('127.0.0.1', 5000)), app)
    #socketio.run(app, debug=False)

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    from geventwebsocket.handler import WebSocketHandler
    http_server = WSGIServer(('127.0.0.1',5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()

