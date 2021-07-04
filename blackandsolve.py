UNKNOWN = '◻'
FILLED = '◼'
EMPTY = 'X'


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
        self.board = [[UNKNOWN for _ in range(len(self.column_indicators))]
                      for _ in range(len(self.row_indicators))]

    def getBoundriesFromSittings(self, sittings):
        start = min(map(lambda pair: pair[0], sittings))
        end = max(map(lambda pair: pair[1], sittings))
        return (start, end)

    def printState(self):
        maxRowIndicatorsLength = max(map(len, self.row_indicators))
        board_copy = list(map(lambda matrix: matrix.copy(), self.board))
        for i in range(len(board_copy)):
            board_copy[i] = [' ' for _ in range(
                maxRowIndicatorsLength-len(self.row_indicators[i]))] + [str(j)
                                                                        for j in self.row_indicators[i]]+["|"] + board_copy[i]
        maxColIndicatorsLength = max(map(len, self.column_indicators))
        colIndReorgenize = []
        for i in range(maxColIndicatorsLength):
            colIndReorgenize = [[' ' for _ in range(maxRowIndicatorsLength+1)] + [inds[len(inds)-1-i] if i < len(
                inds) else ' ' for inds in self.column_indicators]] + colIndReorgenize
        colIndReorgenize = colIndReorgenize + \
            [[' ' if i < maxRowIndicatorsLength else '_' for i in range(
                len(self.board)+maxRowIndicatorsLength)]]
        board_copy = colIndReorgenize + board_copy
        stringifyMatrix = [[str(e) for e in row] for row in board_copy]
        lens = [max(map(len, col)) for col in zip(*stringifyMatrix)]
        fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in stringifyMatrix]
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

    def secondPass(self):
        for column_index in range(len(self.column_indicators)):
            for blockIndex in range(len(self.column_indicators[column_index])):
                bas.colorColOverlap(
                    column_index, bas.possibleColSittings(column_index, blockIndex))
        for row_index in range(len(self.row_indicators)):
            for blockIndex in range(len(self.row_indicators[row_index])):
                bas.colorRowOverlap(
                    row_index, bas.possibleRowSittings(row_index, blockIndex))

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
        leftLimit = sum(self.row_indicators[row][:blockIndex]
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
            for j in range(blocked_indexes[i], blocked_indexes[i+1]-self.row_indicators[row][blockIndex]):
                sittings.append([j+1, j+self.row_indicators[row][blockIndex]])
        return sittings

    def possibleColSittings(self, col, blockIndex):
        upLimit = sum(self.column_indicators[col][:blockIndex]
                      ) + len(self.column_indicators[col][:blockIndex])
        downLimit = len(self.board) - (sum(self.column_indicators[col][blockIndex+1:]
                                           ) + len(self.column_indicators[col][blockIndex+1:]))
        sittings = []
        blocked_indexes = [upLimit-1]
        for i in range(upLimit, downLimit):
            if self.board[i][col] == EMPTY:
                blocked_indexes.append(i)
        blocked_indexes.append(downLimit)
        for i in range(0, len(blocked_indexes)-1):
            for j in range(blocked_indexes[i], blocked_indexes[i+1]-self.column_indicators[col][blockIndex]):
                sittings.append(
                    [j+1, j+self.column_indicators[col][blockIndex]])
        return sittings

    def colorRowOverlap(self, row, sittings):
        for i in range(max(map(lambda pair: pair[0], sittings)), min(map(lambda pair: pair[1], sittings))+1):
            self.board[row][i] = FILLED
        if(len(sittings) == 1):
            if sittings[0][0] != 0:
                self.board[row][sittings[0][0]] = EMPTY
            if sittings[0][1] != len(self.board[row])-1:
                self.board[row][sittings[0][1]] = EMPTY

    def colorColOverlap(self, col, sittings):
        for i in range(max(map(lambda pair: pair[0], sittings)), min(map(lambda pair: pair[1], sittings))+1):
            self.board[i][col] = FILLED

    def fillRowBlockGap(self, row, blockIndex):
        sittings = self.possibleRowSittings(row, blockIndex)
        start, end = self.getBoundriesFromSittings(sittings)
        prevEnd, nextStart = -1, len(self.board[row])
        if(blockIndex > 0):
            prevSittings = self.possibleRowSittings(row, blockIndex-1)
            _, prevEnd = self.getBoundriesFromSittings(prevSittings)
        if(blockIndex+1 < len(self.row_indicators[row])):
            nextSittings = self.possibleRowSittings(row, blockIndex+1)
            nextStart, _ = self.getBoundriesFromSittings(nextSittings)
        colorStart, colorFinish = -1, -2
        for i in range(start, end+1):
            if(self.board[row][i] == FILLED):
                if i > prevEnd and i < nextStart:
                    colorStart = i if colorStart == -1 else colorStart
                    colorFinish = i
        for i in range(colorStart, colorFinish+1):
            self.board[row][i] = FILLED
        if(colorFinish-colorStart == self.row_indicators[row][blockIndex]-1):
            if(colorStart != 0):
                self.board[row][colorStart-1] == EMPTY
            if(colorFinish+1 != len(self.board[row])):
                self.board[row][colorFinish+1] == EMPTY

    def fillColBlockGap(self, col, blockIndex):
        sittings = self.possibleColSittings(col, blockIndex)
        start, end = self.getBoundriesFromSittings(sittings)
        prevEnd, nextStart = -1, len(self.board)
        if(blockIndex > 0):
            prevSittings = self.possibleColSittings(col, blockIndex-1)
            _, prevEnd = self.getBoundriesFromSittings(prevSittings)
        if(blockIndex+1 < len(self.column_indicators[col])):
            nextSittings = self.possibleColSittings(col, blockIndex+1)
            nextStart, _ = self.getBoundriesFromSittings(nextSittings)
        colorStart, colorFinish = -1, -2
        for i in range(start, end+1):
            if(self.board[i][col] == FILLED):
                if i > prevEnd and i < nextStart:
                    colorStart = i if colorStart == -1 else colorStart
                    colorFinish = i
        for i in range(colorStart, colorFinish+1):
            self.board[i][col] = FILLED
        if(colorFinish-colorStart == self.column_indicators[col][blockIndex]-1):
            if(colorStart != 0):
                self.board[colorStart-1][col] == EMPTY
            if(colorFinish+1 != len(self.board)):
                self.board[colorFinish+1][col] == EMPTY

    def thirdPass(self):
        for column_index in range(len(self.column_indicators)):
            for blockIndex in range(len(self.column_indicators[column_index])):
                bas.fillColBlockGap(column_index, blockIndex)
        for row_index in range(len(self.row_indicators)):
            for blockIndex in range(len(self.row_indicators[row_index])):
                bas.fillRowBlockGap(row_index, blockIndex)


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
bas.secondPass()
bas.thirdPass()
bas.printState()
