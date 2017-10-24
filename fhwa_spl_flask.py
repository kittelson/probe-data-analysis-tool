"""
Starts the local flask server that runs the webview/d3js visualizations
"""


from flask import Flask, render_template
import sys
import os


#app = Flask(__name__)

if getattr(sys, 'frozen', False):
      template_folder = os.path.join(sys.executable, '..','templates')
      static_folder = os.path.join(sys.executable, '..','static')
      app = Flask(__name__, template_folder = template_folder,\
                              static_folder = static_folder)
else:
    app = Flask(__name__)


@app.route('/')
def index():
    print('got to flask')
    print(app.template_folder)
    return render_template('index2_2.html')
