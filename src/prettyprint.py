#prints nice grids. Example output:
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

#adds spaces before string x until it is `width` characters long
def pad(x, width):
    while len(x) < width:
        x = " " + x
    return x

#like regular join, but the seperator goes on the ends too.
def enclosed_join(seperator, seq):
    return seperator + seperator.join(seq) + seperator

#prints a sequence of items, each one padded according to its given width.
def row_print(row, widths):
    return enclosed_join("|",map(lambda x: pad(x[0], x[1]), zip(row, widths)))

#finds the widest element in one column of a grid
def max_width(grid, column):
    return max(len(row[column]) for row in grid)

#returns a printable grid representation
def grid_print(grid):
    widths = [max_width(grid, x) for x in range(len(grid[0]))]
    rowSeperator = "\n" + enclosed_join("+",map(lambda x: "-" * x, widths)) + "\n"
    return enclosed_join(rowSeperator, [row_print(row, widths) for row in grid])

#like map, but for 2d arrays.
def grid_map(func, grid):
    return map(lambda x: map(func, x), grid)

#given a dict `d`, whose keys are 2 element tuples,
#makes a grid with the keys as axes and the values as interior values.
#ex. In the sample grid at the top of this page,
#0-6, $, (, ) are keys, and s1, r2, etc are values.
def grid_from_dict(d):
    firstKeys = list(set(map(lambda x: x[0], d)))
    secondKeys = list(set(map(lambda x: x[1], d)))
    firstKeys.sort()
    secondKeys.sort()
    ret = [["X"]]
    for k2 in secondKeys:
        ret[0].append(k2)
    for k1 in firstKeys:
        row = [k1]
        for k2 in secondKeys:
            key = (k1, k2)
            row.append(d.get(key, ""))
        ret.append(row)
    return grid_map(str, ret)

#returns a printable representation of the dict, rendered as a grid.
def dict_print(d):
    l = grid_from_dict(d)
    l = grid_map(lambda x: " " + x + " ", l)
    return grid_print(l)