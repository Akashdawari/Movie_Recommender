import requests
from logger import App_Logger


class TMDB:

    def __init__(self,log_file):
        self.log_file = log_file
        self.log = App_Logger()

    def fetch_poster(self, movie_id):

        """
        This method create a path for posters of the movies
        :param movie_id: string
        :return:
        """
        try:
            reponse = requests.get("https://api.themoviedb.org/3/movie/{}?api_key=f1857f1c73a189d66943c978c4964ea7&language=en-US".format(movie_id))
            data = reponse.json()
            return "https://image.tmdb.org/t/p/w185/"+data['poster_path']
        except Exception as e:
            raise e