#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from fuzzywuzzy import fuzz
from movies_navigator.utils import *
from movies_navigator import __version__
from cmd import Cmd

__author__ = "Ali Masri"
__copyright__ = "Ali Masri"
__license__ = "MIT"


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Movies navigator")
    parser.add_argument(
        '--version',
        action='version',
        version='movies_navigator {ver}'.format(ver=__version__))
    parser.add_argument(
        "--seen",
        dest="seen_path",
        help="seen movies directory",
        type=str
    )
    parser.add_argument(
        "--watchlist",
        dest="watch_list_path",
        help="watch list movies directory",
        type=str
    )
    return parser.parse_args(args)


class Filter:
    @staticmethod
    def by_title(movies, movie_title):
        results = []
        for movie in movies:
            if fuzz.ratio(movie.title, movie_title) > 60:
                results.append(movie)
        return results

    @staticmethod
    def by_rating(movies, rating):
        return list(filter(lambda movie: float(movie.rating) >= rating, movies))

    @staticmethod
    def by_rating_and_type(movies, rating, _type):
        return list(filter(lambda movie: float(movie.rating) >= rating and movie.type == _type, movies))

    @staticmethod
    def by_type(movies, _type):
        return filter(lambda movie: movie.type == _type, movies)

    @staticmethod
    def by_genre(movies, genres):
        genres = set(genres.split(","))
        return list(filter(lambda movie: set(genres).issubset(set(movie.genres)), movies))


class Cli(Cmd):
    def __init__(self, all_movies, seen_path, watchlist_path):
        super().__init__()
        self.all_movies = all_movies
        self.seen_path = seen_path
        self.watchlist_path = watchlist_path
        self.output = ""

    def do_title(self, movie_title):
        """title movie_title
        Searches a movie by title using fuzzy string matching"""
        self.output = Filter.by_title(self.all_movies, movie_title)

    def do_list(self, _type):
        """list [type]
        List movies by type [seen, watchlist], list all if type is not specified"""
        if _type == "":
            self.output = self.all_movies
        else:
            self.output = Filter.by_type(self.all_movies, _type)

    def do_rating(self, line):
        """rating rating_number [type]
        List movies by rating, movies can be filtered by type as well"""
        tokens = line.split(" ")
        rating = int(tokens[0])
        if len(tokens) == 1:
            self.output = Filter.by_rating(self.all_movies, rating)
        else:
            self.output = Filter.by_rating_and_type(self.all_movies, rating, tokens[1])

    def do_info(self, movie_id):
        """info movie_id
        Print movie information"""
        movie_id = int(movie_id)
        movie = get_movie_by_id(self.all_movies, movie_id)
        if movie is None:
            self.output = ""
        else:
            self.output = print_movie_information(movie)

    def do_genres(self, genres):
        """genres [genre1, genre2, ...]
        List movies by genres"""
        self.output = Filter.by_genre(self.all_movies, genres)

    def do_move(self, movie_id):
        """move movie_id
        Toggles the movie folder from seen to watchlist and vice-versa"""
        movie_id = int(movie_id)
        movie = get_movie_by_id(self.all_movies, movie_id)
        if movie is not None:
            try:
                move_movie(movie, self.seen_path, self.watchlist_path)
                self.output = "done!"
            except Exception as e:
                self.output = "error!\n" + str(e)
        else:
            self.output = "No movie found!"

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

    def do_pipe(self, args):
        buffer = None
        for arg in args:
            s = arg
            if buffer:
                s += ' ' + buffer
            self.onecmd(s)
            buffer = self.output

    def postcmd(self, stop, line):
        if hasattr(self, 'output'):
            if isinstance(self.output, list):
                print_movies(self.output)
            else:
                print(self.output)
            self.output = None
        return stop

    def parseline(self, line):
        if '|' in line:
            return 'pipe', line.split('|'), line
        return Cmd.parseline(self, line)


def main(args):
    args = parse_args(args)
    seen_path = args.seen_path
    watch_list_path = args.watch_list_path
    print("Loading movies...")
    all_movies = load_movies(seen_path, watch_list_path)
    print("Movies loaded successfully")
    print('Total number of movies: {0}'.format(len(all_movies)))
    cli = Cli(all_movies, seen_path, watch_list_path)
    cli.prompt = 'navigator> '
    cli.cmdloop()


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
