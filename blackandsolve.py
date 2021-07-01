UNKNOWN = 0
FILLED = 1
EMPTY = 2


def copy_indicators(source_indicators, target_indicators):
    for i in range(len(source_indicators)):
        target_indicators.append([])
        for j in range(len(source_indicators[i])):
            target_indicators[i].append(source_indicators[i][j])


class BlackAndSolve:
    def __init__(self, column_indicators, row_indicators):
        self.column_indicators = []
        copy_indicators(
            column_indicators, self.column_indicators)
        self.row_indicators = []
        copy_indicators(
            row_indicators, self.row_indicators)
        self.board = [[0 for _ in range(len(self.column_indicators))]
                      for _ in range(len(self.row_indicators))]

    def printState(self):
        s = [[str(e) for e in row] for row in self.board]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '  '.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        print('\n'.join(table))

    def colorExactRow(self, row):
        placeholder = 0
        for i in range(len(self.row_indicators[row])):
            for _ in range(self.row_indicators[row][i]):
                self.board[row][placeholder] = FILLED
                placeholder += 1
            if placeholder < len(self.board[row]):
                self.board[row][placeholder] = EMPTY
                placeholder += 1

    def mark_row(self, row):
        min_row_space = sum(
            self.row_indicators[row]) + len(self.row_indicators[row]) - 1
        if min_row_space == len(self.board[row]):
            self.colorExactRow(row)
        else:
            for i in range(len(self.row_indicators[row])):
                if min_row_space + self.row_indicators[row][i] > len(self.board[row]):
                    start = len(
                        self.board[row]) - sum(self.row_indicators[row][i:]) - len(self.row_indicators[row][i:]) + 1
                    end = sum(self.row_indicators[row][:i+1]) + i - 1
                    self.colorInRow(row, start, end)

    def colorExactCol(self, col):
        placeholder = 0
        for i in range(len(self.column_indicators[col])):
            for _ in range(self.column_indicators[col][i]):
                self.board[placeholder][col] = FILLED
                placeholder += 1
            if placeholder < len(self.board):
                self.board[placeholder][col] = EMPTY
                placeholder += 1

    def mark_col(self, col):
        min_col_space = sum(
            self.column_indicators[col]) + len(self.column_indicators[col]) - 1
        if min_col_space == len(self.board):
            self.colorExactCol(col)
        else:
            for i in range(len(self.column_indicators[col])):
                if min_col_space + self.column_indicators[col][i] > len(self.board):
                    start = len(
                        self.board) - sum(self.column_indicators[col][i:]) - len(self.column_indicators[col][i:]) + 1
                    end = sum(self.column_indicators[col][:i+1]) + i - 1
                    self.colorInCol(col, start, end)

    def colorInRow(self, row, start, end):
        for i in range(start, end+1):
            self.board[row][i] = FILLED

    def colorInCol(self, col, start, end):
        for i in range(start, end+1):
            self.board[i][col] = FILLED

    def firstPass(self):
        for i in range(len(self.board)):
            self.mark_col(i)
        for i in range(len(self.board[0])):
            self.mark_row(i)

    def blockSitting(self, row, ind):
        rightLimit = len(
            self.board[row]) - sum(self.row_indicators[row][ind+1:]) - len(self.row_indicators[row][ind+1:]) - 1
        leftLimit = sum(self.row_indicators[row][:ind]) + ind
        for i in range(leftLimit, rightLimit+1):
            if self.board[row][i] == FILLED:
                rightLimitCloser = rightLimit - \
                    self.row_indicators[row][ind] + 1
                while rightLimitCloser < i:
                    self.board[row][rightLimitCloser] = FILLED
                    rightLimitCloser += 1
                leftLimitCloser = leftLimit + self.row_indicators[row][ind] - 1
                while leftLimitCloser > i:
                    self.board[row][leftLimitCloser] = FILLED
                    leftLimitCloser -= 1
                break
        for i in range(rightLimit, leftLimit-1, -1):
            if self.board[row][i] == FILLED:
                rightLimitCloser = rightLimit - \
                    self.row_indicators[row][ind] + 1
                while rightLimitCloser < i:
                    self.board[row][rightLimitCloser] = FILLED
                    rightLimitCloser += 1
                leftLimitCloser = leftLimit + self.row_indicators[row][ind]-1
                while leftLimitCloser > i:
                    self.board[row][leftLimitCloser] = FILLED
                    leftLimitCloser -= 1
                break

    def possibleRowSittings(self, row, blockIndex):
        leftLimit = -1 + sum(self.row_indicators[row][:blockIndex]
                             ) + len(self.row_indicators[row][:blockIndex])
        rightLimit = len(self.board[row]) - (sum(self.row_indicators[row][blockIndex+1:]
                                                 ) + len(self.row_indicators[row][blockIndex+1:]))
        sittings = []
        blocked_indexes = [leftLimit-1]
        for i in range(leftLimit, rightLimit):
            if self.board[row][i] == EMPTY:
                blocked_indexes.append(i)
        blocked_indexes.append(rightLimit)
        for i in range(0, len(blocked_indexes)-1):
            for j in range(blocked_indexes[i]+1, blocked_indexes[i+1]-self.row_indicators[row][blockIndex]):
                sittings.append([j+1, j+self.row_indicators[row][blockIndex]])
        return sittings


row_indicators = [
    [7],
    [4, 4, 2],
    [4, 4, 2],
    [4, 4, 3],
    [4, 3, 6],
    [4, 4, 7],
    [4, 3, 7],
    [7, 2, 3],
    [11],
    [5],
    [8],
    [11],
    [3, 2, 5],
    [3, 4, 6],
    [3, 4, 5],
    [4, 3, 2],
    [3, 4, 1],
    [4, 4, 1],
    [4, 5],
    [7]
]
column_indicators = [
    [3, 3],
    [6, 6],
    [8, 8],
    [3, 5, 9],
    [2, 8, 2],
    [1, 4, 1],
    [2, 7, 1],
    [3, 10, 2],
    [7, 4, 7],
    [6, 2, 1, 6],
    [5, 2, 2, 5],
    [1, 3, 2, 2],
    [3, 3],
    [5, 4],
    [6, 4],
    [3, 5],
    [2, 7],
    [2, 6],
    [3],
    [2]
]
bas = BlackAndSolve(column_indicators=column_indicators,
                    row_indicators=row_indicators)
bas.firstPass()
#bas.blockSitting(3, 0)
bas.printState()
print(bas.possibleRowSittings(1, 1))
