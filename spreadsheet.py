import re
import string

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
        self.cell_id = cell_id
        self.expression = expression
        self.dependent_cells = set()
        self.value = None

    def get_references(self):
        '''
        Return the list of cell ids referenced in the cell.
        '''
        return re.findall(self._cell_id_pattern, self.expression)

    def add_dependent_cell(self, cell):
        self.dependent_cells.add(cell)

    def remove_dependent_cell(self, cell):
        self.dependent_cells.remove(cell)

    def get_dependent_cells(self):
        return self.dependent_cells

    def update_expression(self, expression):
        self.expression = expression
        self.value = None

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def evaluate(self, ref_values):
        try:
            # For security reasons, eval is called with an empty globals dict and
            # a locals dict only containing the referenced cells values.
            val = eval(self.expression, {"__builtins__":None}, ref_values)
            self.value = float(val)
        except Exception as e:
            raise InvalidExpressionException(e)

        return self.value

    def get_expression(self):
        return self.expression

    def __repr__(self):
        return '<Cell: %s>' % self.expression

    def __hash__(self):
        return hash(self.cell_id)

class Spreadsheet(object):

    ROWS = 26
    COLUMNS = 9

    def __init__(self, spreadsheet_cells):
        '''
        Initialize the spreadsheet. All values should be strings.
        Cell validation is not performed until the value of the cell is calculated.
        '''

        if not spreadsheet_cells or len(spreadsheet_cells) != self.ROWS \
             or len(spreadsheet_cells[0]) != self.COLUMNS:
            raise SpreadSheetException("Invalid input data")

        self.cells = []
        for i, raw_row in enumerate(spreadsheet_cells):
            row = [Cell(self._build_cell_id(i, j), raw_cell)
                   for (j, raw_cell) in enumerate(raw_row)]
            self.cells.append(row)

        self._fill_cell_dependencies()

    def get_value(self, row, column):
        '''
        Return the cell value, uses 0 based row and col number.
        '''
        self._validate_cell_index(row, column)
        cell = self.cells[row][column]
        return self._get_value_from_cell(cell)

    def set_value(self, row, column, value):
        '''
        Update the expression stored in the cell, uses 0 based row and col number.
        Updates the referece graph and sets to None the computed
        values of all the dependent cells.
        '''

        self._validate_cell_index(row, column)
        cell = self.cells[row][column]
        if cell.get_value() is not None:
            self._set_dependent_cells_value_to_none(cell)

        self._remove_cell_from_referenced_cells(cell)
        cell.update_expression(value)
        self._add_cell_to_referenced_cells(cell)

    def _fill_cell_dependencies(self):
        for row in self.cells:
            for cell in row:
                self._add_cell_to_referenced_cells(cell)

    def _add_cell_to_referenced_cells(self, cell):
        for ref_cell_id in cell.get_references():
            self._get_cell_from_id(ref_cell_id) \
                .add_dependent_cell(cell)

    def _remove_cell_from_referenced_cells(self, cell):
        for ref_cell_id in cell.get_references():
            self._get_cell_from_id(ref_cell_id) \
                .remove_dependent_cell(cell)

    def _set_dependent_cells_value_to_none(self, cell):
        for dep_cell in cell.get_dependent_cells():
            if dep_cell.get_value() is not None:
                dep_cell.set_value(None)
                self._set_dependent_cells_value_to_none(dep_cell)

    def _validate_cell_index(self, row, column):
        if row < 0 or row >= self.ROWS or column < 0 or column >= self.COLUMNS:
            raise InvalidCellIdException('Row:%d Col:%d' % (row, column))

    def _build_cell_id(self, row, column):
        return string.uppercase[row] + str(column + 1)

    def _get_value_from_cell(self, cell, visited=None):
        cell_value = cell.get_value()
        if cell_value is not None:
            return cell_value

        if visited is None:
            visited = {cell.cell_id}

        ref_values = {}
        for ref_cell_id in cell.get_references():

            if ref_cell_id in visited:
                msg = "%s referenced from %s" % (ref_cell_id, cell.cell_id)
                raise CircularReferenceException(msg)

            visited.add(ref_cell_id)
            ref_cell = self._get_cell_from_id(ref_cell_id)
            ref_values[ref_cell_id] = self._get_value_from_cell(ref_cell, visited)
            visited.discard(ref_cell_id)

        return cell.evaluate(ref_values)

    def _get_cell_from_id(self, cell_id):
        try:
            row_num = ord(cell_id[:1]) - ord('A')
            col_num = int(cell_id[1:]) - 1
            return self.cells[row_num][col_num]
        except Exception as e:
            raise InvalidCellIdException(e)
