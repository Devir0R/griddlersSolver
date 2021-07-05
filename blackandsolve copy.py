UNKNOWN = '◻'
FILLED = '◼'
EMPTY = 'X'
ROW = 0
COLUMN = 1


def create_indicators_list(source_indicators, axis) -> 'list[Indicator]':
    target_indicators = []
    for i in range(len(source_indicators)):
        target_indicators.append([])
        for j in range(len(source_indicators[i])):
            target_indicators[i].append(
                Indicator(source_indicators[i][j], axis))
    return target_indicators


class BlackAndSolve:
    def __init__(self, column_indicators, row_indicators):
        self.column_indicators = create_indicators_list(
            column_indicators, COLUMN)
        self.row_indicators = create_indicators_list(row_indicators, ROW)
        self.board = [[Cell(j, i, self.row_indicators[j], self.column_indicators[i]) for i in range(len(self.column_indicators))]
                      for j in range(len(self.row_indicators))]

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
                len(self.board)+maxRowIndicatorsLength+1)]]
        board_copy = colIndReorgenize + board_copy
        stringifyMatrix = [[str(e) for e in row] for row in board_copy]
        lens = [max(map(len, col)) for col in zip(*stringifyMatrix)]
        fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in stringifyMatrix]
        print('\n'.join(table))


class Cell:
    def __init__(self, row, column, rowIndicatorsList, colIndicatorsList):
        self.coordinates = (row, column)
        self.col_indicator = -1
        self.row_indicator = -1
        self.content = UNKNOWN
        self.rowIndicatorsList = rowIndicatorsList
        self.colIndicatorsList = colIndicatorsList
        self.possibleRowBlocks: list[int] = range(
            len(rowIndicatorsList)) + [-1]
        self.possibleColBlocks: list[int] = range(
            len(colIndicatorsList)) + [-1]

    def markWith(self, content, rowIndicator=-1, colIndicator=-1):
        self.content = content
        if(rowIndicator != -1):
            self.row_indicator = rowIndicator
        if(colIndicator != -1):
            self.col_indicator = colIndicator

    def __str__(self) -> str:
        return self.content


class Indicator:
    def __init__(self, blockLength, axis):
        self.blockLength = blockLength
        self.cells = range(blockLength)
        self.axis = axis

    def str(self) -> str:
        return self.blockLength

    def addCell(self, cell: Cell):
        row, col = cell.coordinates
        self.cells[row if self.axis == row else col] = cell


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

bas.printState()
