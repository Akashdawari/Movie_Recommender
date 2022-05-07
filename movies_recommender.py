import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.porter import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
from Tmdb_Api_Hitter import TMDB
from logger import App_Logger

class MoviesRecommender:

    def __init__(self, log_file):
        self.log_file=log_file
        self.log = App_Logger()
        self.df = None

    def extract_data(self):

        """This method extract the data from the Data Folder"""
        try:
            movies = pd.read_csv("Data/tmdb_5000_movies.csv")
            credits = pd.read_csv("Data/tmdb_5000_credits.csv")
            # Merging the two data frames on the basis of 'title'
            self.df = pd.merge(movies, credits, on='title', how='left')
            self.log.log(self.log_file, " Successfull executed extract_data method ")  # log
            return

        except Exception as e:
            self.log.log(self.log_file, " ERROR :: " + str(e))  # log
            raise e

    def convert_json(self,k):

        """
        This will convert a json data to a list
        :param k: tuple/row of a data frame
        :return: list
        """
        try:
            genre=[]
            k=ast.literal_eval(k) # ast.literal_eval used to convert string-list to list type
            for dic in k:
                if 'name' in dic:
                    genre.append(dic['name'])
            return genre
        except Exception as e:
            self.log.log(self.log_file, " ERROR :: " + str(e))  # log
            raise e

    def convert_json1(self,k):

        """
        This method convert json to list which has some limits
        :param k: tuple/row of a data frame
        :return: list
        """
        try:
            genre = []
            k = ast.literal_eval(k)  # ast.literal_eval used to convert string-list to list type
            count = 0
            for dic in k:
                if count >= 4:
                    break
                if 'name' in dic:
                    genre.append(dic['name'])
                    count += 1

            return genre
        except Exception as e:
            self.log.log(self.log_file, " ERROR :: " + str(e))  # log
            raise e

    def fetch_director(self,k):

        """
        This method helps to extract director name from the json data
        :param k: tuple/row of a data frame
        :return: director name (list)
        """
        try:
            genre = []
            k = ast.literal_eval(k)  # ast.literal_eval used to convert string-list to list type
            for dic in k:
                if dic['job'] == 'Director':
                    genre.append(dic['name'])
                    break
            return genre
        except Exception as e:
            self.log.log(self.log_file, " ERROR :: " + str(e))  # log
            raise e

    def stem(self,t):

        """
        This method helps to remove similar words from a string
        :param t:  tuple/row of a data frame
        :return: string
        """
        try:
            y = []
            for i in t.split():
                y.append(PorterStemmer().stem(i))
            return " ".join(y)
        except Exception as e:
            self.log.log(self.log_file, " ERROR :: " + str(e))  # log
            raise e


    def preprocessing_data(self):

        """
        This method preprocess the data for further use
        :return:
        """
        try:
            temp = self.df.copy()
            # drop unwanted columns which we donot need in our system.
            temp = temp[['id', 'title', 'genres', 'keywords', 'overview', 'cast', 'crew']]
            # Filling null values with empty string
            temp.fillna("", inplace=True)
            # Converting all the data in eah column to list with tags
            temp['genres'] = temp.genres.apply(self.convert_json)
            self.log.log(self.log_file, " Successful executed convert_json method ")  # log
            temp['keywords'] = temp['keywords'].apply(self.convert_json)
            self.log.log(self.log_file, " Successful executed convert_json method ")  # log
            temp['cast'] = temp['cast'].apply(self.convert_json1)
            self.log.log(self.log_file, " Successful executed convert_json1 method ")  # log
            temp['crew'] = temp.crew.apply(self.fetch_director)
            self.log.log(self.log_file, " Successful executed fetch_director method ")  # log
            temp['overview'] = temp.overview.apply(lambda x: x.split())

            #removing space between the tags
            temp['keywords'] = temp['keywords'].apply(lambda x: [i.replace(" ", '') for i in x])
            temp['genres'] = temp['genres'].apply(lambda x: [i.replace(" ", '') for i in x])
            temp['cast'] = temp['cast'].apply(lambda x: [i.replace(" ", '') for i in x])
            temp['crew'] = temp['crew'].apply(lambda x: [i.replace(" ", '') for i in x])

            # Creating a new column tags
            temp['tags'] = temp['keywords'] + temp['genres'] + temp['cast'] + temp['crew'] + temp['overview']


            temp = temp[['id', 'title', 'tags']]
            #Converting list of tags back to string
            temp['tags'] = temp['tags'].apply(lambda x: " ".join(x))
            #Converting into lower case
            temp['tags'] = temp['tags'].apply(lambda x: x.lower())

            #Removing similar words from the tags
            temp['tags'] = temp['tags'].apply(self.stem)
            self.log.log(self.log_file, " Successful executed stem method ")  # log

            # Processing of data is Done!!!
            self.df = temp.copy()
            self.log.log(self.log_file, " Successful executed preprocessing_data method ")  # log
            return
        except Exception as e:
            self.log.log(self.log_file, " ERROR :: " + str(e))  # log
            raise e

    def similarity_vectors(self):

        """
        This method creates vectors for each movie by using the tags
        :return:
        """
        try:
            cv = CountVectorizer(max_features=5000, stop_words='english')
            vectors = cv.fit_transform(self.df['tags']).toarray()
            similarity = cosine_similarity(vectors)
            self.log.log(self.log_file, " Successful executed similarity_vectors method ")  # log
            return similarity
        except Exception as e:
            self.log.log(self.log_file, " ERROR :: " + str(e))  # log
            raise e

    def movie_in_database(self,movie_name):
        """
        Check the movie is in the database or not
        :param movie_name: string
        :return: boolean
        """
        try:
            movie_list = self.df.title.tolist()
            if movie_name in movie_list:
                self.log.log(self.log_file, " Successful executed movie_in_database method ")  # log
                return True
            else:
                self.log.log(self.log_file, " Successful executed movie_in_database method ")  # log
                return False
        except Exception as e:
            self.log.log(self.log_file, " ERROR :: " + str(e))  # log
            raise e

    def movies_recommendations(self,movie_name):

        """
        This method recommands movies
        :param movie_name: string
        :return: list
        """
        try:
            #load Data
            self.extract_data()

            #Check the move name is in the database or not
            if self.movie_in_database(movie_name):
                #Prepocess Data
                self.preprocessing_data()

                #Similarity Vctors
                similarity = self.similarity_vectors()

                movie_index = self.df[self.df['title'] == movie_name].index[0]
                movie_list = sorted(list(enumerate(similarity[movie_index])), reverse=True, key=lambda x: x[1])[1:8]

                lt=[]
                tmdb= TMDB(self.log_file)
                for i in movie_list:
                    name=self.df['title'].iloc[i[0]]
                    img = tmdb.fetch_poster(self.df['id'].iloc[i[0]])
                    lt.append([name,img])
                self.log.log(self.log_file, " Successful executed movies_recommendations method ")  # log
                return lt
            else:
                self.log.log(self.log_file, " Successful executed movies_recommendations method ")  # log
                return []
        except Exception as e:
            self.log.log(self.log_file, " ERROR :: " + str(e))  # log
            raise e


