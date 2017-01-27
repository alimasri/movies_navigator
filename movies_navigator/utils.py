import os
import sys
import shutil
import platform
import subprocess
import pickle

from imdbpie import Imdb

from movies_navigator.movie import Movie, TYPE_SEEN, TYPE_WATCHLIST

from colorama import init, Fore

init(autoreset=True)

imdb = Imdb()
INFO_FILE = "info.txt"

if sys.version[0] == "3":
    raw_input = input


def get_movie_information(movie):
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
    if (seen_path is not None and not os.path.isdir(seen_path)) \
            and \
            (watchlist_path is not None and not os.path.isdir(watchlist_path)):
        raise FileNotFoundError
    if seen_path is not None and os.path.isdir(seen_path):
        for genre in os.listdir(seen_path):
            genre_path = os.path.join(seen_path, genre)
            # skip non dir files
            if not os.path.isdir(genre_path):
                continue
            for movie_folder in os.listdir(genre_path):
                movie = parse_info_file(os.path.join(seen_path, genre, movie_folder, INFO_FILE))
                if movie is None:
                    continue
                movie.genres = genre.split(",")
                movie.type = TYPE_SEEN
                movie.id = _id
                movie.path = os.path.join(seen_path, genre, movie_folder)
                _id += 1
                movies.append(movie)
    if watchlist_path is not None and os.path.isdir(watchlist_path):
        for genre in os.listdir(watchlist_path):
            genre_path = os.path.join(watchlist_path, genre)
            # skip non dir files
            if not os.path.isdir(genre_path):
                continue
            for movie_folder in os.listdir(genre_path):
                movie = parse_info_file(os.path.join(watchlist_path, genre, movie_folder, INFO_FILE))
                if movie is None:
                    continue
                movie.type = TYPE_WATCHLIST
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
                movie.year = int(value)
            elif key.startswith('release date'):
                movie.release_date = value
            elif key.startswith('rating'):
                movie.rating = float(value)
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
        info = str(movie)
        if movie.type == TYPE_SEEN:
            print(Fore.RED + info)
        else:
            print(Fore.GREEN + info)


def get_movie_by_id(movies, id):
    for movie in movies:
        if movie.id == id:
            return movie
    return None


def move_movie(movie, seen_path, watchlist_path):
    if movie is None:
        return
    if movie.type == TYPE_SEEN:
        destination_root = watchlist_path
    elif movie.type == TYPE_WATCHLIST:
        destination_root = seen_path
    else:
        raise Exception("Unable to move - unknown movie type")
    try:
        destination_path = os.path.join(destination_root, ",".join(movie.genres), os.path.basename(movie.path))
        shutil.move(movie.path, destination_path)
        movie.path = destination_path
        movie.type = TYPE_WATCHLIST if movie.type == TYPE_SEEN else TYPE_SEEN
    except Exception as e:
        raise e


def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def persist_object(file_name, obj):
    try:
        with open(file_name, 'wb') as f:
            pickle.dump(obj, f)
    except Exception as e:
        print(e)


def load_object(file_name):
    obj = None
    try:
        with open(file_name, 'rb') as f:
            obj = pickle.load(f)
    except:
        pass
    return obj
