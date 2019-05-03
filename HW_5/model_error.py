import numpy as np
import json


class ErrorModel:
    def __init__(self):
        self.statistics = dict()  # {"origin" : {"fix" : number}}
        self._statistics_size = 0

    def load_json(self, json_path):
        (size, stat) = json.loads(open(json_path, "r").read())
        self._statistics_size, self.statistics = size, stat

    def store_json(self, json_path):
        file = open(json_path, "w")
        file.write(json.dumps((self._statistics_size, self.statistics)))
        file.close()

    def fit(self, a, b):
        levenshtein_matrix = self._get_levenshtein_matrix(a, b)
        self._fill_statistics(a, b, levenshtein_matrix)

    def prichesat_statistiku(self):
        for orig in self.statistics.keys():
            for fix in self.statistics[orig].keys():
                self.statistics[orig][fix] /= self._statistics_size

    def get_weighted_distance(self, a, b):
        n, m = len(a), len(b)
        if n > m:
            # Make sure n <= m, to use O(min(n,m)) space
            a, b = b, a
            n, m = m, n

        current_row = list(range(n + 1))  # Keep current and previous row, not entire matrix
        # matrix = np.array([current_row])
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = (previous_row[j] + 1) / self._get_statistics("~", b[i - 1]), \
                                      (current_row[j - 1] + 1) / self._get_statistics(a[j - 1], "~"), \
                                      (previous_row[j - 1] + int(a[j - 1] != b[i - 1])) / self._get_statistics(a[j - 1],
                                                                                                               b[i - 1])
                current_row[j] = min(add, delete, change)
            # matrix = np.vstack((matrix, [current_row]))
        return current_row[n]

    def _get_statistics(self, orig, fit):
        if orig in self.statistics and fit in self.statistics[orig]:
            return self.statistics[orig][fit]
        return 0.5 / self._statistics_size  # newer sow this case

    def _add_statistics(self, orig, fix):
        self.statistics.setdefault(orig, dict())
        self.statistics[orig].setdefault(fix, 0)
        self.statistics[orig][fix] += 1
        self._statistics_size += 1

    def _fill_statistics(self, a, b, matrix):
        n, m = len(a), len(b)

        position = [n, m, matrix[m, n]]  # [x, y, distance]
        while position[2] != 0:  # пока position не придет в правый нижний угол
            x, y = position[0], position[1]

            possible_actions = [matrix[y - 1][x - 1],  # change
                                matrix[y - 1][x],  # add
                                matrix[y][x - 1]]  # delete
            action = np.argmin(possible_actions)

            if action == 0:  # change
                if position[2] != possible_actions[action.item()]:
                    position[2] -= 1
                    self._add_statistics(a[x - 1], b[y - 1])
                    # print(a[x - 1] + " -> " + b[y - 1])
                position[0] -= 1
                position[1] -= 1
            elif action == 1:  # add
                if position[2] != possible_actions[action.item()]:
                    position[2] -= 1
                    self._add_statistics("~", b[y - 1])
                    # print("~ -> " + b[y - 1])
                position[1] -= 1
            else:  # delete
                if position[2] != possible_actions[action.item()]:
                    position[2] -= 1
                    self._add_statistics(a[x - 1], "~")
                    # print(a[x - 1] + " -> ~")
                position[0] -= 1

    @staticmethod
    def _get_levenshtein_matrix(a, b):
        n, m = len(a), len(b)
        inverse = False
        if n > m:
            # Make sure n <= m, to use O(min(n,m)) space
            a, b = b, a
            n, m = m, n
            inverse = True

        current_row = list(range(n + 1))  # Keep current and previous row, not entire matrix
        matrix = np.array([current_row])
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, \
                                      current_row[j - 1] + 1, \
                                      previous_row[j - 1] + int(a[j - 1] != b[i - 1])
                current_row[j] = min(add, delete, change)
            matrix = np.vstack((matrix, [current_row]))
        return matrix if not inverse else matrix.T


# represent word as bigrams
def bi_symbols(string):
    if not string:
        return ["^_"]
    new_string = ["^" + string[0]]
    for i in range(len(string) - 1):
        new_string += [string[i:i + 2]]
    new_string += [string[-1:] + "_"]
    return new_string


if __name__ == "__main__":
    error = ErrorModel()
    error.fit("p", "k")
    error.fit("p", "s")
    error.prichesat_statistiku()
    print(error.statistics)
    print(error.get_weighted_distance("po", "k"))
    # a1 = ["^a", "ab", "b_"]
    # b1 = ["^a", "a_"]
    # print(levenshtein_distance(make_bigram(a1), make_bigram(b1)))  # a to b
    # print(levenshtein_distance(b1, a1))  # b to a
