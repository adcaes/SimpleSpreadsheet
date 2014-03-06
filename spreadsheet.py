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

    cell_id_pattern = '[A-Z][1-9][0-6]?'

    def __init__(self, cell_id, expression):
        self.expression = expression
        self.cell_id = cell_id
        self.references = self.extract_references()
        self.value = None

        self.evaluate()

    def get_references(self):
        return self.references

    def extract_references(self):
        re.findall(self.cell_id_pattern, self.expression)

    def validate(self):
        pass

    def get_value(self):
        return self.value

    def evaluate(self, ref_values):
        try:
            self.value = eval(self.expression, {"__builtins__":None}, ref_values)
        except Exception as e:
            raise InvalidExpressionException()

class Spreadsheet(object):

    def __init__(self, spreadsheet_cells):
        self.data = []

        for i, raw_row in enumerate(spreadsheet_cells):
            row = []
            for j, raw_cell in enumerate(raw_row):
                cell_id = self.build_cell_id(i, j)
                cell = Cell(cell_id, raw_cell)
                row.append(cell)

            self.data.append(row)

    def build_cell_id(self, row, cloumn):
        try:
            return string.uppercase[row] + str(column)
        except:
            raise InvalidCellIdException()

    def get_value(self, row, column):
        # ROW and COL are 0 or 1 based? Assuming 0
        cell_id = build_cell_id(row, cloumn)
        return self.get_value_from_id(cell_id)

    def get_value_from_id(self, cell_id, visited=None):
        cell = self.get_cell_from_id(cell_id)
        cell_value = cell.get_value()
        if cell_value is not None:
            return cell_value

        if visited is None:
            visited = {cell_id}

        ref_values = []
        refs = cell.get_references()
        for ref_cell_id in refs:

            if ref_cell_id in visited:
                raise CircularReferenceException()

            visited.add(ref_cell_id)
            ref_values[ref_cell_id] = self.get_value_from_id(ref_cell_id, visited)
            visited.discard(ref_cell_id)

        return cell.evaluate(ref_values).get_value()

    def get_cell_from_id(self, cell_id):
        try:
            return self.data[cell_id[:1]][cell_id[1:]]
        except:
            raise InvalidCellIdException()

    def set_value(row, column, value):
        pass
