from flask import Flask, render_template, request
from flask_cors import cross_origin
from movies_recommender import MoviesRecommender
from datetime import datetime
from logger import App_Logger

app = Flask(__name__) # initializing a flask app

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():

    try:
        return render_template("search.html")
    except Exception as e:
        raise e

@app.route('/recommendation',methods=['POST','GET']) # route to show the recommendation in a web UI
@cross_origin()
def index():
    try:
        if request.method == 'POST':
            log = App_Logger()
            obj = datetime.now()
            date = ''.join(map(str, str(obj.date()).split('-')))
            time = ''.join(map(str, str(obj.time()).split(':')))
            log_file = open('logs/log-' + date + '-' + time + '.txt', 'w+')
            log.log(log_file, " Recommendation Starts!!! ")  # log

            movie_name = request.form['movie_name']
            mr = MoviesRecommender(log_file)
            log.log(log_file, " Created a object of  MoviesRecommender")  # log
            movie_list = mr.movies_recommendations(movie_name)
            log.log(log_file, " Got the list of movuies and their posters ")  # log
            if len(movie_list)>0:
                return render_template("recommendation.html", movies=movie_list)
            else:
                log.log(log_file, " No Recommendation ")  # log
                return render_template("nomovie.html", movies=movie_list)
    except Exception as e:

        raise e

if __name__ == "__main__":
    app.run() # running the app