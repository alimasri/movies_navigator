import os
import sys
import shutil

from imdbpie import Imdb

from movies_navigator.movie import Movie

imdb = Imdb()
INFO_FILE = "info.txt"

if sys.version[0] == "3":
    raw_input = input


def print_movie_information(movie):
    return ('Title: {0}\n'
            'Year: {1}\n'
            'Release date: {2}\n'
            'Rating: {3}\n'
            'Runtime: {4}\n'
            'Genres: {5}\n'
            'Plot summary: {6}'.format(movie.title, movie.year, movie.release_date, movie.rating,
                                       print_time(movie.runtime), movie.genres,
                                       movie.plot))


def load_movies(seen_path, watchlist_path):
    movies = []
    _id = 1
    if seen_path is not None:
        for genre in os.listdir(seen_path):
            for movie_folder in os.listdir(os.path.join(seen_path, genre)):
                movie = parse_info_file(os.path.join(seen_path, genre, movie_folder, INFO_FILE))
                if movie is None:
                    continue
                movie.genres = genre.split(",")
                movie.type = "seen"
                movie.id = _id
                movie.path = os.path.join(seen_path, genre, movie_folder)
                _id += 1
                movies.append(movie)
    if watchlist_path is not None:
        for genre in os.listdir(watchlist_path):
            for movie_folder in os.listdir(os.path.join(watchlist_path, genre)):
                movie = parse_info_file(os.path.join(watchlist_path, genre, movie_folder, INFO_FILE))
                if movie is None:
                    continue
                movie.type = "watchlist"
                movie.genres = genre.split(",")
                movie.id = _id
                movie.path = os.path.join(watchlist_path, genre, movie_folder)
                _id += 1
                movies.append(movie)
    return movies


def print_time(seconds):
    try:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return "%d:%02d:%02d" % (h, m, s)
    except:
        return seconds


def parse_info_file(info):
    try:
        f = open(info, 'r')
        movie = Movie()
        for line in f:
            tokens = line.lower().split(":", 1)
            key = tokens[0]
            value = tokens[1].strip().lower()
            if value is None or value == "none":
                continue
            if key.startswith('title'):
                movie.title = value
            elif key.startswith('year'):
                movie.year = value
            elif key.startswith('release date'):
                movie.release_date = value
            elif key.startswith('rating'):
                movie.rating = value
            elif key.startswith('runtime'):
                movie.runtime = value
            elif key.startswith('plot'):
                movie.plot = value
        f.close()
        return movie
    except:
        return None


def print_movies(movies):
    for movie in movies:
        print(movie)


def get_movie_by_id(movies, id):
    for movie in movies:
        if movie.id == id:
            return movie
    return None


def move_movie(movie, seen_path, watchlist_path):
    if movie is None:
        return
    if movie.type == "seen":
        destination_root = watchlist_path
    elif movie.type == "watchlist":
        destination_root = seen_path
    else:
        raise Exception("Unable to move - unknown movie type")
    try:
        destination_path = os.path.join(destination_root, ",".join(movie.genres), os.path.basename(movie.path))
        shutil.move(movie.path, destination_path)
        movie.path = destination_path
        movie.type = "watchlist" if movie.type == "seen" else "seen"
    except Exception as e:
        raise e
