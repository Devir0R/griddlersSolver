from typing import Tuple
from queue import Queue
import json

UNKNOWN = '◻'
FILLED = '◼'
EMPTY = 'X'
ROW = 0
COLUMN = 1


def compareRowIndicators(cell1: 'Cell', cell2: 'Cell'):
    if cell1.content == cell2.content and cell1.content == FILLED:
        if(len(cell1.possibleRowBlocks) == 1 and len(cell2.possibleRowBlocks) != 1):
            cell2.possibleRowBlocks = cell1.possibleRowBlocks
            cell2.rowIndicatorsList[cell1.possibleRowBlocks[0]].cells.append(
                cell2)
        if(len(cell1.possibleRowBlocks) != 1 and len(cell2.possibleRowBlocks) == 1):
            cell1.possibleRowBlocks = cell2.possibleRowBlocks
            cell1.rowIndicatorsList[cell2.possibleRowBlocks[0]].cells.append(
                cell1)


def compareColIndicators(cell1: 'Cell', cell2: 'Cell'):
    if cell1.content == cell2.content and cell1.content == FILLED:
        if(len(cell1.possibleColBlocks) == 1 and len(cell2.possibleColBlocks) != 1):
            cell2.possibleColBlocks = cell1.possibleColBlocks
            cell2.colIndicatorsList[cell1.possibleColBlocks[0]].cells.append(
                cell2)
        if(len(cell1.possibleColBlocks) != 1 and len(cell2.possibleColBlocks) == 1):
            cell1.possibleColBlocks = cell2.possibleColBlocks
            cell1.colIndicatorsList[cell2.possibleColBlocks[0]].cells.append(
                cell1)


def create_indicators_list(source_indicators: 'list[list[int]]', axis, lineLength):
    target_indicators = []
    for i in range(len(source_indicators)):
        target_indicators.append([])
        for j in range(len(source_indicators[i])):
            target_indicators[i].append(
                Indicator(j, axis, source_indicators[i], lineLength))
    return target_indicators


def getCertainBlockLimits(inds: 'list[Indicator]', block, maxLength):
    return getCertainBlockLimitsUsingNumberAsIndicators([ind.blockLength for ind in inds], block, maxLength)


def getCertainBlockLimitsUsingNumberAsIndicators(inds: 'list[int]', block, maxLength):
    start = maxLength - \
        sum(map(lambda ind: ind,
                inds[block:])) - len(inds[block:]) + 1
    end = sum(map(lambda ind: ind, inds[:block+1])) + block - 1
    return (start, end)


def inHowManyRanges(index, ranges):
    forEachRangeIsIndexPresent = map(
        lambda range: range[0] <= index and range[1] >= index, ranges)
    count = 0
    for isPresnt in forEachRangeIsIndexPresent:
        if(isPresnt):
            count += 1
    return count


def naiveRange(indicators: 'list[Indicator]', indicatorIndex, maxLength) -> Tuple[int, int]:
    return naiveRangeUsingNumberAsIndicators([ind.blockLength for ind in indicators], indicatorIndex, maxLength)


def naiveRangeUsingNumberAsIndicators(indicators: 'list[int]', indicatorIndex, maxLength):
    start, finish = getCertainBlockLimitsUsingNumberAsIndicators(
        indicators, indicatorIndex, maxLength)
    blockLength = indicators[indicatorIndex]
    if start <= finish:
        return (max(0, start+1-blockLength), min(maxLength-1, finish-1+blockLength))
    else:
        return (sum([ind+1 for ind in indicators[:indicatorIndex]]), maxLength - sum([ind+1 for ind in indicators[indicatorIndex+1:]])-1)


class BlackAndSolve:
    def __init__(self, column_indicators, row_indicators):
        self.column_indicators = create_indicators_list(
            column_indicators, COLUMN, len(row_indicators))
        self.row_indicators = create_indicators_list(
            row_indicators, ROW, len(column_indicators))
        self.board: list[list[Cell]] = [[Cell(j, i, self.row_indicators[j], self.column_indicators[i], len(row_indicators), len(column_indicators)) for i in range(len(self.column_indicators))]
                                        for j in range(len(self.row_indicators))]
        for row in self.board:
            for cell in row:
                cell.markIfEmpty()

    def solve(self):
        count = 0
        previosState = ''
        currentState = self.boardRepresentation()
        while not bas.isSolved() and count < 50 and previosState != currentState:
            count += 1
            self.markEmptiesUsingFilled()
            self.markEmptiesUsingEmpty()
            self.reevaluatePossibleBlocks()
            self.reevaluateIndicatorsRanges()
            self.fillGaps()
            self.unifyBlocks()
            self.emptyCellsIndicatorsInform()
            self.blockIndicatorIdentity()
            self.fillIndicatorsByTheirRange()
            self.cellWithNoPossibleIndicators()
            self.addCellsToIndicators()
            previosState = currentState
            currentState = self.boardRepresentation()
        return count

    def boardRepresentation(self):
        return str(self) + "\n" + \
            str([[ind.ranges for ind in row_ind]for row_ind in self.row_indicators]) + \
            "\n" + str([[ind.ranges for ind in col_ind]
                       for col_ind in self.column_indicators])

    @classmethod
    def fromJsonFile(cls, fileName):
        with open(fileName) as jsonFile:
            jsonObject = json.load(jsonFile)
            jsonFile.close()
        return cls(column_indicators=jsonObject["column_indicators"],
                   row_indicators=jsonObject["row_indicators"])

    def isSolved(self) -> bool:
        for row in self.board:
            for cell in row:
                if cell.content == UNKNOWN:
                    return False
        return True

    def reevaluateIndicatorsRanges(self):
        self.reevaluateIndicatorsRangesForOneList(self.row_indicators)
        self.reevaluateIndicatorsRangesForOneList(self.column_indicators)

    def reevaluateIndicatorsRangesForOneList(self, indicators: 'list[Indicator]'):
        for one_indicator_list in indicators:
            for i in range(len(one_indicator_list)):
                current_indicator: Indicator = one_indicator_list[i]
                if i+1 < len(one_indicator_list):
                    minimalStart = one_indicator_list[i +
                                                      1].minimalStart()-1
                    indexes_to_remove = []
                    for j in range(len(current_indicator.ranges)):
                        start, finish = current_indicator.ranges[j]
                        if start > minimalStart:
                            indexes_to_remove.append(j)
                        elif minimalStart >= start and minimalStart <= finish:
                            current_indicator.ranges[j] = (start, minimalStart)
                            if minimalStart - start + 1 < current_indicator.blockLength:
                                indexes_to_remove.append(j)
                    indexes_to_remove.reverse()
                    for index in indexes_to_remove:
                        del current_indicator.ranges[index]
                if i-1 >= 0:
                    minimalEnd = one_indicator_list[i -
                                                    1].minimalEnd()+1
                    indexes_to_remove = []
                    for j in range(len(current_indicator.ranges)):
                        start, finish = current_indicator.ranges[j]
                        if finish < minimalEnd:
                            indexes_to_remove.append(j)
                        elif minimalEnd >= start and minimalEnd <= finish:
                            current_indicator.ranges[j] = (
                                minimalEnd, finish)
                            if finish - minimalEnd + 1 < current_indicator.blockLength:
                                indexes_to_remove.append(j)
                    indexes_to_remove.reverse()
                    for index in indexes_to_remove:
                        del current_indicator.ranges[index]

    def addCellsToIndicators(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                cell: Cell = self.board[i][j]
                if(cell.content == FILLED):
                    if(len(cell.possibleColBlocks) == 1 and cell not in self.column_indicators[j][cell.possibleColBlocks[0]].cells):
                        current_col_indicator = self.column_indicators[j][cell.possibleColBlocks[0]]
                        current_col_indicator.addCell(cell)
                        self.ifIndicatorFullBlockLimits(current_col_indicator)
                    if(len(cell.possibleRowBlocks) == 1 and cell not in self.row_indicators[i][cell.possibleRowBlocks[0]].cells):
                        current_row_indicator = self.row_indicators[i][cell.possibleRowBlocks[0]]
                        current_row_indicator.addCell(cell)
                        self.ifIndicatorFullBlockLimits(current_row_indicator)

    def cellWithNoPossibleIndicators(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                exist_possible_row_indicator = False
                exist_possible_col_indicator = False
                for indic in self.row_indicators[i]:
                    for r in indic.ranges:
                        start, finish = r
                        if j >= start and j <= finish:
                            exist_possible_row_indicator = True
                            break
                    if exist_possible_row_indicator:
                        break
                for indic in self.column_indicators[j]:
                    for r in indic.ranges:
                        start, finish = r
                        if i >= start and i <= finish:
                            exist_possible_col_indicator = True
                            break
                    if exist_possible_col_indicator:
                        break
                if(not exist_possible_row_indicator or not exist_possible_col_indicator):
                    self.board[i][j].markWith(EMPTY)

    def fillIndicatorsByTheirRange(self):
        for row_index in range(len(self.row_indicators)):
            row_indic = self.row_indicators[row_index]
            for indicaror_index in range(len(row_indic)):
                indic = row_indic[indicaror_index]
                if(len(indic.ranges) == 1):
                    start, finish = indic.ranges[0]
                    maxStart = finish + 1 - indic.blockLength
                    minFinish = start - 1 + indic.blockLength
                    for i in range(maxStart, minFinish+1):
                        self.board[row_index][i].markWith(
                            FILLED, rowIndicator=indicaror_index)
                        indic.addCell(self.board[row_index][i])
                    self.ifIndicatorFullBlockLimits(indic)
        for col_index in range(len(self.column_indicators)):
            col_indic = self.column_indicators[col_index]
            for indicator_index in range(len(col_indic)):
                indic = col_indic[indicator_index]
                if(len(indic.ranges) == 1):
                    start, finish = indic.ranges[0]
                    maxStart = finish + 1 - indic.blockLength
                    minFinish = start - 1 + indic.blockLength
                    for i in range(maxStart, minFinish+1):
                        self.board[i][col_index].markWith(
                            FILLED, colIndicator=indicator_index)
                        indic.addCell(self.board[i][col_index])
                    self.ifIndicatorFullBlockLimits(indic)

    def ifIndicatorFullBlockLimits(self, ind: 'Indicator'):
        if(ind.isFull()):
            if ind.axis == COLUMN:
                start, end = min([cell.coordinates[0] for cell in ind.cells]), max(
                    [cell.coordinates[0] for cell in ind.cells])
            else:  # if ind.axis == ROW:
                start, end = min([cell.coordinates[1] for cell in ind.cells]), max(
                    [cell.coordinates[1] for cell in ind.cells])
            x, y = ind.cells[0].coordinates
            if(ind.axis == COLUMN):
                if(start-1 >= 0):
                    self.board[start-1][y].markWith(EMPTY)
                if(end+1 < len(self.board[x])):
                    self.board[end+1][y].markWith(EMPTY)
            if(ind.axis == ROW):
                if(start-1 >= 0):
                    self.board[x][start-1].markWith(EMPTY)
                if(end+1 < len(self.board)):
                    self.board[x][end+1].markWith(EMPTY)

    def blockIndicatorIdentity(self):
        start = -1
        for m in range(len(self.board)):
            row = self.board[m]
            for i in range(len(row)):
                if row[i].content == FILLED:
                    if start == -1:
                        start = i
                    else:
                        continue
                elif(start != -1):
                    possiblesIndicators = []
                    for j in range(len(self.row_indicators[m])):
                        if(self.row_indicators[m][j].canContainRange((start, i-1))):
                            possiblesIndicators.append(j)
                    if(len(possiblesIndicators) == 1):
                        decidedIndicator = self.row_indicators[m][possiblesIndicators[0]]
                        for k in range(start, i):
                            row[k].possibleRowBlocks = possiblesIndicators
                            if row[k] not in decidedIndicator.cells:
                                decidedIndicator.addCell(row[k])
                        self.ifIndicatorFullBlockLimits(
                            decidedIndicator)
                    start = -1
            start = -1
        start = -1
        for m in range(len(self.board[0])):
            col = [self.board[k][m] for k in range(len(self.board))]
            for i in range(len(col)):
                if col[i].content == FILLED:
                    if start == -1:
                        start = i
                    else:
                        continue
                elif(start != -1):
                    possiblesIndicators = []
                    for j in range(len(self.column_indicators[m])):
                        if(self.column_indicators[m][j].canContainRange((start, i-1))):
                            possiblesIndicators.append(
                                j)
                    if(len(possiblesIndicators) == 1):
                        for k in range(start, i):
                            col[k].possibleColBlocks = possiblesIndicators
                            decidedIndicator = self.column_indicators[m][possiblesIndicators[0]]
                            if col[k] not in decidedIndicator.cells:
                                decidedIndicator.addCell(col[k])
                                self.ifIndicatorFullBlockLimits(
                                    decidedIndicator)
                    start = -1

    def vaildate(self):
        for indicatorsOfRow in self.row_indicators:
            for indicator in indicatorsOfRow:
                if len(indicator.ranges) == 0:
                    raise RuntimeError("indicator with no ranges: ", indicator)
        for indicatorsOfCol in self.column_indicators:
            for indicator in indicatorsOfCol:
                if len(indicator.ranges) == 0:
                    raise RuntimeError("indicator with no ranges: ", indicator)

    def unifyBlocks(self):
        cellsQueue:  Queue[Cell] = Queue()
        upUsed, downUsed, rightUsed, leftUsed = set(), set(), set(), set()
        cellsQueue.put(self.board[0][0])
        while not cellsQueue.empty():
            cell = cellsQueue.get()
            x, y = cell.coordinates
            if(y < len(self.board[0])-1):
                rightCell = self.board[x][y+1]
                compareRowIndicators(cell, rightCell)
                if(rightCell not in rightUsed):
                    rightUsed.add(rightCell)
                    cellsQueue.put(rightCell)
            if(x < len(self.board)-1):
                downCell = self.board[x+1][y]
                compareColIndicators(cell, downCell)
                if(downCell not in downUsed):
                    downUsed.add(downCell)
                    cellsQueue.put(downCell)
        cellsQueue.put(self.board[-1][-1])
        while not cellsQueue.empty():
            cell = cellsQueue.get()
            x, y = cell.coordinates
            if(y > 0):
                leftCell = self.board[x][y-1]
                compareRowIndicators(cell, leftCell)
                if(leftCell not in leftUsed):
                    leftUsed.add(leftCell)
                    cellsQueue.put(leftCell)
            if(x > 0):
                upCell = self.board[x-1][y]
                compareColIndicators(cell, upCell)
                if(upCell not in upUsed):
                    upUsed.add(upCell)
                    cellsQueue.put(upCell)

    def emptyCellsIndicatorsInform(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                cell = self.board[i][j]
                if(cell.content == EMPTY):
                    for indicator in self.row_indicators[i]:
                        indicator.cellIsEmpty(cell)
                    for indicator in self.column_indicators[j]:
                        indicator.cellIsEmpty(cell)

    def reevaluatePossibleBlocks(self):
        for row in self.board:
            for cell in row:
                self.simpleReevaluation(cell)
        for row in self.board:
            for cell in row:
                row_indic = cell.rowIndicatorsList
                indexesToRemove = []
                for row_index in cell.possibleRowBlocks:
                    if(row_index != -1 and not cell.canBeIn(row_indic[row_index])):
                        indexesToRemove.append(row_index)
                for row_index in indexesToRemove:
                    cell.possibleRowBlocks.remove(row_index)
                col_indic = cell.colIndicatorsList
                indexesToRemove = []
                for col_index in cell.possibleColBlocks:
                    if(col_index != -1 and not cell.canBeIn(col_indic[col_index])):
                        indexesToRemove.append(col_index)
                for col_index in indexesToRemove:
                    cell.possibleColBlocks.remove(col_index)

    def simpleReevaluation(self, cell: 'Cell'):
        if(cell.content == EMPTY):
            cell.possibleColBlocks = [-1]
            cell.possibleRowBlocks = [-1]
        elif (cell.content == FILLED):
            if(-1 in cell.possibleColBlocks):
                cell.possibleColBlocks.remove(-1)
            if(-1 in cell.possibleRowBlocks):
                cell.possibleRowBlocks.remove(-1)

    def __str__(self) -> str:
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
        colIndReorgenize = colIndReorgenize + [[' ' if i < maxRowIndicatorsLength else '_' for i in range(
            len(self.board[0])+maxRowIndicatorsLength+1)]]
        board_copy = colIndReorgenize + board_copy
        stringifyMatrix = [[str(e) for e in row] for row in board_copy]
        lens = [max(map(len, col)) for col in zip(*stringifyMatrix)]
        fmt = ' '.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in stringifyMatrix]
        return '\n'.join(table)

    def printState(self):
        print(str(self))

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
        naiveRanges = [naiveRange(indicators, index, maxLength)
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
        naiveRanges = [naiveRange(indicators, index, maxLength)
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

    def fillGapsRow(self, line: 'list[Cell]'):
        startingRange, endingRange = -1, -1
        for i in range(len(line)):
            cell = line[i]
            if(len(cell.possibleRowBlocks) == 1 and cell.possibleRowBlocks[0] != -1):
                if(startingRange == -1):
                    startingRange = i
                else:
                    if cell.possibleRowBlocks[0] == line[startingRange].possibleRowBlocks[0]:
                        endingRange = i
                    else:
                        self.fillGapRow(line, startingRange, endingRange)
                        endingRange = -1
                        startingRange = i
            elif cell.content == EMPTY:
                self.fillGapRow(line, startingRange, endingRange)
                startingRange, endingRange = -1, -1
            elif len(line)-1 == i:
                self.fillGapRow(line, startingRange, endingRange)

    def fillGapsCol(self, line: 'list[Cell]'):
        startingRange, endingRange = -1, -1
        for i in range(len(line)):
            cell = line[i]
            if(len(cell.possibleColBlocks) == 1 and cell.possibleColBlocks[0] != -1):
                if(startingRange == -1):
                    startingRange = i
                else:
                    if cell.possibleColBlocks[0] == line[startingRange].possibleColBlocks[0]:
                        endingRange = i
                    else:
                        self.fillGapCol(line, startingRange, endingRange)
                        endingRange = -1
                        startingRange = i
            elif cell.content == EMPTY:
                self.fillGapCol(line, startingRange, endingRange)
                startingRange, endingRange = -1, -1
            elif len(line)-1 == i:
                self.fillGapCol(line, startingRange, endingRange)

    def fillGapCol(self, line: 'list[Cell]', startingRange: int, endingRange: int):
        for cellToMark in line[startingRange:endingRange+1]:
            cellToMark.markWith(
                FILLED, colIndicator=line[startingRange].possibleColBlocks[0])

    def fillGapRow(self, line: 'list[Cell]', startingRange: int, endingRange: int):
        for cellToMark in line[startingRange:endingRange+1]:
            cellToMark.markWith(
                FILLED, rowIndicator=line[startingRange].possibleRowBlocks[0])

    def fillGaps(self):
        for row in self.board:
            self.fillGapsRow(row)
        for i in range(len(self.board[0])):
            self.fillGapsCol([self.board[row][i]
                              for row in range(len(self.board))])


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
        # self.markIfCertain()

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
            if self.colIndicatorsList[i].isFull() and self not in self.colIndicatorsList[i].cells:
                if i in self.possibleColBlocks:
                    self.possibleColBlocks.remove(i)
        if(self.possibleColBlocks == [-1]):
            self.content = EMPTY
            self.possibleRowBlocks = [-1]
        for i in range(len(self.rowIndicatorsList)):
            if self.rowIndicatorsList[i].isFull() and self not in self.rowIndicatorsList[i].cells:
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
            self.possibleRowBlocks = [rowIndicator]
        if(colIndicator != -1):
            self.possibleColBlocks = [colIndicator]

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

    def canBeIn(self, indicator: 'Indicator') -> bool:
        for rang in indicator.ranges:
            start, finish = rang
            y, x = self.coordinates
            if start <= y and y <= finish if indicator.axis == COLUMN else start <= x and x <= finish:
                return True
        return False

    def __str__(self) -> str:
        return self.content


class Indicator:
    def __init__(self, index, axis, myLineIndicators: 'list[int]', maxLineLength):
        self.blockLength = myLineIndicators[index]
        self.cells = []
        self.axis = axis
        self.maxLineLength = maxLineLength
        self.ranges = [naiveRangeUsingNumberAsIndicators(
            myLineIndicators, index, maxLineLength)]
        if(len(self.ranges) == []):
            raise RuntimeError("ranges cannot be empty")

    def minimalStart(self):
        return max([range[1] for range in self.ranges])+1-self.blockLength

    def minimalEnd(self):
        return min([range[0] for range in self.ranges])-1+self.blockLength

    def __str__(self) -> str:
        return str(self.blockLength)

    def canContainRange(self, range):
        rangeStart, rangeFinish = range
        if rangeFinish-rangeStart+1 > self.blockLength:
            return False
        for r in self.ranges:
            start, finish = r
            if start <= rangeStart and finish >= rangeFinish:
                return True
        return False

    def addCell(self, cell: Cell):
        if cell in self.cells:
            return
        self.cells.append(cell)
        y, x = cell.coordinates
        start, end = min([pair[0] for pair in self.ranges]), max(
            [pair[1] for pair in self.ranges])
        if(self.axis == ROW):
            start = max(x-self.blockLength+1, start)
            end = min(end, x+self.blockLength-1)
        else:  # self.axis == COLUMN
            start = max(y-self.blockLength+1, start)
            end = min(end, y+self.blockLength-1)
        for i in range(len(self.ranges)):
            rangeStart, rangeEnd = self.ranges[i]
            if rangeStart <= start and start <= rangeEnd:
                self.ranges[i] = (start, rangeEnd)
                rangeStart, rangeEnd = self.ranges[i]
            if rangeStart <= end and end <= rangeEnd:
                self.ranges[i] = (rangeStart, end)
        self.ranges = list(filter(
            lambda rang: rang[1]-rang[0]+1 >= self.blockLength, self.ranges))
        self.ranges = list(filter(
            lambda rang: x <= rang[1] and x >= rang[0] if self.axis == ROW else y <= rang[1] and y >= rang[0], self.ranges))
        if(len(self.ranges) == 0):
            raise RuntimeError("ranges cannot be empty")

    def isFull(self) -> bool:
        return len(self.cells) == self.blockLength

    def cellIsEmpty(self, cell: Cell):
        y, x = cell.coordinates
        newRanges = []
        if self.axis == COLUMN:
            for i in range(len(self.ranges)):
                start, finish = self.ranges[i]
                if start <= y and y <= finish:
                    if y-start >= self.blockLength and finish - y >= self.blockLength:
                        newRanges.append((start, y-1))
                        newRanges.append((y+1, finish))
                    else:
                        if y-start < self.blockLength:
                            start = y+1
                        if finish - y < self.blockLength:
                            finish = y-1
                        if(finish-start+1 >= self.blockLength):
                            newRanges.append((start, finish))
                else:
                    newRanges.append(self.ranges[i])
        if self.axis == ROW:
            for i in range(len(self.ranges)):
                start, finish = self.ranges[i]
                if start <= x and x <= finish:
                    if x-start >= self.blockLength and finish - x >= self.blockLength:
                        newRanges.append((start, x-1))
                        newRanges.append((x+1, finish))
                    else:
                        if x-start < self.blockLength:
                            start = x+1
                        if finish - x < self.blockLength:
                            finish = x-1
                        if(finish-start+1 >= self.blockLength):
                            newRanges.append((start, finish))

                else:
                    newRanges.append(self.ranges[i])
        self.ranges = newRanges
        if(len(self.ranges) == 0):
            raise RuntimeError("ranges cannot be empty")


bas = BlackAndSolve.fromJsonFile("blackAndSolve2.json")
iterations = bas.solve()
bas.printState()
print("took " + str(iterations) + " iterations")
