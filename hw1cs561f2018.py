INPUT_FILE_NAME = "input.txt"
OUTPUT_FILE_NAME = "output.txt"
ANS = []
MAX_COLLECTED_POINTS = 0
MAX_ACHIEVABLE = []
SORTED_COLUMNS = [[]]
SORTED_ROWS = []


def visualize_grids(grids):
    for grid in grids:
        print(grid)


def get_input():
    f = open(INPUT_FILE_NAME, "r")
    grid_size = int(f.readline())
    number_of_police_officers = int(f.readline())
    number_of_scooters = int(f.readline())
    all_scooter_positions = []
    for nos in range(number_of_scooters):
        scooter_positions = []
        for timestamp in range(12):
            x, y = [int(coordinate) for coordinate in f.readline().split(",")]
            scooter_positions.append((x, y))
        all_scooter_positions.append(scooter_positions)
    return grid_size, number_of_police_officers, all_scooter_positions


def construct_points_grid(grid_size, all_scooter_positions):
    points_grid = [[0] * grid_size for x in range(grid_size)]
    for scooter_positions in all_scooter_positions:
        for scooter_position in scooter_positions:
            x, y = scooter_position
            points_grid[x][y] += 1
    return points_grid


def is_position_safe(placed_police_officers_coordinate, new_police_coordinate):
    for coordinate in placed_police_officers_coordinate:
        if is_same_row(new_police_coordinate, coordinate) or \
                is_same_col(new_police_coordinate, coordinate) or \
                is_same_diagnol(new_police_coordinate, coordinate):
            return False
    return True


def is_same_diagnol(new_police_coordinate, coordinate):
    return abs(coordinate[0] - new_police_coordinate[0]) == abs(coordinate[1] - new_police_coordinate[1])


def is_same_col(new_police_coordinate, coordinate):
    return coordinate[1] == new_police_coordinate[1]


def is_same_row(new_police_coordinate, coordinate):
    return coordinate[0] == new_police_coordinate[0]


def place_police_officers_util(grid_size, points_grid, placed_police_officers_coordinate, number_of_police_officers,
                               row, collected_points):
    remaining_police = number_of_police_officers - len(placed_police_officers_coordinate)

    global MAX_COLLECTED_POINTS
    if row < grid_size and (collected_points + sum(
            sorted(MAX_ACHIEVABLE[row:], reverse=True)[:remaining_police])) <= MAX_COLLECTED_POINTS:
        return

    if remaining_police == 0:
        global ANS
        if collected_points > MAX_COLLECTED_POINTS:
            MAX_COLLECTED_POINTS = collected_points
            ANS = placed_police_officers_coordinate[:]

    if 0 < remaining_police <= (grid_size - row) and row < grid_size:
        for column_index in range(grid_size):
            column = SORTED_COLUMNS[row][column_index]
            # Search by placing a police here
            if is_position_safe(
                    placed_police_officers_coordinate,
                    (row, column)):
                placed_police_officers_coordinate.append((row, column))
                place_police_officers_util(grid_size, points_grid,
                                           placed_police_officers_coordinate,
                                           number_of_police_officers, row + 1,
                                           collected_points + points_grid[row][column])
                placed_police_officers_coordinate.pop()

        # Search without placing a police here
        place_police_officers_util(grid_size, points_grid, placed_police_officers_coordinate, number_of_police_officers,
                                   row + 1, collected_points)


def place_police_officers(grid_size, points_grid, number_of_police_officers):
    global MAX_ACHIEVABLE
    MAX_ACHIEVABLE = [max(grid) for grid in points_grid]

    # global SORTED_ROWS
    # SORTED_ROWS = get_sorted_rows(grid_size)

    global SORTED_COLUMNS
    SORTED_COLUMNS = get_sorted_columns(points_grid, grid_size)

    placed_police_officers_coordinate = []
    return place_police_officers_util(grid_size, points_grid, placed_police_officers_coordinate,
                                      number_of_police_officers, 0, 0)


def write_result_to_output(result):
    output_file = open(OUTPUT_FILE_NAME, 'w')
    output_file.write(str(result))
    output_file.close()


def get_sorted_columns(points_grid, grid_size):
    return [sorted(range(grid_size), key=lambda k: grid[k], reverse=True) for grid in points_grid]


def get_sorted_rows(grid_size):
    return sorted(range(grid_size), key=lambda k: MAX_ACHIEVABLE[k], reverse=True)


def print_ans(pg):
    print("Sorted rows : " + str(SORTED_ROWS))
    print("Sorted columns : " + str(SORTED_COLUMNS))
    print("Answer : ")
    print(ANS)
    print(" + ".join([str(pg[a[0]][a[1]]) for a in ANS]) + " = " + str(sum([pg[a[0]][a[1]] for a in ANS])))
    n = len(pg)
    grids = [[" X "] * n for x in range(n)]
    for a in ANS:
        grids[a[0]][a[1]] = " P "
    for grid in grids:
        print(" | ".join(grid))


def assert_output(max_points, pg):
    print_ans(pg)
    print("Actual output : " + str(max_points))
    f = open(OUTPUT_FILE_NAME, "r")
    expected_output = int(f.readline())
    print("Expected output : " + str(expected_output))
    assert max_points == expected_output
    f.close()


def run_homework():
    (grid_size, number_of_police_officers, all_scooter_positions) = get_input()
    points_grid = construct_points_grid(grid_size, all_scooter_positions)
    # visualize_grids(points_grid)
    place_police_officers(grid_size, points_grid, number_of_police_officers)
    # assert_output(MAX_COLLECTED_POINTS, points_grid)
    write_result_to_output(MAX_COLLECTED_POINTS)


if __name__ == "__main__":
    run_homework()
