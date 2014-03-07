import unittest
from spreadsheet import Spreadsheet, Cell
from spreadsheet import InvalidCellIdException, CircularReferenceException


class TestSpreadsheet(unittest.TestCase):

    def setUp(self):
        self.basic_data = []
        for r in range(Spreadsheet.ROWS):
            self.basic_data.append([str(r*Spreadsheet.COLUMNS + c) for c in range(Spreadsheet.COLUMNS)])


class TestInitializeSpreadsheet(TestSpreadsheet):

    def test_initialize_and_access_spreadsheet_without_references(self):
        ss = Spreadsheet(self.basic_data)
        for i in range(Spreadsheet.ROWS):
            for j in range(Spreadsheet.COLUMNS):
                continue
                self.assertEquals(ss.get_value(i, j), float(self.basic_data[i][j]))

    def test_initialize_and_access_spreadsheet_with_references(self):
        self.basic_data[0][0] = "10"
        for j in range(1, Spreadsheet.COLUMNS):
            self.basic_data[0][j] = "A1"

        ss = Spreadsheet(self.basic_data)
        for j in range(Spreadsheet.COLUMNS):
            self.assertEquals(ss.get_value(0, j), 10)

    def test_initialize_spreadsheet_with_cell_referencing_non_existing_cell_raises_exception(self):
        self.basic_data[0][0] = 'A40'
        with self.assertRaises(InvalidCellIdException):
            Spreadsheet(self.basic_data)


class TestGetValue(TestSpreadsheet):

    def test_get_non_existing_cell_raises_exception(self):
        ss = Spreadsheet(self.basic_data)
        with self.assertRaises(InvalidCellIdException):
            ss.get_value(0, -1)

        with self.assertRaises(InvalidCellIdException):
            ss.get_value(29, 1)

    def test_get_cell_with_circular_reference_raises_exception(self):
        self.basic_data[0][0] = 'A2'
        self.basic_data[0][1] = 'A1'
        ss = Spreadsheet(self.basic_data)
        with self.assertRaises(CircularReferenceException):
            ss.get_value(0, 0)

    def test_get_cell_with_auto_reference_raises_exception(self):
        self.basic_data[0][0] = 'A1'
        ss = Spreadsheet(self.basic_data)
        with self.assertRaises(CircularReferenceException):
            ss.get_value(0, 0)

    def test_get_cells_with_references(self):
        computed_fib = [0, 1, 1, 2, 3, 5, 8, 13, 21]
        self.basic_data[0][0] = '0'
        self.basic_data[0][1] = '1'
        for j in range(2, Spreadsheet.COLUMNS):
            self.basic_data[0][j] = "A{} + A{}".format(str(j+1-2), str(j+1-1))

        ss = Spreadsheet(self.basic_data)
        for j in range(Spreadsheet.COLUMNS - 1, -1, -1):
            self.assertEquals(ss.get_value(0, j), computed_fib[j])


class TestSetValue(TestSpreadsheet):

    def test_set_value_without_references(self):
        ss = Spreadsheet(self.basic_data)
        new_value = ss.get_value(4, 5) + 10
        ss.set_value(4, 5, str(new_value))
        self.assertEquals(ss.get_value(4, 5), new_value)

    def test_set_value_with_references(self):
        self.basic_data[4][5] = 'A9'
        ss = Spreadsheet(self.basic_data)

        new_value = ss.get_value(0, 8) + ss.get_value(1, 5) + 10

        ss.set_value(4, 5, 'A9 + B6 + 10')
        self.assertEquals(ss.get_value(4, 5), new_value)

    def test_set_value_with_dependent_cells(self):
        self.basic_data[0][0] = '0'
        for j in range(1, Spreadsheet.COLUMNS):
            self.basic_data[0][j] = 'A%d + 1' % j

        ss = Spreadsheet(self.basic_data)
        for j in range(Spreadsheet.COLUMNS):
            ss.get_value(0, j)

        ss.set_value(0, 0, '1')
        for j in range(Spreadsheet.COLUMNS - 1, -1, -1):
            self.assertEquals(ss.get_value(0, j), j+1)

    def test_set_value_modifying_references(self):
        self.basic_data[0][0] = 'A2'
        self.basic_data[1][0] = 'A1'
        ss = Spreadsheet(self.basic_data)
        self.assertEquals(ss.get_value(0, 0), float(self.basic_data[0][1]))
        self.assertEquals(ss.get_value(1, 0), float(self.basic_data[0][1]))

        ss.set_value(0, 0, 'A3')
        self.assertEquals(ss.get_value(0, 0), float(self.basic_data[0][2]))
        self.assertEquals(ss.get_value(1, 0), float(self.basic_data[0][2]))

class TestCell(unittest.TestCase):

    def test_extract_references_without_references(self):
        cell = Cell('C1', '1 + 2')
        self.assertEquals(cell.get_references(), [])

    def test_extract_references_with_references(self):
        cell = Cell('C1', 'A1 + B14 + C23')
        self.assertEquals(cell.get_references(), ['A1', 'B14', 'C23'])

    def test_evaluate_arithmetic_expressions_without_references(self):
        cell = Cell('C1', '(1./2 + 2.5 - 1.25)*0.5')
        val = cell.evaluate({})
        self.assertEquals(val, 0.875)

    def test_evaluate_arithmetic_expressions_with_references(self):
        cell = Cell('C1', '(1./A1 + 2.5 - A2)*0.5')
        val = cell.evaluate({'A1': 2, 'A2': 1.25})
        self.assertEquals(val, 0.875)

if __name__ == '__main__':
    unittest.main()
