INPUT_FILE_NAME = "io/input.txt"
OUTPUT_FILE_NAME = "io/output.txt"
ANS = []
MAX_COLLECTED_POINTS = 0
MAX_ACHIEVABLE = [[]]
SORTED_COLUMNS = [[]]
SLASH = []
BACK_SLASH = []
COLS = []


def visualize_grids_util(grids):
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


def is_position_safe(coordinate, grid_size):
    return COLS[coordinate[1]] and SLASH[coordinate[0] - coordinate[1] + grid_size - 1] and BACK_SLASH[
        coordinate[0] + coordinate[1]]


def make_safe(coordinate, grid_size):
    COLS[coordinate[1]] = True
    SLASH[coordinate[0] - coordinate[1] + grid_size - 1] = True
    BACK_SLASH[coordinate[0] + coordinate[1]] = True


def make_un_safe(coordinate, grid_size):
    COLS[coordinate[1]] = False
    SLASH[coordinate[0] - coordinate[1] + grid_size - 1] = False
    BACK_SLASH[coordinate[0] + coordinate[1]] = False


def place_police_officer_util(grid_size, points_grid, remaining_police, row, collected_points):
    global MAX_COLLECTED_POINTS

    if row < grid_size and (collected_points + MAX_ACHIEVABLE[row][remaining_police - 1]) <= MAX_COLLECTED_POINTS:
        return

    if remaining_police == 0:
        if collected_points > MAX_COLLECTED_POINTS:
            MAX_COLLECTED_POINTS = collected_points

    if 0 < remaining_police <= (grid_size - row) and row < grid_size:
        # Search without placing a police here
        place_police_officer_util(grid_size, points_grid, remaining_police, row + 1, collected_points)

        # Search by placing a police at each column sorted by maximum points
        for column_index in range(grid_size):
            column = SORTED_COLUMNS[row][column_index]
            new_coord = (row, column)
            if is_position_safe(new_coord, grid_size):
                remaining_police -= 1
                make_un_safe(new_coord, grid_size)
                place_police_officer_util(grid_size, points_grid, remaining_police, row + 1,
                                          collected_points + points_grid[row][column])
                make_safe(new_coord, grid_size)
                remaining_police += 1


def construct_max_achievable(number_of_police_officers, points_grid, grid_size):
    max_per_column = [max(grid) for grid in points_grid]
    global MAX_ACHIEVABLE
    MAX_ACHIEVABLE = [[0] * number_of_police_officers for x in range(grid_size)]
    for row in range(grid_size):
        for remaining_police in range(number_of_police_officers):
            MAX_ACHIEVABLE[row][remaining_police] = sum(
                sorted(max_per_column[row:], reverse=True)[:remaining_police + 1])


def construct_position_arrays(grid_size):
    global SLASH
    SLASH = [True] * ((2 * grid_size) - 1)
    global BACK_SLASH
    BACK_SLASH = [True] * ((2 * grid_size) - 1)
    global COLS
    COLS = [True] * grid_size


def construct_sorted_columns(points_grid, grid_size):
    global SORTED_COLUMNS
    SORTED_COLUMNS = [sorted(range(grid_size), key=lambda k: grid[k], reverse=True) for grid in points_grid]


def place_police_officers(grid_size, points_grid, number_of_police_officers):
    construct_max_achievable(number_of_police_officers, points_grid, grid_size)
    construct_position_arrays(grid_size)
    construct_sorted_columns(points_grid, grid_size)

    return place_police_officer_util(grid_size, points_grid, number_of_police_officers, 0, 0)


def write_result_to_output(result):
    output_file = open(OUTPUT_FILE_NAME, 'w')
    output_file.write(str(result))
    output_file.close()


def get_sorted_rows(grid_size):
    global SORTED_COLUMNS
    SORTED_COLUMNS = sorted(range(grid_size), key=lambda k: MAX_ACHIEVABLE[k], reverse=True)


def print_ans(pg):
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
    visualize_grids_util(points_grid)
    place_police_officers(grid_size, points_grid, number_of_police_officers)
    assert_output(MAX_COLLECTED_POINTS, points_grid)
    # write_result_to_output(MAX_COLLECTED_POINTS)


if __name__ == "__main__":
    run_homework()
