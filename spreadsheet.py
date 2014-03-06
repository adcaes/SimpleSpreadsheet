import re
import string

ROWS = 26
COLUMNS = 9


class SpreadSheetException(Exception):
    pass

class CircularReferenceException(SpreadSheetException):
    pass

class InvalidExpressionException(SpreadSheetException):
    pass

class InvalidCellIdException(SpreadSheetException):
    pass


class Cell(object):

    _cell_id_pattern = '[A-Z][1-9][0-6]?'

    def __init__(self, cell_id, expression):
        self.expression = expression
        # TODO: Delete cell_id from here?
        self.cell_id = cell_id
        self.references = self.extract_references()
        self.value = None

    def get_references(self):
        return self.references

    def extract_references(self):
        self.references = re.findall(self._cell_id_pattern, self.expression)
        return self.references

    def get_value(self):
        return self.value

    def evaluate(self, ref_values):
        try:
            self.value = float(eval(self.expression, {"__builtins__":None}, ref_values))
        except Exception as e:
            raise InvalidExpressionException(e)

        return self.value

    def __repr__(self):
        return '<Cell: %s>' % self.expression

class Spreadsheet(object):

    def __init__(self, spreadsheet_cells):
        self.data = []

        for i, raw_row in enumerate(spreadsheet_cells):
            row = []
            for j, raw_cell in enumerate(raw_row):
                cell_id = self._build_cell_id(i, j)
                cell = Cell(cell_id, raw_cell)
                row.append(cell)

            self.data.append(row)

    def get_value(self, row, column):
        # ROW and COL are 0 or 1 based? Assuming 0
        cell_id = self._build_cell_id(row, column)
        return self._get_value_from_id(cell_id)

    def _build_cell_id(self, row, column):
        self._validate_col_and_row(row, column)
        return string.uppercase[row] + str(column + 1)

    def _get_value_from_id(self, cell_id, visited=None):
        cell = self._get_cell_from_id(cell_id)
        cell_value = cell.get_value()
        if cell_value is not None:
            return cell_value

        if visited is None:
            visited = {cell_id}

        ref_values = {}
        refs = cell.get_references()
        for ref_cell_id in refs:

            if ref_cell_id in visited:
                raise CircularReferenceException("%s referenced from %s" % (ref_cell_id, cell_id))

            visited.add(ref_cell_id)
            ref_values[ref_cell_id] = self._get_value_from_id(ref_cell_id, visited)
            visited.discard(ref_cell_id)

        return cell.evaluate(ref_values)

    def _get_cell_from_id(self, cell_id):
        try:
            row_num = ord(cell_id[:1]) - ord('A')
            col_num = int(cell_id[1:]) - 1
            return self.data[row_num][col_num]
        except Exception as e:
            raise InvalidCellIdException(e)

    def _validate_col_and_row(self, row, column):
        if row < 0 or row >= ROWS or column < 0 or column >= COLUMNS:
            raise InvalidCellIdException('Row:%d Col:%d' % (row, column))

