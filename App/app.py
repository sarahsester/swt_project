from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap

# set variables in terminal:
# set FLASK_APP=app.py
# set FLASK_ENV=development

# to start the app:
# - activate virtual environment: "venv\Scripts\activate.bat"
# - run "python app.py" or "flask run" in your terminal

app = Flask(__name__)
Bootstrap(app)


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    #processed_text = coordinate1.upper()
    #return processed_text
    return render_template('streets.html')


@app.route("/streets")
def streets():
    return render_template('streets.html')


@app.route("/churches")
def about():
    return render_template('churches.html')


if __name__ == "__main__":
    app.run(debug=True)
