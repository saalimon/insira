from flask import Flask, render_template, session, send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import sys
sys.path.insert(0, './handler')
from handler import Data, Upload
from uuid import uuid4

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)
def random():
    session['number'] = str(uuid4())
    return None

@app.route('/')
def home():
    random()
    return render_template('index.html')
@app.route('/visualize')
def visualize():
    return render_template('visualize.html')
@app.route('/d3') 
def d3():
    # d3 is histogram distribution of data
    return render_template('d3.html')
@app.route('/d3_2')
def d3_2():
    # d3_2 is correlation scatter plot of data
    return render_template('d3_2.html')
@app.route('/d3_3')
def d3_3():
    # d3_3 is heatmap of data pearson correlation
    return render_template('d3_3.html')
@app.route('/d3_4')
def d3_4():
    # d3_4 is barchart of single catergorical data
    return render_template('d3_4.html')
@app.route('/d3_5')
def d3_5():
    # d3_5 is boxplot of single numerical data
    return render_template('d3_5.html')
@app.route('/data_type')
def data_type():
    return render_template('table.html')

api.add_resource(Upload, '/upload')
api.add_resource(Data, '/data')

app.secret_key = "Miyawaki Sakura"
app.run(port=5000)