from flask import Flask, request, render_template, session
from flask_bootstrap import Bootstrap
from flask_session import Session
from SPARQL_queries import create_df_level1, create_map_level1
from SPARQL_queries import create_df_level2, create_map_level2, create_abstract_level2

# activate virtual env: venv\Scripts\activate.bat

# set variables in terminal:
# set FLASK_APP=app.py
# set FLASK_ENV=development

# to start the app, run "python app.py" or "flask run" in your terminal


app = Flask(__name__, template_folder="./Templates")
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)


@app.route("/")
def level1():
    return render_template('level1.html')


@app.route("/", methods=['POST'])
def level1_post():
    if "somebodyLabel" in request.form:
        latitude = session["latitude"]
        longitude = session["longitude"]
        somebody = request.form['somebodyLabel']
        df = create_df_level2(somebody, current_latitude=latitude, current_longitude=longitude)
        somebodys_name = df.loc[0, 'Person']
        df.drop(['x', 'Person'], axis=1, inplace=True)
        abstract = create_abstract_level2(somebody, somebodys_name)
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
        session["latitude"] = request.form['latitude']
        session["longitude"] = request.form['longitude']
        session["radius"] = request.form['radius']
        if session["radius"] == "":
            session["radius"] = '10'
        latitude = session["latitude"]
        longitude = session["longitude"]
        radius = session["radius"]
        df = create_df_level1(latitude=latitude, longitude=longitude, radius=radius, limit='30')
        df.drop(['x'], axis=1, inplace=True)
        _map = create_map_level1(latitude=latitude, longitude=longitude, radius=radius, limit='30')
        return render_template('level1.html',
                               latitude=latitude,
                               longitude=longitude,
                               radius=radius,
                               string="You have entered the coordinates (" + latitude + ", " + longitude
                                      + ") and the radius " + radius + " km.",
                               column_names=df.columns.values,
                               row_data=list(df.values.tolist()),
                               link_column="Further Results",
                               zip=zip,
                               _map=_map)


@app.route("/level2")
def level2():
    latitude = session["latitude"]
    longitude = session["longitude"]
    return render_template('level2.html',
                           latitude=latitude,
                           longitude=longitude)


@app.route("/level2", methods=['POST'])
def level2_post():
    latitude = session["latitude"]
    longitude = session["longitude"]
    somebody = request.form['somebodyLabel']
    df = create_df_level2(somebody, current_latitude=latitude, current_longitude=longitude)
    somebodys_name = df.loc[0, 'Person']
    df.drop(['x', 'Person'], axis=1, inplace=True)
    abstract = create_abstract_level2(somebody, somebodys_name)
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
