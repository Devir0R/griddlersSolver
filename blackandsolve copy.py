from typing import Tuple


UNKNOWN = '◻'
FILLED = '◼'
EMPTY = 'X'
ROW = 0
COLUMN = 1


def create_indicators_list(source_indicators, axis):
    target_indicators = []
    for i in range(len(source_indicators)):
        target_indicators.append([])
        for j in range(len(source_indicators[i])):
            target_indicators[i].append(
                Indicator(source_indicators[i][j], axis))
    return target_indicators


def getCertainBlockLimits(inds: 'list[Indicator]', block, maxLength):
    start = maxLength - \
        sum(map(lambda ind: ind.blockLength,
                inds[block:])) - len(inds[block:]) + 1
    end = sum(map(lambda ind: ind.blockLength, inds[:block+1])) + block - 1
    return (start, end)


def inHowManyRanges(index, ranges):
    forEachRangeIsIndexPresent = map(
        lambda range: range[0] <= index and range[1] >= index, ranges)
    count = 0
    for isPresnt in forEachRangeIsIndexPresent:
        if(isPresnt):
            count += 1
    return count


class BlackAndSolve:
    def __init__(self, column_indicators, row_indicators):
        self.column_indicators = create_indicators_list(
            column_indicators, COLUMN)
        self.row_indicators = create_indicators_list(row_indicators, ROW)
        self.board: list[list[Cell]] = [[Cell(j, i, self.row_indicators[j], self.column_indicators[i], len(row_indicators), len(column_indicators)) for i in range(len(self.column_indicators))]
                                        for j in range(len(self.row_indicators))]
        for row in self.board:
            for cell in row:
                cell.markIfEmpty()

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

    def markEmptiesUsingFilled(self):
        for i in range(len(self.column_indicators)):
            self.markEmptiesLineUsingFilledCells(i, COLUMN)
        for i in range(len(self.row_indicators)):
            self.markEmptiesLineUsingFilledCells(i, ROW)

    def markEmptiesUsingEmpty(self):
        for i in range(len(self.row_indicators)):
            self.markEmptiesLineUsingEmptyCells(i, ROW)
        for i in range(len(self.column_indicators)):
            self.markEmptiesLineUsingEmptyCells(i, COLUMN)

    def markEmptiesLineUsingFilledCells(self, index: int, axis):
        indicators: list[Indicator] = self.column_indicators[index] if axis == COLUMN else self.row_indicators[index]
        maxLength = len(self.board) if axis == COLUMN else len(self.board[0])
        naiveRanges = [self.naiveRange(indicators, index, maxLength)
                       for index in range(len(indicators))]
        line = self.board[index] if axis == ROW else [
            self.board[i][index] for i in range(maxLength)]
        for i in range(len(line)):
            for j in range(len(naiveRanges)):
                left, right = naiveRanges[j]
                if line[i].content == FILLED:
                    if i >= left and i <= right:
                        if i - left >= indicators[j].blockLength:
                            if inHowManyRanges(i, naiveRanges) == 1:
                                naiveRanges[j] = (
                                    i-indicators[j].blockLength+1, right)
                        left, right = naiveRanges[j]
                        if right - i >= indicators[j].blockLength:
                            if inHowManyRanges(i, naiveRanges) == 1:
                                naiveRanges[j] = (
                                    left, i+indicators[j].blockLength-1)
        for i in range(len(line)):
            found = False
            for left, right in naiveRanges:
                if i >= left and i <= right:
                    found = True
                    break
            if(not found):
                line[i].markWith(EMPTY)

    def markEmptiesLineUsingEmptyCells(self, index: int, axis):
        indicators: list[Indicator] = self.column_indicators[index] if axis == COLUMN else self.row_indicators[index]
        maxLength = len(self.board) if axis == COLUMN else len(self.board[0])
        naiveRanges = [self.naiveRange(indicators, index, maxLength)
                       for index in range(len(indicators))]
        line = self.board[index] if axis == ROW else [
            self.board[i][index] for i in range(maxLength)]
        cellsContent = [cell.content for cell in line]
        count = 0
        nonEmptyRanges = []
        for i in range(len(cellsContent)):
            if line[i].content != EMPTY:
                count += 1
                if count == 1:
                    start = i
            elif count > 0:
                nonEmptyRanges.append((start, i-1))
                count = 0
        for i in range(len(naiveRanges)):
            left, right = naiveRanges[i]
            indicator = indicators[i]
            myNonEmptyRanges = nonEmptyRanges.copy()
            leftCut = -1
            rightCut = -1
            for j in range(len(nonEmptyRanges)):
                nonEmptyRangeLeft, nonEmptyRangeRight = nonEmptyRanges[j]
                if (leftCut == -1):
                    if left > nonEmptyRangeRight:
                        continue
                    elif left < nonEmptyRangeLeft:
                        leftCut = j  # nonEmptyRangeLeft should be new left
                        naiveRanges[i] = (nonEmptyRangeLeft, right)
                        left, right = naiveRanges[i]
                    else:  # left is in the range
                        leftCut = j
                        myNonEmptyRanges[j] = (left, nonEmptyRangeRight)
                else:  # find right cut
                    # if right< nonEmptyRangeLeft is impossible case
                    if nonEmptyRangeRight < right:
                        continue
                    elif nonEmptyRangeRight == right:
                        rightCut = j+1
                        break
                    else:  # right is in range
                        rightCut = j+1
                        myNonEmptyRanges[j] = (nonEmptyRangeLeft, right)
            myNonEmptyRanges = myNonEmptyRanges[leftCut:rightCut]
            for myNonEmptyRangeLeft, myNonEmptyRangeRight in myNonEmptyRanges:
                if (myNonEmptyRangeRight-myNonEmptyRangeLeft + 1 < indicator.blockLength):
                    for cell in line[myNonEmptyRangeLeft:myNonEmptyRangeRight+1]:
                        if(axis == COLUMN):
                            cell.removeFromPossibleColList(i)
                        else:  # (axis == COLUMN):
                            cell.removeFromPossibleRowList(i)

    def naiveRange(self, indicators: 'list[Indicator]', indicatorIndex, maxLength) -> Tuple[int, int]:
        start, finish = getCertainBlockLimits(
            indicators, indicatorIndex, maxLength)
        blockLength = indicators[indicatorIndex].blockLength
        if start <= finish:
            return (max(0, start+1-blockLength), min(maxLength-1, finish-1+blockLength))
        else:
            return (sum([ind.blockLength+1 for ind in indicators[:indicatorIndex]]), maxLength - sum([ind.blockLength+1 for ind in indicators[indicatorIndex+1:]])-1)


class Cell:
    def __init__(self, row, column, rowIndicatorsList, colIndicatorsList, rowLength, colLength):
        self.coordinates = (row, column)
        self.content = UNKNOWN
        self.rowIndicatorsList: list[Indicator] = rowIndicatorsList
        self.colIndicatorsList: list[Indicator] = colIndicatorsList
        self.possibleRowBlocks: list[int] = list(range(
            len(rowIndicatorsList)))
        self.possibleRowBlocks.append(-1)
        self.possibleColBlocks: list[int] = list(range(
            len(colIndicatorsList)))
        self.possibleColBlocks.append(-1)
        self.rowLength = rowLength
        self.colLength = colLength
        self.markIfCertain()

    def markIfCertain(self):
        row, col = self.coordinates
        for i in range(len(self.rowIndicatorsList)):
            left, right = getCertainBlockLimits(
                self.rowIndicatorsList, i, self.rowLength)
            if left <= col and right >= col:
                self.content = FILLED
                self.possibleRowBlocks = [i]
                self.rowIndicatorsList[i].addCell(self)
                break
        for i in range(len(self.colIndicatorsList)):
            top, bottom = getCertainBlockLimits(
                self.colIndicatorsList, i, self.colLength)
            if top <= row and bottom >= row:
                self.content = FILLED
                self.possibleColBlocks = [i]
                self.colIndicatorsList[i].addCell(self)
                break

    def markIfEmpty(self):
        for i in range(len(self.colIndicatorsList)):
            if self.colIndicatorsList[i].isFull():
                if i in self.possibleColBlocks:
                    self.possibleColBlocks.remove(i)
        if(self.possibleColBlocks == [-1]):
            self.content = EMPTY
            self.possibleRowBlocks = [-1]
        for i in range(len(self.rowIndicatorsList)):
            if self.rowIndicatorsList[i].isFull():
                if i in self.possibleRowBlocks:
                    self.possibleRowBlocks.remove(i)
        if(self.possibleRowBlocks == [-1]):
            self.content = EMPTY
            self.possibleColBlocks = [-1]

    def markWith(self, content, rowIndicator=-1, colIndicator=-1):
        self.content = content
        if(self.content == EMPTY):
            self.possibleColBlocks = [-1]
            self.possibleRowBlocks = [-1]
        if(rowIndicator != -1):
            self.row_indicator = rowIndicator
        if(colIndicator != -1):
            self.col_indicator = colIndicator

    def removeFromPossibleColList(self, index):
        if index in self.possibleColBlocks:
            self.possibleColBlocks.remove(index)
            if self.possibleColBlocks == [-1]:
                self.markWith(EMPTY)

    def removeFromPossibleRowList(self, index):
        if index in self.possibleRowBlocks:
            self.possibleRowBlocks.remove(index)
            if self.possibleRowBlocks == [-1]:
                self.markWith(EMPTY)

    def __str__(self) -> str:
        return self.content


class Indicator:
    def __init__(self, blockLength, axis):
        self.blockLength = blockLength
        self.cells = []
        self.axis = axis

    def __str__(self) -> str:
        return str(self.blockLength)

    def addCell(self, cell: Cell):
        self.cells.append(cell)

    def isFull(self) -> bool:
        return len(self.cells) == self.blockLength


column_indicators = [
    [7],
    [4, 4, 2],
    [4, 4, 2],
    [4, 4, 3],
    [4, 3, 6],
    [4, 4, 7],
    [4, 3, 7],
    [3, 2, 7],
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
row_indicators = [
    [3, 3],
    [6, 6],
    [8, 8],
    [9, 5, 3],
    [2, 8, 2],
    [1, 4, 1],
    [2, 7, 1],
    [2, 10, 3],
    [7, 4, 7],
    [6, 1, 2, 6],
    [5, 2, 2, 5],
    [2, 2, 3, 1],
    [3, 3],
    [4, 5],
    [4, 6],
    [5, 3],
    [7, 2],
    [6, 2],
    [3],
    [2]
]
bas = BlackAndSolve(column_indicators=column_indicators,
                    row_indicators=row_indicators)
bas.markEmptiesUsingFilled()
bas.markEmptiesUsingEmpty()

bas.printState()
