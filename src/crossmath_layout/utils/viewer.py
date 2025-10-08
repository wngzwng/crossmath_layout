import pandas

def print_board(layout_info: str, width: int, height: int):
    pandas.set_option("display.max_rows", None)
    pandas.set_option("display.max_columns", None)
    pandas.set_option("display.width", 2000)

    board = [
        [int(layout_info[y * width + x]) for x in range(width)]
        for y in range(height)
    ]
    """
     "■" : "□"
    """
    temp_map = [
        [" " for _ in range(width)] for _ in range(height)
    ]
    for row in range(height):
        for col in range(width):
            value = board[row][col]
            if value == 0:
                temp_map[row][col] = " "
            else:
                temp_map[row][col] = "■"

    df = pandas.DataFrame(temp_map)
    print(df)
    pandas.reset_option("display.max_rows")
    pandas.reset_option("display.max_columns")
    pandas.reset_option("display.width")