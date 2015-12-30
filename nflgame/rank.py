import nflgame
import os
import numpy


class PowerRanking(object):
    def __init__(self, year, through_week=None, path=None):
        if path:
            self.games = PowerRanking.load_games(path)
        else:
            weeks = range(1, through_week + 1) if through_week else None
            self.games = nflgame.games(year, weeks)

        self.teams = []
        for team in nflgame.teams:
            self.teams.append(team[0])


    @staticmethod
    def load_games(path):
        games = []
        for (dir, dirs, files) in os.walk(path):
            for file in files:
                game = nflgame.game.Game(None, path + '/' + file)
                games.append(game)
        return games


    def save_games(self, path):
        for game in self.games:
            game.save(os.path.join(path, game.away + '_' + game.home))


    def do_power_ranking(self):
        dim = len(self.teams)

        init_matrix = map(lambda x: map(lambda y: 0.0, range(0, dim)), range(0, dim))

        for game in self.games:
            hindex = self.teams.index(game.home)
            aindex = self.teams.index(game.away)
            if game.score_home > game.score_away:
                init_matrix[hindex][aindex] += 1.0
            elif game.score_away > game.score_home:
                init_matrix[aindex][hindex] += 1.0
            else:
                init_matrix[hindex][aindex] += 0.5
                init_matrix[aindex][hindex] += 0.5

        games_played = []
        for i in range(0, dim):
            games_played.append(
                sum(init_matrix[i])
                + sum([init_matrix[j][i] for j in range(0, dim)])
            )

        for i in range(0, dim):
            num_wins = sum(init_matrix[i])
            if num_wins > 0.0:
                for j in range(0, dim):
                    init_matrix[i][j] = init_matrix[i][j] / num_wins

        in_matrix = numpy.matrix(init_matrix)
        tmp = in_matrix

        for i in range(0, 12):
            tmp = tmp * tmp

        out_vector = tmp.sum(axis=0).tolist()[0]

        ranking = []
        for i in range(0, dim):
            weighted_wins = games_played[i]/(out_vector[i] + 1.0)
            weighted_losses = games_played[i] - weighted_wins
            ranking.append((self.teams[i], out_vector[i], weighted_wins, weighted_losses))

        ret = sorted(ranking, cmp=lambda x, y: cmp(x[1], y[1]))
        return ret
