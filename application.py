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

    if method == 'GET': # read text to be predicted from url
        print request.headers.get('Content-Type')
        text = request.args.get('text')
        # Document should consists of only digits or characters
        # or their combination
        if re.match('^(\\s)*([a-z]|[A-Z]|[0-9])([a-z]|[A-Z]|[0-9]|\\s)*', text):
            predictions = ml_model.predict_proba([text])
        else:
            return render_template('index.html')

    elif method == "POST":
        try:
            type = request.headers.get('Content-Type')
            if type.startswith('multipart/form-data'):
                f = request.files['file']
                file_name = secure_filename(f.filename)
                f.save(os.path.join(app.instance_path, 'htmlfi', file_name))
                print "File downloaded."
                text = read_file(file_name)
                predictions = ml_model.predict_proba(text)
            elif type.startswith('application/json'):
                data = request.get_json()
                text = data['text']
                predictions = ml_model.predict_proba(text)
            else:
                return render_template('index.html')
        except Exception as e:
            raise e

    print predictions
    results = generate_results(predictions)
    return render_template('results.html', result = results)


def load_data():
    try:
        print "Loading machine learning model..."
        global ml_model
        model_path = 'model/NB_doc_clf_model.z'
        with open(model_path, 'rb') as f:
            ml_model = joblib.load(f)
        print "Model loaded successfully!"

    except Exception as e:
        print "Unable to load machine learning model!!"
        raise e

    try:
        print "Loading label..."
        global label
        label_path = 'model/label_id.csv'
        df = pd.read_csv(label_path, header=None)
        label = df.as_matrix(columns=[0])
        print "Label loaded!"

    except Exception as e:
        print "Unable to load label!!"
        raise e

def generate_results(predictions):
    (n, d) = predictions.shape
    idx_sort = np.argsort(-predictions, axis=1)
    primary = idx_sort[:,0]
#    secondary = idx_sort[:,1]
    predictions = np.around(predictions, decimals=2)

    result = np.concatenate((label[primary],
                             np.choose(primary, predictions.T).reshape(n,1)#,
                             #label[secondary],
                             #np.choose(secondary, predictions.T).reshape(n,1)
                             ), axis=1)
    return pd.DataFrame(result).to_json(orient='index')


def read_file(file_name):
    file_path = 'instance/htmlfi/' + file_name
    df = pd.read_csv(file_path, header=None)
    return df[1].astype('str')


if __name__ == '__main__':
    load_data()

    # Create folder to receive uploaded files
    try:
        os.makedirs(os.path.join(app.instance_path, 'htmlfi'))
    except OSError, e:
        if e.errno != os.errno.EEXIST:
            raise
        pass

    app.run(debug=True, host='0.0.0.0')
