import numpy as np

INPUT_FILE_NAME = "io/input1.txt"
OUTPUT_FILE_NAME = "io/output1.txt"


class DIRECTION:
    NORTH = 1
    EAST = 2
    WEST = 3
    SOUTH = 4
    TURN_LEFT = {NORTH: WEST, EAST: NORTH, WEST: SOUTH, SOUTH: EAST}
    TURN_RIGHT = {NORTH: EAST, EAST: SOUTH, WEST: NORTH, SOUTH: WEST}
    ABOVE_TURN = {NORTH: SOUTH, EAST: WEST, WEST: EAST, SOUTH: NORTH}
    MOVE = {NORTH: lambda (x, y), n: (x - 1, y) if x > 0 else (x, y),
            EAST: lambda (x, y), n: (x, y + 1) if y < n - 1 else (x, y),
            WEST: lambda (x, y), n: (x, y - 1) if y > 0 else (x, y),
            SOUTH: lambda (x, y), n: (x + 1, y) if x < n - 1 else (x, y)}


class Simulator:

    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.MAX_SEARCH_SIZE = 1000000
        self.swerves = self._generate_swerves()
        self.trial_count = 10

    def _generate_swerves(self):
        def _generate_swerves_util(seed):
            np.random.seed(seed)
            return np.random.random_sample(self.MAX_SEARCH_SIZE)

        return [_generate_swerves_util(x) for x in range(10)]

    def simulate(self, start_position, end_position, policy, reward):
        total_car_reward = 0
        for trial in range(self.trial_count):
            swerve = self.swerves[trial]
            current_position = start_position
            this_trial_car_reward = 0
            k = 0
            while current_position != end_position:
                move = policy[current_position[0]][current_position[1]]
                if swerve[k] > 0.7:
                    if swerve[k] > 0.8:
                        if swerve[k] > 0.9:
                            move = DIRECTION.ABOVE_TURN[move]
                        else:
                            move = DIRECTION.TURN_LEFT[move]
                    else:
                        move = DIRECTION.TURN_RIGHT[move]
                current_position = DIRECTION.MOVE[move](current_position, self.grid_size)
                this_trial_car_reward += reward[current_position[0]][current_position[1]]
                k += 1
            total_car_reward += this_trial_car_reward
        return int(np.floor(total_car_reward / self.trial_count))


class PolicyGenerator:
    def __init__(self, grid_size):
        self.gamma = 0.9
        self.epsilon = 0.1
        self.grid_size = grid_size

    def _is_policy_unchanged(self, old_policy, new_policy):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if old_policy[row][col] != new_policy[row][col]:
                    return False
        return True

    def _get_initial_policy(self):
        return [[1] * self.grid_size for _ in range(self.grid_size)]

    def _get_initial_utility(self):
        return [[0] * self.grid_size for _ in range(self.grid_size)]

    def _is_converged(self, old_utility, new_utility):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if abs(old_utility[row][col] - new_utility[row][col]) > self.epsilon:
                    return False
        return True

    # def _probability_summation_2(self, rewards, old_utility, curr_pos, move):
    #     (x, y) = DIRECTION.MOVE[move](curr_pos, self.grid_size)
    #     v1 = (0.7 * ((self.gamma * old_utility[x][y]) + rewards[x][y]))
    #
    #     (x, y) = DIRECTION.MOVE[DIRECTION.TURN_LEFT[move]](curr_pos, self.grid_size)
    #     v2 = (0.1 * ((self.gamma * old_utility[x][y]) + rewards[x][y]))
    #
    #     (x, y) = DIRECTION.MOVE[DIRECTION.TURN_RIGHT[move]](curr_pos, self.grid_size)
    #     v3 = (0.1 * ((self.gamma * old_utility[x][y]) + rewards[x][y]))
    #
    #     (x, y) = DIRECTION.MOVE[DIRECTION.ABOVE_TURN[move]](curr_pos, self.grid_size)
    #     v4 = (0.1 * ((self.gamma * old_utility[x][y]) + rewards[x][y]))
    #
    #     return (v1 + v2 + v3 + v4), move

    def _probability_summation(self, old_utility, curr_pos, move):
        (x, y) = DIRECTION.MOVE[move](curr_pos, self.grid_size)
        v1 = (0.7 * old_utility[x][y])

        (x, y) = DIRECTION.MOVE[DIRECTION.TURN_LEFT[move]](curr_pos, self.grid_size)
        v2 = (0.1 * old_utility[x][y])

        (x, y) = DIRECTION.MOVE[DIRECTION.TURN_RIGHT[move]](curr_pos, self.grid_size)
        v3 = (0.1 * old_utility[x][y])

        (x, y) = DIRECTION.MOVE[DIRECTION.ABOVE_TURN[move]](curr_pos, self.grid_size)
        v4 = (0.1 * old_utility[x][y])

        return (v1 + v2 + v3 + v4), move

    def _generate_new_policy_and_utility(self, rewards, utility, end_position):
        policy = self._get_initial_policy()
        new_utility = [x[:] for x in utility]
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if (row, col) != end_position:
                    north_val = self._probability_summation(new_utility, (row, col), DIRECTION.NORTH)
                    south_val = self._probability_summation(new_utility, (row, col), DIRECTION.SOUTH)
                    east_val = self._probability_summation(new_utility, (row, col), DIRECTION.EAST)
                    west_val = self._probability_summation(new_utility, (row, col), DIRECTION.WEST)
                    max_util, policy[row][col] = max([north_val, south_val, west_val, east_val], key=lambda y: y[0])
                    new_utility[row][col] = rewards[row][col] + (self.gamma * max_util)
                else:
                    new_utility[row][col] = 99

        return policy, new_utility

    def generate_via_value_iteration_method(self, rewards, end_position):
        old_utility = self._get_initial_utility()
        while True:
            policy, new_utility = self._generate_new_policy_and_utility(rewards, old_utility, end_position)
            # print new_utility
            # print_policy(policy)
            if self._is_converged(old_utility, new_utility):
                break
            old_utility = new_utility
        return policy

    def generate_via_policy_method(self, rewards, end_position):
        old_policy = self._get_initial_policy()
        old_utility = self._get_initial_utility()
        while True:
            new_utility = self._generate_utility_for_given_policy(rewards, old_policy, old_utility, end_position)
            new_policy = self._generate_new_policy(new_utility)
            # print new_utility
            # print_policy(new_policy)
            if self._is_policy_unchanged(old_policy, new_policy):
                break
            old_policy = new_policy
            old_utility = new_utility

        return old_policy

    def _generate_utility_for_given_policy(self, rewards, policy, old_utility, end_position):
        k = 0
        while True:
            new_utility = self._generate_new_utility(rewards, policy, old_utility, end_position)
            if self._is_converged(old_utility, new_utility) or k > 20:
                break
            old_utility = new_utility
            k += 1
        return old_utility

    def _generate_new_utility(self, rewards, policy, old_utility, end_position):
        new_utility = [x[:] for x in old_utility]
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if (row, col) != end_position:
                    max_util, _ = self._probability_summation(new_utility, (row, col), policy[row][col])
                    new_utility[row][col] = rewards[row][col] + (self.gamma * max_util)
                else:
                    new_utility[row][col] = 99

        return new_utility

    def _generate_new_policy(self, utility):
        new_policy = np.ones((self.grid_size, self.grid_size), dtype=np.int8)
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                north_val = self._probability_summation(utility, (row, col), DIRECTION.NORTH)
                south_val = self._probability_summation(utility, (row, col), DIRECTION.SOUTH)
                east_val = self._probability_summation(utility, (row, col), DIRECTION.EAST)
                west_val = self._probability_summation(utility, (row, col), DIRECTION.WEST)
                new_policy[row, col] = max([north_val, south_val, east_val, west_val], key=lambda x: x[0])[1]

        return new_policy


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
        # assert ouput == expected_output
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


def print_policy(policy):
    m = {1: "^", 2: ">", 3: "<", 4: "V"}
    for row in policy:
        print(map(lambda x: m[x], row))


def run_homework():
    (grid_size, number_of_cars, number_of_obstacles, obstacles, car_start_locations,
     car_terminal_locations) = get_input()
    policy_generator = PolicyGenerator(grid_size)
    simulator = Simulator(grid_size)
    ans = []
    for car_index in range(number_of_cars):
        start_position = car_start_locations[car_index]
        end_position = car_terminal_locations[car_index]
        rewards = construct_reward_grid(grid_size, end_position, obstacles)
        policy = policy_generator.generate_via_policy_method(rewards, end_position)
        # policy = policy_generator.generate_via_value_iteration_method(rewards, end_position)
        money_collected = simulator.simulate(start_position, end_position, policy, rewards)
        ans.append(money_collected)

    assert_output(ans)
    # write_result_to_output(ans)


if __name__ == "__main__":
    run_homework()
