import sys

INPUT_FILE_NAME = "input.txt"
OUTPUT_FILE_NAME = "output.txt"
ANS = []


def visualize_scooters(grid_size, all_scooter_positions):
    grids = [["****"] * grid_size for x in range(grid_size)]

    def refresh_grids():
        for x in range(grid_size):
            for y in range(grid_size):
                grids[x][y] = "****"

    scooter_index = 1
    for scooter_positions in all_scooter_positions:
        refresh_grids()
        print("")
        print("Scooter : " + str(scooter_index))
        print("")
        for timestamp in range(12):
            x, y = scooter_positions[timestamp]
            if grids[x][y] == '****':
                grids[x][y] = ""
            grids[x][y] += (" T-" + str(timestamp + 1))
        for grid in grids:
            print("---------------------------------------------------------------------")
            print("\t | \t".join(grid))
            print("---------------------------------------------------------------------")
        scooter_index += 1


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
                               row):
    # If unplaced police officers are more than remaining column, we can't proceed with this solution
    remaining_police = number_of_police_officers - len(placed_police_officers_coordinate)
    if remaining_police > (grid_size - row):
        return 1 - sys.maxsize

    max_points = 0
    for column in range(grid_size):
        if remaining_police > 0 and row < grid_size and is_position_safe(placed_police_officers_coordinate,
                                                                         (row, column)):
            # Search without placing a police here
            points = place_police_officers_util(grid_size, points_grid, placed_police_officers_coordinate,
                                                number_of_police_officers, row + 1)
            if points > max_points:
                max_points = points

            # Search by placing a police here
            placed_police_officers_coordinate.append((row, column))
            points = points_grid[row][column] + place_police_officers_util(grid_size, points_grid,
                                                                           placed_police_officers_coordinate,
                                                                           number_of_police_officers, row + 1)
            if points > max_points:
                max_points = points
            placed_police_officers_coordinate.pop()

    return max_points


def place_police_officers(grid_size, points_grid, number_of_police_officers):
    placed_police_officers_coordinate = []
    return place_police_officers_util(grid_size, points_grid, placed_police_officers_coordinate,
                                      number_of_police_officers, 0)


def write_result_to_output(result):
    output_file = open(OUTPUT_FILE_NAME, 'w')
    output_file.write(result)
    output_file.close()


def assert_output(max_points):
    print("Answer : ")
    # print(ANS)
    print("Actual output : " + str(max_points))
    f = open(OUTPUT_FILE_NAME, "r")
    expected_output = int(f.readline())
    print("Expected output : " + str(expected_output))
    assert max_points == expected_output
    f.close()


def run_homework():
    (grid_size, number_of_police_officers, all_scooter_positions) = get_input()
    # visualize_scooters(grid_size, all_scooter_positions)
    points_grid = construct_points_grid(grid_size, all_scooter_positions)
    visualize_grids(points_grid)
    max_points = place_police_officers(grid_size, points_grid, number_of_police_officers)
    assert_output(max_points)
    # write_result_to_output(max_points)


if __name__ == "__main__":
    run_homework()
