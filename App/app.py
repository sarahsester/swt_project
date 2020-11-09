from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import pandas as pd
import numpy as np


# set variables in terminal:
# set FLASK_APP=app.py
# set FLASK_ENV=development

# to start the app, run "python app.py" or "flask run" in your terminal

app = Flask(__name__)
Bootstrap(app)


df = pd.DataFrame({'Street Name': ["Schillerpromenade", "Goethestraße"],
                   "City": ["Berlin", "Chemnitz"],
                   "Person": ["Friedrich Schiller", "Johann Wolfgang von Goethe"]})


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    return render_template('streets.html',
                           latitude=latitude,
                           longitude=longitude,
                           column_names=df.columns.values,
                           row_data=list(df.values.tolist()),
                           link_column="Person",
                           zip=zip)


@app.route("/streets")
def streets():
    return render_template('streets.html')


@app.route("/churches")
def about():
    return render_template('churches.html')


if __name__ == "__main__":
    app.run(debug=True)
