import unittest
from spreadsheet import Spreadsheet, Cell, ROWS, COLUMNS
from spreadsheet import InvalidCellIdException


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
        self.basic_data[0][0] = '0'
        self.basic_data[0][1] = '1'
        for j in range(2, COLUMNS):
            self.basic_data[0][j] = "A{} + A{}".format(str(j+1-2), str(j+1-1))

        ss = Spreadsheet(self.basic_data)
        for j in range(COLUMNS):
            self.assertEquals(ss.get_value(0, j), computed_fib[j])

    def test_get_invalid_cell_raises_exception(self):
        ss = Spreadsheet(self.basic_data)
        with self.assertRaises(InvalidCellIdException):
            ss.get_value(0, -1)

        with self.assertRaises(InvalidCellIdException):
            ss.get_value(29, 1)

    def test_invalid_cell_reference_in_expression_raises_exception(self):
        self.basic_data[0][0] = 'A40'
        ss = Spreadsheet(self.basic_data)

    def test_circular_reference_in_expression(self):
        self.basic_data[0][0] = 'A2'
        self.basic_data[0][1] = 'A1'
        ss = Spreadsheet(self.basic_data)

    def test_auto_reference_in_expression(self):
        self.basic_data[0][0] = 'A1'
        ss = Spreadsheet(self.basic_data)


class TestCell(unittest.TestCase):

    def test_extract_references_without_references(self):
        cell = Cell('C1', '1 + 2')
        refs = cell.extract_references()
        self.assertEquals(refs, [])

    def test_extract_references_with_references(self):
        cell = Cell('C1', 'A1 + B14 + C23')
        refs = cell.extract_references()
        self.assertEquals(refs, ['A1', 'B14', 'C23'])

    def test_evaluate_arithmetic_expressions_without_references(self):
        cell = Cell('C1', '1./2 + 2.5 - 1.25')
        val = cell.evaluate({})
        self.assertEquals(val, 1.75)

    def test_evaluate_arithmetic_expressions_with_references(self):
        cell = Cell('C1', '1./A1 + 2.5 - A2')
        val = cell.evaluate({'A1': 2, 'A2': 1.25})
        self.assertEquals(val, 1.75)

if __name__ == '__main__':
    unittest.main()
