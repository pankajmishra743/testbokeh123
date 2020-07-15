
#flask_app.py
import subprocess
import atexit
from flask import render_template, render_template_string, Flask
from bokeh.embed import server_document
from bokeh.client import pull_session

app_html="""
<!DOCTYPE html>
<html lang="en">
  <body>
    <div class="bk-root">
      {{ bokeh_script|safe }}
    </div>
  </body>
</html>
"""

app = Flask(__name__)

bokeh_process = subprocess.Popen(["bokeh", "serve", "--allow-websocket-origin=testbokeh123.herokuapp", "--port=5008", "bokeh_plot.py"],stdout=subprocess.PIPE)

@atexit.register
def kill_server():
    bokeh_process.kill()

@app.route('/')
def index():
    session=pull_session(url = 'https://testbokeh123.herokuapp.com/')
    bokeh_script=server_document(None,app_path="/bokeh_plot",session_id=session.id)
    # return render_template('app.html', bokeh_script=bokeh_script)
    return render_template_string(app_html, bokeh_script=bokeh_script)

if __name__ == '__main__':
    print("STARTED")
    app.run(debug=True)
