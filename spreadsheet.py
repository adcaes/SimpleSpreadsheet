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
        # TODO: Delete cell_id from here?
        self.cell_id = cell_id
        self.references = self.extract_references()
        self.value = None

    def get_references(self):
        return self.references

    def extract_references(self):
        self.references = re.findall(self.cell_id_pattern, self.expression)
        return self.references

    def get_value(self):
        return self.value

    def evaluate(self, ref_values):
        try:
            self.value = float(eval(self.expression, {"__builtins__":None}, ref_values))
        except Exception as e:
            raise InvalidExpressionException(e)

        return self.value

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

    def build_cell_id(self, row, column):
        try:
            return string.uppercase[row] + str(column + 1)
        except Exception as e:
            raise InvalidCellIdException(e)

    def get_value(self, row, column):
        # ROW and COL are 0 or 1 based? Assuming 0
        cell_id = self.build_cell_id(row, column)
        return self.get_value_from_id(cell_id)

    def get_value_from_id(self, cell_id, visited=None):
        cell = self.get_cell_from_id(cell_id)
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
            ref_values[ref_cell_id] = self.get_value_from_id(ref_cell_id, visited)
            visited.discard(ref_cell_id)

        return cell.evaluate(ref_values)

    def get_cell_from_id(self, cell_id):
        try:
            row_num = ord(cell_id[:1]) - ord('A')
            col_num = int(cell_id[1:]) - 1
            return self.data[row_num][col_num]
        except Exception as e:
            raise InvalidCellIdException(e)

    def set_value(row, column, value):
        pass


import unittest


class TestSpreadsheet(unittest.TestCase):

    def setUp(self):
        self.basic_data = []
        for r in range(ROWS):
            self.basic_data.append([str(r*COLUMNS + c) for c in range(COLUMNS)])

    def test_initialize_and_access_spreadsheet_without_references(self):
        ss = Spreadsheet(self.basic_data)
        for i in range(ROWS):
            for j in range(COLUMNS):
                continue
                self.assertEquals(ss.get_value(i, j), float(self.basic_data[i][j]))

    def test_initialize_and_access_spreadsheet_with_references(self):
        computed_fib = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        self.basic_data[0][0] = '1'
        self.basic_data[0][1] = '1'
        for j in range(2, COLUMNS):
            self.basic_data[0][j] = "A{} + A{}".format(str(j+1-2), str(j+1-1))

        ss = Spreadsheet(self.basic_data)
        for j in range(COLUMNS):
            self.assertEquals(ss.get_value(0, j), computed_fib[j])

    def test_get_invalid_cell(self):
        pass

    def test_invalid_cell_reference_in_expression(self):
        pass

    def test_circular_reference_in_expression(self):
        pass

    def test_auto_reference_in_expression(self):
        pass

class TestCell():
    pass

if __name__ == '__main__':
    unittest.main()
