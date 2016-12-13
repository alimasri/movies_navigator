class Movie:
    def __init__(self):
        self.title = ""
        self.year = 0
        self.release_date = ""
        self.rating = 0
        self.runtime = 0
        self.genres = []
        self.cover = ""
        self.plot = ""
        self.id = 0
        self.type = ""

    def __repr__(self):
        return '[{0}] {1} - {2}, rating {3}, genres: {4}'.format(self.id, self.title, self.year, self.rating,
                                                                 self.genres)
