#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import warnings
from movies_navigator.utils import *
from movies_navigator import __version__
from cmd import Cmd

warnings.simplefilter('ignore', UserWarning)
from fuzzywuzzy import fuzz

__author__ = "Ali Masri"
__copyright__ = "Ali Masri"
__license__ = "MIT"


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Movies navigator")
    parser.add_argument(
        "-v",
        '--version',
        action='version',
        version='movies_navigator {ver}'.format(ver=__version__))
    parser.add_argument(
        "-s",
        "--seen",
        dest="seen_path",
        help="seen movies directory",
        type=str
    )
    parser.add_argument(
        "-w",
        "--watchlist",
        dest="watch_list_path",
        help="watch list movies directory",
        type=str
    )
    parser.add_argument(
        "-d",
        "--data-file",
        dest="data_file",
        help="data file path to store parsed movie information",
        type=str
    )
    return parser.parse_args(args)


def parse_ls(args):
    parser = argparse.ArgumentParser("ls")
    parser.add_argument("-t", "--type", dest="type", help="movie type", choices=[TYPE_SEEN, TYPE_WATCHLIST],
                        type=str)
    parser.add_argument("--min-rating", dest="min_rating", help="the minimum rating of the movie", choices=range(0, 11),
                        default=0, type=int)
    parser.add_argument("--max-rating", dest="max_rating", help="the maximum rating of the movie", choices=range(0, 11),
                        default=10, type=int)
    parser.add_argument("-g", "--genres", dest="genres", help="the movie genres", nargs="*")
    parser.add_argument("--min-year", dest="min_year", help="the minimum release year of the movie", default=0,
                        type=int)
    parser.add_argument("--max-year", dest="max_year", help="the maximum release year of the movie", default=9999,
                        type=int)
    parser.add_argument("--sort-by", dest="sort_by", help="choose the order of the movies",
                        choices=["year", "rating", "title", "id", ""], type=str)
    return parser.parse_args(args)


class Filter:
    @staticmethod
    def by_title(movies, movie_title):
        results = []
        for movie in movies:
            if fuzz.ratio(movie.title, movie_title) > 60 or movie_title in movie.title:
                results.append(movie)
        return results

    @staticmethod
    def by_rating(movies, min_rating=0, max_rating=10):
        return list(
            filter(lambda movie: min_rating <= float(movie.rating) <= max_rating, movies))

    @staticmethod
    def by_type(movies, _type):
        return list(filter(lambda movie: movie.type == _type, movies))

    @staticmethod
    def by_genre(movies, genres):
        if genres is None:
            return movies
        return list(filter(lambda movie: set(genres).issubset(set(movie.genres)), movies))

    @staticmethod
    def by_year(movies, min_year=0, max_year=9999):
        return list(filter(lambda movie: min_year <= movie.year <= max_year, movies))


class Cli(Cmd):
    def __init__(self, all_movies, seen_path, watchlist_path, data_file):
        Cmd.__init__(self)
        self.all_movies = all_movies
        self.seen_path = seen_path
        self.watchlist_path = watchlist_path
        self.data_file = data_file

    def do_search(self, movie_title):
        """search movie_title
        Searches a movie by title using fuzzy string matching"""
        print_movies(Filter.by_title(self.all_movies, movie_title))

    def do_ls(self, line):
        if line is not None and line != "":
            line = line.strip()
            line = line.split(" ")
        try:
            args = parse_ls(line)
            _type = args.type or None
            min_rating = args.min_rating
            max_rating = args.max_rating
            min_year = args.min_year
            max_year = args.max_year
            genres = args.genres
            sort_by = args.sort_by
            if _type is None:
                movies = self.all_movies
            else:
                movies = Filter.by_type(self.all_movies, _type)
            if min_year is not None or max_year is not None:
                movies = Filter.by_year(movies, min_year, max_year)
            if min_rating is not None or max_rating is not None:
                movies = Filter.by_rating(movies, min_rating, max_rating)
            if genres is not None:
                movies = Filter.by_genre(movies, genres)
            if sort_by is not None:
                movies = sorted(movies, key=lambda movie: getattr(movie, sort_by))
            print_movies(movies)
        except Exception as e:
            print(e)
        except SystemExit:
            pass

    def help_ls(self):
        print('run ls -h for detailed information')

    def do_open(self, movie_id):
        """open movie_id
        Opens the movie directory with the folder manager"""
        if movie_id is not None and movie_id.isdigit():
            movie_id = int(movie_id)
            movie = get_movie_by_id(self.all_movies, movie_id)
            if movie is not None:
                movie_path = os.path.abspath(movie.path)
                try:
                    open_file(movie_path)
                except:
                    print('Folder not found: ' + movie_path)

    def do_info(self, movie_id):
        """info movie_id
        Print movie information"""
        if movie_id is not None and movie_id.isdigit():
            movie_id = int(movie_id)
            movie = get_movie_by_id(self.all_movies, movie_id)
            if movie is not None:
                print(get_movie_information(movie))

    def do_mv(self, movie_id):
        """mv movie_id
        Toggles the movie folder from seen to watchlist and vice-versa"""
        if self.seen_path is None or self.watchlist_path is None:
            print("seen and/or watchlist path are/is undefined")
            return
        movie_id = int(movie_id)
        movie = get_movie_by_id(self.all_movies, movie_id)
        if movie is not None:
            try:
                move_movie(movie, self.seen_path, self.watchlist_path)
                persist_object(self.data_file, self.all_movies)
            except Exception as e:
                print("error!\n" + str(e))
        else:
            print("No movie found!")

    def do_reload(self, line):
        """reload
        Reloads the movie list from the directories"""
        try:
            self.all_movies = load_movies(self.seen_path, self.watchlist_path)
            persist_object(self.data_file, self.all_movies)
        except FileNotFoundError:
            print("Error - Please make sure that the directories you specified actually exist")

    def do_summary(self, line):
        """summary
        Returns a summary of the current movie database
        """
        nb_total = len(self.all_movies)
        nb_seen = len(list(filter(lambda movie: movie.type == TYPE_SEEN, self.all_movies)))
        nb_watchlist = len(list(filter(lambda movie: movie.type == TYPE_WATCHLIST, self.all_movies)))
        print("Total number of movies {}\nSeen: {}, Watchlist: {}".format(nb_total, nb_seen, nb_watchlist))

    def do_cls(self, line):
        """cls
        Clears the screen"""
        if sys.platform.startswith("win"):
            os.system("cls")
        else:
            os.system("clear")

    def do_exit(self, line):
        """exit
        Exit the program"""
        return True


def main(args):
    args = parse_args(args)
    seen_path = args.seen_path
    watch_list_path = args.watch_list_path
    data_file = args.data_file or "movies_navigator.data"
    print("Loading movies...")
    all_movies = load_object(data_file)
    if all_movies is None:
        try:
            all_movies = load_movies(seen_path, watch_list_path)
        except FileNotFoundError:
            print("Error - Please make sure that the directories you specified actually exist")
            return
        persist_object(data_file, all_movies)
        print("Movies loaded successfully")
    else:
        print("Movies loaded from previous data - use 'reload' command to refresh")
    print('Total number of movies: {0}'.format(len(all_movies)))
    cli = Cli(all_movies, seen_path, watch_list_path, data_file)
    cli.prompt = 'navigator> '
    cli.cmdloop()


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
