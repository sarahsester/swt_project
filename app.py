from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from SPARQL_queries import create_df_level1, create_map_level1

# activate virtual env: venv\Scripts\activate.bat

# set variables in terminal:
# set FLASK_APP=app.py
# set FLASK_ENV=development

# to start the app, run "python app.py" or "flask run" in your terminal


app = Flask(__name__, template_folder="./Templates")
Bootstrap(app)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    radius = request.form['radius']
    df = create_df_level1(latitude=latitude, longitude=longitude, radius=radius, limit='30')
    _map = create_map_level1(latitude=latitude, longitude=longitude, radius=radius, limit='30')
    return render_template('level1.html',
                           latitude=latitude,
                           longitude=longitude,
                           radius=radius,
                           column_names=df.columns.values,
                           row_data=list(df.values.tolist()),
                           link_column="somebodyLabel",
                           zip=zip,
                           _map=_map)


@app.route("/level1")
def level1():
    return render_template('level1.html')


@app.route("/level2")
def level2():
    return render_template('level2.html')


if __name__ == "__main__":
    app.run(debug=True)
