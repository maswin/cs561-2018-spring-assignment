import numpy as np

INPUT_FILE_NAME = "io/input0.txt"
OUTPUT_FILE_NAME = "io/output0.txt"


class DIRECTION:
    NORTH = 1
    EAST = 2
    WEST = 3
    SOUTH = 4
    TURN_LEFT = {NORTH: WEST, EAST: NORTH, WEST: SOUTH, SOUTH: EAST}
    TURN_RIGHT = {NORTH: EAST, EAST: SOUTH, WEST: NORTH, SOUTH: WEST}
    MOVE = {NORTH: lambda (x, y), n: (x - 1, y) if x > 0 else (x, y),
            EAST: lambda (x, y), n: (x, y + 1) if y < n - 1 else (x, y),
            WEST: lambda (x, y), n: (x, y - 1) if y > 0 else (x, y),
            SOUTH: lambda (x, y), n: (x + 1, y) if x < n - 1 else (x, y)}


class Simulator:

    def __init__(self):
        self.MAX_SEARCH_SIZE = 1000000
        self.swerves = self._generate_swerves()
        self.trial_count = 10

    def _generate_swerves(self):
        def _generate_swerves_util(seed):
            np.random.seed(seed)
            return np.random.random_sample(self.MAX_SEARCH_SIZE)

        return [_generate_swerves_util(x + 1) for x in range(10)]

    def simulate(self, grid_size, start_position, end_position, policy, reward):
        total_car_reward = 0
        for trial in range(self.trial_count):
            swerve = self.swerves[trial]
            current_position = start_position
            this_trial_car_reward = reward[current_position[0]][current_position[1]]
            k = 0
            while current_position != end_position:
                move = policy[current_position[0]][current_position[1]]
                if swerve[k] > 0.7:
                    if swerve[k] > 0.8:
                        if swerve[k] > 0.9:
                            move = DIRECTION.TURN_LEFT[DIRECTION.TURN_LEFT[move]]
                        else:
                            move = DIRECTION.TURN_LEFT[move]
                    else:
                        move = DIRECTION.TURN_RIGHT[move]
                current_position = DIRECTION.MOVE[move](current_position, grid_size)
                this_trial_car_reward += policy[current_position[0]][current_position[1]]
                k += 1
            total_car_reward += this_trial_car_reward
        return total_car_reward / self.trial_count


class PolicyGenerator:
    def __init__(self):
        self.gamma = 0.9

    def generate_policy(self, grid_size, rewards):

        return []


def write_result_to_output(result):
    result = "\n".join([str(x) for x in result])
    output_file = open(OUTPUT_FILE_NAME, 'w')
    output_file.write(result)
    output_file.close()


def assert_output(actual_output):
    f = open(OUTPUT_FILE_NAME, "r")
    for ouput in actual_output:
        ouput = str(ouput)
        print("Actual output : " + ouput)
        expected_output = f.readline().strip()
        print("Expected output : " + str(expected_output))
        assert ouput == expected_output
    f.close()


def get_input():
    def get_x_y(ff):
        positions = ff.readline().strip().split(",")
        return int(positions[0]), int(positions[1])

    f = open(INPUT_FILE_NAME, "r")
    grid_size = int(f.readline().strip())
    number_of_cars = int(f.readline().strip())
    number_of_obstacles = int(f.readline().strip())
    obstacles = [get_x_y(f) for _ in range(number_of_obstacles)]
    car_start_locations = [get_x_y(f) for _ in range(number_of_cars)]
    car_terminal_locations = [get_x_y(f) for _ in range(number_of_cars)]
    return grid_size, number_of_cars, number_of_obstacles, obstacles, car_start_locations, car_terminal_locations


def construct_reward_grid(grid_size, end_position, obstacles):
    reward = [[-1] * grid_size for _ in range(grid_size)]
    reward[end_position[0]][end_position[1]] += 100
    for obstacle in obstacles:
        reward[obstacle[0]][obstacle[1]] -= 100
    return reward


def run_homework():
    (grid_size, number_of_cars, number_of_obstacles, obstacles, car_start_locations,
     car_terminal_locations) = get_input()
    policy_generator = PolicyGenerator()
    simulator = Simulator()
    ans = []
    for car_index in range(number_of_cars):
        start_position = car_start_locations[car_index]
        end_position = car_terminal_locations[car_index]
        reward = construct_reward_grid(grid_size, end_position, obstacles)
        policy = policy_generator.generate_policy(grid_size, reward)
        money_collected = simulator.simulate(grid_size, start_position, end_position, policy, reward)
        ans.append(money_collected)

    assert_output(ans)
    # write_result_to_output(ans)


if __name__ == "__main__":
    run_homework()
