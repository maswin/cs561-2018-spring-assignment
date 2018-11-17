import bisect
from itertools import groupby
# 1 6 8
INPUT_FILE_NAME = "io/grading_case/input1.txt"
# INPUT_FILE_NAME = "/Users/aswin/Documents/ai_hw/test/input0440.txt"
OUTPUT_FILE_NAME = "io/grading_case/output1.txt"
NUMBER_OF_DAYS_IN_WEEK = 7


class Applicant:

    def __init__(self, id, is_female, age, has_pet, has_medical_condition, has_car, has_driver_license, days_required):
        self.key = days_required
        self.days_required = self.parse_days_required(days_required)
        self.has_driver_license = has_driver_license
        self.has_car = has_car
        self.has_medical_condition = has_medical_condition
        self.has_pet = has_pet
        self.age = age
        self.is_female = is_female
        self.id = id
        self.number_of_days = self._get_number_of_days()

    def __repr__(self):
        return "\n { id : " + str(self.id) + \
               "\n days_required : " + str(self.days_required) + " } \n"

    @staticmethod
    def parse_applicant(raw_applicant):
        raw_applicant = raw_applicant.strip()

        def is_yes(x):
            return x.lower() == 'y'

        def is_female(x):
            return x.lower() == 'f'

        return Applicant(int(raw_applicant[0:5]),
                         is_female(raw_applicant[5:6]),
                         int(raw_applicant[6:9]),
                         is_yes(raw_applicant[9:10]),
                         is_yes(raw_applicant[10:11]),
                         is_yes(raw_applicant[11:12]),
                         is_yes(raw_applicant[12:13]),
                         raw_applicant[13:])

    def get_key(self):
        return ''.join(['1' if x else '0' for x in self.days_required])

    @staticmethod
    def parse_days_required(x):
        return [True if val == '1' else False for val in x]

    def _get_number_of_days(self):
        return sum(self.days_required)


class Housing:

    def __init__(self, name, number_of_resources, pre_enrolled_applicants, unavailable_applicants, all_applicants,
                 is_compatible):
        self.name = name
        self.number_of_resources = number_of_resources
        self.availability = [self.number_of_resources] * NUMBER_OF_DAYS_IN_WEEK
        self._process_pre_enrolled_applicants(pre_enrolled_applicants)
        self.domain = self._get_domain(all_applicants, is_compatible, pre_enrolled_applicants, unavailable_applicants)
        self.clustered_domain = self._construct_clustered_domain()
        self.enrolled_applicants = []
        self.max = self.number_of_resources * NUMBER_OF_DAYS_IN_WEEK

    def _construct_clustered_domain(self):
        clustered_domain = []
        for k, g in groupby(self.domain, key=lambda x: x.key):
            clustered_domain.append(list(g))
        return clustered_domain

    def get_sorted_applicants_as_key(self):
        # Feature Toggle: Sorted applicants
        # app = sorted(self.enrolled_applicants)
        app = self.enrolled_applicants
        return ','.join([str(x) for x in app])

    def can_accommodate_all_remaining(self, available_applicant_ids):
        restricted_domain = [x for x in self.domain if x.id in available_applicant_ids]
        added = []
        failure = False
        for applicant in restricted_domain:
            if self.is_days_available(applicant):
                self.add_new_applicant(applicant)
                added.append(applicant)
            else:
                failure = True
        efficiency = self.get_efficiency()
        for applicant in added:
            self.remove_applicant(applicant)
        return efficiency if not failure else -1

    def _get_domain(self, all_applicants, is_compatible, pre_enrolled_applicants, unavailable_applicants):
        exclude_domain = set([x.id for x in pre_enrolled_applicants] + [x.id for x in unavailable_applicants])
        return sorted([x for x in all_applicants if is_compatible(x) and x.id not in exclude_domain],
                      key=lambda y: y.id)

    def _process_pre_enrolled_applicants(self, pre_enrolled_applicants):
        self.pre_enrolled_applicants = pre_enrolled_applicants
        for applicant in self.pre_enrolled_applicants:
            self.reserve_a_slot(applicant)

    def add_new_applicant(self, applicant):
        # Feature Toggle: Sorted applicants
        # self.enrolled_applicants.append(applicant.id)
        bisect.insort(self.enrolled_applicants, applicant.id)
        self.reserve_a_slot(applicant)

    def reserve_a_slot(self, applicant):
        for index, is_day_required in enumerate(applicant.days_required):
            if is_day_required:
                self.availability[index] -= 1

    def remove_applicant(self, applicant):
        # Feature Toggle: Sorted applicants
        # self.enrolled_applicants.pop()
        del self.enrolled_applicants[bisect.bisect(self.enrolled_applicants, applicant.id) - 1]
        for index, is_day_required in enumerate(applicant.days_required):
            if is_day_required:
                self.availability[index] += 1

    def is_days_available(self, applicant):
        for index, is_day_required in enumerate(applicant.days_required):
            if is_day_required:
                if self.availability[index] == 0:
                    return False
        return True

    def get_efficiency(self):
        return sum([self.number_of_resources - x for x in self.availability])

    def __repr__(self):
        return "\n{\n Name: " + self.name + "\nResources available : " + str(
            self.availability) + "\n Pre enrolled : " + str(
            self.pre_enrolled_applicants) + "\n Domain : " + str(
            self.domain) + "\n Efficiency : " + str(self.get_efficiency()) + " \n } \n"


class MinMax:
    def __init__(self, spla, lahsa):
        self.spla = spla
        self.lahsa = lahsa
        self.available_applicant_ids = self._get_available_domain_ids()
        self.cache = dict()

    def _get_available_domain_ids(self):
        return set([x.id for x in self.spla.domain] + [x.id for x in self.lahsa.domain])

    def check_cache(self):
        spla_key = self.spla.get_sorted_applicants_as_key()
        lasha_key = self.lahsa.get_sorted_applicants_as_key()
        if spla_key in self.cache:
            if lasha_key in self.cache[spla_key]:
                return self.cache[spla_key][lasha_key]
        return None

    def add_cache(self, move, spla_score, lasha_score):
        spla_key = self.spla.get_sorted_applicants_as_key()
        lasha_key = self.lahsa.get_sorted_applicants_as_key()
        if spla_key not in self.cache:
            self.cache[spla_key] = dict()
        self.cache[spla_key][lasha_key] = (move, spla_score, lasha_score)

    def pick_alone(self, housing, other_score):
        cache_val = self.check_cache()
        if cache_val:
            (_, spla_score, lasha_score) = cache_val
            if housing.name == 'spla':
                return spla_score
            else:
                return lasha_score

        best_score = -1
        score = housing.can_accommodate_all_remaining(self.available_applicant_ids)
        if score != -1:
            best_score = score
        else:
            for applicant_group in housing.clustered_domain:
                for applicant in applicant_group:
                    if applicant.id in self.available_applicant_ids and housing.is_days_available(applicant):
                        # Add to stack
                        housing.add_new_applicant(applicant)
                        self.available_applicant_ids.remove(applicant.id)

                        # Perform recursion
                        score = self.pick_alone(housing, other_score)
                        if score > best_score:
                            best_score = score

                        # Remove from stack
                        housing.remove_applicant(applicant)
                        self.available_applicant_ids.add(applicant.id)
                        break
                if best_score == housing.max:
                    break

        # Base case
        if best_score == -1:
            best_score = housing.get_efficiency()
        if housing.name == 'spla':
            self.add_cache(None, best_score, other_score)
        else:
            self.add_cache(None, other_score, best_score)
        return best_score

    def spla_picks(self, chance):
        cache_val = self.check_cache()
        if cache_val:
            return cache_val

        best_move = None
        best_spla_score = 0
        best_lasha_score = 0
        for applicant_group in self.spla.clustered_domain:
            for applicant in applicant_group:
                if applicant.id in self.available_applicant_ids and self.spla.is_days_available(applicant):
                    # Add to stack
                    self.spla.add_new_applicant(applicant)
                    self.available_applicant_ids.remove(applicant.id)

                    # Perform recursion
                    (move, spla_score, lasha_score) = self.lasha_picks(chance + 1)
                    if spla_score > best_spla_score:
                        best_spla_score = spla_score
                        best_lasha_score = lasha_score
                        best_move = applicant

                    # Remove from stack
                    self.spla.remove_applicant(applicant)
                    self.available_applicant_ids.add(applicant.id)
                    break
            if best_spla_score == self.spla.max:
                break

        # Base case
        if not best_move:
            best_spla_score = self.spla.get_efficiency()
            best_lasha_score = self.pick_alone(self.lahsa, best_spla_score)

        self.add_cache(best_move, best_spla_score, best_lasha_score)
        return best_move, best_spla_score, best_lasha_score

    def lasha_picks(self, chance):
        cache_val = self.check_cache()
        if cache_val:
            return cache_val

        best_move = None
        best_lasha_score = 0
        best_spla_score = 0
        for applicant_group in self.lahsa.clustered_domain:
            for applicant in applicant_group:
                if applicant.id in self.available_applicant_ids and self.lahsa.is_days_available(applicant):
                    # Add to stack
                    self.lahsa.add_new_applicant(applicant)
                    self.available_applicant_ids.remove(applicant.id)

                    # Perform recursion
                    (move, spla_score, lasha_score) = self.spla_picks(chance + 1)
                    if lasha_score > best_lasha_score:
                        best_lasha_score = lasha_score
                        best_spla_score = spla_score
                        best_move = applicant

                    # Remove from stack
                    self.lahsa.remove_applicant(applicant)
                    self.available_applicant_ids.add(applicant.id)
                    break
            if best_lasha_score == self.lahsa.max:
                break

        # Base case
        if not best_move:
            best_lasha_score = self.lahsa.get_efficiency()
            best_spla_score = self.pick_alone(self.spla, best_lasha_score)

        self.add_cache(best_move, best_spla_score, best_lasha_score)
        return best_move, best_spla_score, best_lasha_score

    def first_move(self):
        (first_move, spla_efficiency, lahsa_efficiency) = self.spla_picks(1)
        # print(str(spla_efficiency) + " / " + str(lahsa_efficiency))
        # print("Cache size : " + str(len(self.cache)))
        return first_move


def get_input():
    f = open(INPUT_FILE_NAME, "r")
    number_of_beds = int(f.readline().strip())
    number_of_parking_lot = int(f.readline().strip())

    number_of_applicants_chosen_by_lahsa = int(f.readline().strip())
    lahsa_applicant_ids = [int(f.readline().strip()) for _ in range(number_of_applicants_chosen_by_lahsa)]

    number_of_applicants_chose_by_spla = int(f.readline().strip())
    spla_applicants_ids = [int(f.readline().strip()) for _ in range(number_of_applicants_chose_by_spla)]

    total_applicants = int(f.readline().strip())
    all_applicants = [Applicant.parse_applicant(f.readline().strip()) for _ in range(total_applicants)]

    application_dictionary = dict([(x.id, x) for x in all_applicants])

    lahsa_applicants = [application_dictionary[x] for x in lahsa_applicant_ids]
    spla_applicants = [application_dictionary[x] for x in spla_applicants_ids]

    return number_of_beds, number_of_parking_lot, all_applicants, lahsa_applicants, spla_applicants


def write_result_to_output(result):
    result = str(result).zfill(5)
    output_file = open(OUTPUT_FILE_NAME, 'w')
    output_file.write(str(result))
    output_file.close()


def assert_output(actual_output):
    actual_output = str(actual_output).zfill(5)
    print("Actual output : " + str(actual_output))
    f = open(OUTPUT_FILE_NAME, "r")
    expected_output = f.readline().strip()
    print("Expected output : " + str(expected_output))
    # assert actual_output == expected_output
    f.close()


def run_homework():
    (number_of_beds, number_of_parking_lot, all_applicants, lahsa_applicants, spla_applicants) = get_input()
    lahsa = Housing("lasha", number_of_beds, lahsa_applicants, spla_applicants, all_applicants,
                    lambda applicant: applicant.is_female and applicant.age > 17 and not applicant.has_pet)
    spla = Housing("spla", number_of_parking_lot, spla_applicants, lahsa_applicants, all_applicants,
                   lambda applicant: applicant.has_car and applicant.has_driver_license and not
                   applicant.has_medical_condition)
    min_max = MinMax(spla, lahsa)
    first_applicant = min_max.first_move()
    # assert_output(first_applicant.id)
    write_result_to_output(first_applicant.id)


if __name__ == "__main__":
    run_homework()
