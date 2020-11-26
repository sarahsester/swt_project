from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from SPARQL_queries import create_df_level1, create_map_level1
from SPARQL_queries import create_df_level2, create_map_level2, create_abstract_level2
from SPARQL_queries import get_somebodys_name

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
    if radius == "":
        radius = '10'
    df = create_df_level1(latitude=latitude, longitude=longitude, radius=radius, limit='30')
    _map = create_map_level1(latitude=latitude, longitude=longitude, radius=radius, limit='30')
    return render_template('level1.html',
                           latitude=latitude,
                           longitude=longitude,
                           radius=radius,
                           column_names=df.columns.values,
                           row_data=list(df.values.tolist()),
                           link_column="somebody",
                           zip=zip,
                           _map=_map)


@app.route("/level1")
def level1():
    return render_template('level1.html')


@app.route("/level1", methods=['POST'])
def level1_post():
    if "somebodyLabel" in request.form:
        latitude = 49.49671
        longitude = 8.47955
        somebody = request.form['somebodyLabel']
        somebodys_name = get_somebodys_name(somebody)
        abstract = create_abstract_level2(somebody, somebodys_name)
        df = create_df_level2(somebody, current_latitude=latitude, current_longitude=longitude)
        _map = create_map_level2(somebody)
        return render_template('level2.html',
                               latitude=latitude,
                               longitude=longitude,
                               somebody=somebody,
                               somebodys_name=somebodys_name,
                               abstract=abstract,
                               column_names=df.columns.values,
                               row_data=list(df.values.tolist()),
                               zip=zip,
                               _map=_map)
    else:
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        radius = request.form['radius']
        if radius == "":
            radius = '10'
        df = create_df_level1(latitude=latitude, longitude=longitude, radius=radius, limit='30')
        _map = create_map_level1(latitude=latitude, longitude=longitude, radius=radius, limit='30')
        return render_template('level1.html',
                               latitude=latitude,
                               longitude=longitude,
                               radius=radius,
                               column_names=df.columns.values,
                               row_data=list(df.values.tolist()),
                               link_column="somebody",
                               zip=zip,
                               _map=_map)


@app.route("/level2")
def level2():
    return render_template('level2.html')


@app.route("/level2", methods=['POST'])
def level2_post():
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    somebody = request.form['somebody']
    somebodys_name = request.form['somebodys_name']
    abstract = create_abstract_level2(somebody, somebodys_name)
    df = create_df_level2(somebody, current_latitude=latitude, current_longitude=longitude)
    _map = create_map_level2(somebody)
    return render_template('level2.html',
                           latitude=latitude,
                           longitude=longitude,
                           somebody=somebody,
                           somebodys_name=somebodys_name,
                           abstract=abstract,
                           column_names=df.columns.values,
                           row_data=list(df.values.tolist()),
                           zip=zip,
                           _map=_map)


if __name__ == "__main__":
    app.run(debug=True)
