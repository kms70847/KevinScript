# prints nice grids. Example output:
"""
+---+-----+----+----+
| X |   $ |  ( |  ) |
+---+-----+----+----+
| 0 |     | s1 |    |
+---+-----+----+----+
| 1 |     | s1 | s2 |
+---+-----+----+----+
| 2 |  r2 | r2 | r2 |
+---+-----+----+----+
| 3 |     | s1 |    |
+---+-----+----+----+
| 4 |     |    | s5 |
+---+-----+----+----+
| 5 |  r1 | r1 | r1 |
+---+-----+----+----+
| 6 | acc |    |    |
+---+-----+----+----+
"""


# adds spaces before string x until it is `width` characters long
def _pad(x, width):
    while len(x) < width:
        x = " " + x
    return x


# like regular join, but the separator goes on the ends too.
def _enclosed_join(separator, seq):
    return separator + separator.join(seq) + separator


# prints a sequence of items, each one _padded according to its given width.
def _row_print(row, widths):
    return _enclosed_join("|", map(lambda x: _pad(x[0], x[1]), zip(row, widths)))


# finds the widest element in one column of a grid
def _max_width(grid, column):
    return max(len(row[column]) for row in grid)


# returns a printable grid representation
def grid_print(grid):
    widths = [_max_width(grid, x) for x in range(len(grid[0]))]
    row_separator = "\n" + _enclosed_join("+", map(lambda x: "-" * x, widths)) + "\n"
    return _enclosed_join(row_separator, [_row_print(row, widths) for row in grid])


# like map, but for 2d arrays.
def _grid_map(func, grid):
    return map(lambda x: map(func, x), grid)


# given a dict `d`, whose keys are 2 element tuples,
# makes a grid with the keys as axes and the values as interior values.
# ex. In the sample grid at the top of this page,
# 0-6, $, (, ) are keys, and s1, r2, etc are values.
def _grid_from_dict(d):
    first_keys = list(set(map(lambda x: x[0], d)))
    second_keys = list(set(map(lambda x: x[1], d)))
    first_keys.sort()
    second_keys.sort()
    ret = [["X"]]
    for k2 in second_keys:
        ret[0].append(k2)
    for k1 in first_keys:
        row = [k1]
        for k2 in second_keys:
            key = (k1, k2)
            row.append(d.get(key, ""))
        ret.append(row)
    return _grid_map(str, ret)


# returns a printable representation of the dict, rendered as a grid.
def dict_print(d):
    l = _grid_from_dict(d)
    l = _grid_map(lambda x: " " + x + " ", l)
    return grid_print(l)
