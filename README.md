Simple Spreadsheet
==================

Simple implementation of CLI based spreadsheet. The spreadsheet can evaluate mathematical expressions containing references to other cells.

The provided mathematical expressions will be evaluated using Python eval built-in function.
Any mathematical expression supported by the Python interpreter is allowed. This includes expressions with decimal and integer values, mathematical operators (+, -, *, /), and parenthesis.

Adding support for other Python built-in functions like sqrt(), abs(), max(), min() would require minimum changes. All built-in functions have been disabled for security reasons.

Notice that Python interpreter applies integer arithmetic to non-decimal numbers, this means that eval('1/2') evaluates to 1, instead eval('1./2') or eval('1/2.0') evaluates to 0.5.


## Public interface

### `Spreadsheet(spreadsheetCells)`

Class initialization. spreadSheetCells has to be a list of list with 26 rows and 9 columns.
Each cell must contain a String. Each cell can contain mathematical expressions and references to other cells.

### `getValue(row, column)`

Returns the value of the expression at cell[row][column].
row and column are 0 based. This means valid values for row are [0, 25] and for column [0, 8].

### `setValue(row, column, value)`

Stores a new expression at cell[row][column]. row and column are 0 based.


## Design

The spreadsheet is stored in the `Spreadsheet` class. The `Spreadsheet` class stores a matrix of `Cell` class instances.
The matrix is used to fetch a cell provided its row and column numbers.

Each `Cell` instance stores its mathematical expression and a dependent_cells set, containing references to all the cells that directly depend on it.
The dependent_cells set is used to invalidate the computed values of directly or indirectly dependent cells when a cell is updated.

**The algorithm for getting the value of a cell:**

    1 - The requested cell is accessed using the matrix.
    2 - If the value of the cell has already been computed, it is returned.
    3 - Otherwise, the expression is parsed and all the references to other cells extracted.
    4 - Recursively, the value of all the referenced cells is computed.
    5 - The expression is evaluated using Python eval function.
    6 - The computed value is stored in the cell to avoid recomputing it if the cell is later accessed.

The cost of getting a cell's value is constant if the cell doesn't have any reference or has already been computed.
In the case of getting the value of a cell with references, the cost is that of computing the value of all the referenced cells.
In the worst case this will require computing the value of all the other cells in the spreadsheet.

**The algorithm for setting the value of a cell:**

    1 - The cell is accessed using the matrix and the expression of the cell is updated.
    2 - If the cell's value is not None, its value is set to None as it is no longer valid.
    3 - In this case, using the list of dependent cells, all the values of directly and indirectly dependent cells are set to None.
    4 - The depentent_cell sets of the old and new referenced cells are updated.

The cost of setting the value of a cell is constant if no other cell references it or the value of the cell hasn't been computed.
Otherwise, the cost is that of setting to None the value of all dependent cells that have been computed. In the worst case this will mean setting to None the value of all the cells in the spreadsheet.
