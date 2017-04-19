# prints nice grids. Sample usage:
"""
>>> d = {
...     (0, "("): "s1",
...     (1, "("): "s1",
...     (1, ")"): "s2",
...     (2, "$"): "r2",
...     (2, "("): "r2",
...     (2, ")"): "r2",
...     (3, "("): "s1",
...     (4, ")"): "s5",
...     (5, "$"): "r1",
...     (5, "("): "r1",
...     (5, ")"): "r1",
...     (6, "$"): "acc"
... }
>>> print(prettyprint.dict_print(d))

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

>>> matrix = [
...     ["1","2"],
...     ["foo", "bar"]
... ]
>>> print(prettyprint.grid_print(matrix))

+---+---+
|  1|  2|
+---+---+
|foo|bar|
+---+---+

"""


def dict_print(d):
    """returns a printable representation of the dict, rendered as a grid."""
    l = _grid_from_dict(d)
    l = _grid_map(lambda x: " " + x + " ", l)
    return grid_print(l)


def grid_print(grid):
    """returns a printable grid representation of a 2-d list of strings."""
    widths = [_max_width(grid, x) for x in range(len(grid[0]))]
    row_separator = "\n" + _enclosed_join("+", ["-" * x for x in widths]) + "\n"
    return _enclosed_join(row_separator, [_row_print(row, widths) for row in grid])


def _enclosed_join(separator, seq):
    """like regular join, but the separator goes on the ends too."""
    return separator + separator.join(seq) + separator


def _row_print(row, widths):
    """prints a sequence of items, each one padded according to its given width."""
    return _enclosed_join("|", [x[0].rjust(x[1]) for x in zip(row, widths)])


def _max_width(grid, column):
    """finds the widest element in one column of a grid."""
    return max(len(row[column]) for row in grid)


def _grid_map(func, grid):
    """like map, but for 2d lists."""
    return [list(map(func, x)) for x in grid]


def _grid_from_dict(d):
    """
    given a dict `d`, whose keys are 2 element tuples,
    makes a grid with the keys as axes and the values as interior values.
    ex. In the sample grid at the top of this page,
    0-6, $, (, ) are keys, and s1, r2, etc are values.
    """
    first_keys = list(set([x[0] for x in d]))
    second_keys = list(set([x[1] for x in d]))
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
