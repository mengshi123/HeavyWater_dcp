import re
import os
import csv
import numpy as np
import pandas as pd

from sklearn.externals import joblib
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

ml_model = None
label = None

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    """Homepage"""
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    method = request.method
    predictions = None

    #If methods == get we use text to transfer data
    if method == 'GET':
        print (request.headers.get('Content-Type'))
        text = request.args.get('text')
        # data should be in well-format
        if re.match('^([a-z]|[A-Z]|[0-9]|\\s)+', text):
            predictions = ml_model.predict_proba([text])
        else:
            return render_template('index.html')
    #post use json
    elif method == "POST":
        type = request.headers.get('Content-Type')
        if type.startswith('multipart/form-data'):
            f = request.files['file']
            file_name = secure_filename(f.filename)
            f.save(os.path.join(app.instance_path, 'htmlfi', file_name))
            text = read_file(file_name)
            predictions = ml_model.predict_proba(text)
        elif type.startswith('application/json'):
            data = request.get_json()
            text = data['text']
            predictions = ml_model.predict_proba(text)
        else:
            return render_template('index.html')

    print (predictions)
    results = generate_results(predictions)
    return render_template('result.html', result = results)


def load_data():
    # Load machine learning model
    global ml_model
    model_path = 'model/nb_model.z'
    with open(model_path, 'rb') as f:
        ml_model = joblib.load(f)

    #Load label from csv, here we use numbers as label
    global label
    label_path = 'model/label_id.csv'
    df = pd.read_csv(label_path, header=None)
    label = df.as_matrix(columns=[0])

def generate_results(predictions):
    (n, d) = predictions.shape
    idx_sort = np.argsort(-predictions, axis=1)
    primary = idx_sort[:,0]
    predictions = np.around(predictions, decimals=2)

    result = np.concatenate((label[primary],
                             np.choose(primary, predictions.T).reshape(n,1)
                             ), axis=1)
    return pd.DataFrame(result).to_json(orient='index')


def read_file(file_name):
    file_path = 'instance/htmlfi/' + file_name
    df = pd.read_csv(file_path, header=None)
    return df[1].astype('str')


if __name__ == '__main__':
    load_data()

    app.run(debug=True, host='0.0.0.0')
