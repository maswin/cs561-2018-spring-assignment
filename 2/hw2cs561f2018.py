INPUT_FILE_NAME = "io/input.txt"
OUTPUT_FILE_NAME = "io/output.txt"
NUMBER_OF_DAYS_IN_WEEK = 7


class Applicant:

    def __init__(self, id, is_female, age, has_pet, has_medical_condition, has_car, has_driver_license, days_required):
        self.days_required = days_required
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

        def parse_days_required(x):
            return [True if val == '1' else False for val in x]

        return Applicant(raw_applicant[0:5],
                         is_female(raw_applicant[5:6]),
                         int(raw_applicant[6:9]),
                         is_yes(raw_applicant[9:10]),
                         is_yes(raw_applicant[10:11]),
                         is_yes(raw_applicant[11:12]),
                         is_yes(raw_applicant[12:13]),
                         parse_days_required(raw_applicant[13:]))

    def _get_number_of_days(self):
        return sum(self.days_required)


class Housing:

    def __init__(self, number_of_resources, pre_enrolled_applicants, is_compatible):
        self.number_of_resources = number_of_resources
        self.availability = [self.number_of_resources] * NUMBER_OF_DAYS_IN_WEEK
        self.pre_enrolled_applicants = []
        self.new_applicants = []
        self._process_pre_enrolled_applicants(pre_enrolled_applicants)
        self.is_compatible = is_compatible

    def _process_pre_enrolled_applicants(self, pre_enrolled_applicants):
        self.pre_enrolled_applicants = pre_enrolled_applicants
        for applicant in self.pre_enrolled_applicants:
            self.reserve_a_slot(applicant.days_required)

    def add_new_applicant(self, applicant):
        self.new_applicants.append(applicant)
        self.reserve_a_slot(applicant.days_required)

    def remove_last_applicant(self):
        applicant = self.new_applicants.pop()
        self.free_a_slot(applicant.days_required)

    def reserve_a_slot(self, days_required):
        for index, is_day_required in enumerate(days_required):
            if is_day_required:
                self.availability[index] -= 1

    def free_a_slot(self, days_booked):
        for index, is_day_required in enumerate(days_booked):
            if is_day_required:
                self.availability[index] += 1

    def is_days_available(self, days_required):
        for index, is_day_required in enumerate(days_required):
            if is_day_required:
                if self.availability[index] < 0:
                    return False
        return True

    def is_applicant_compatible(self, applicant):
        return self.is_compatible(applicant)

    def get_efficiency(self):
        return sum([self.number_of_resources - x for x in self.availability])

    def __repr__(self):
        return "\n{\n Resources available : " + str(self.availability) + "\n Pre enrolled : " + str(
            self.pre_enrolled_applicants) + "\n Newly enrolled : " + str(
            self.new_applicants) + "\n Efficiency : " + str(self.get_efficiency()) + " \n } \n"


class MinMax:
    def __init__(self, spla, lahsa, domain):
        self.domain = domain
        self.spla = spla
        self.lahsa = lahsa
        self.spla_domain, self.lahsa_domain = self.filter_available_compatible_applicants()
        self.available_applicant_ids = self._get_available_domain_ids()

    def filter_available_compatible_applicants(self):
        spla_existing = set([applicant.id for applicant in self.spla.pre_enrolled_applicants])
        lahsa_existing = set([applicant.id for applicant in self.lahsa.pre_enrolled_applicants])
        spla_domain = [applicant for applicant in self.domain if
                       self.spla.is_compatible(applicant) and (applicant.id not in spla_existing) and (
                               applicant.id not in lahsa_existing)]
        lahsa_domain = [applicant for applicant in self.domain if
                        self.lahsa.is_compatible(applicant) and (applicant.id not in spla_existing) and (
                                applicant.id not in lahsa_existing)]
        # print("SPLA Domain " + str(spla_domain))
        # print("LAHSA Domain " + str(lahsa_domain))
        return spla_domain, lahsa_domain

    def pick_alone(self, housing, domain):
        best_score = -1
        for applicant in domain:
            if applicant.id in self.available_applicant_ids and housing.is_days_available(applicant.days_required):
                # Add to stack
                housing.add_new_applicant(applicant)
                self.available_applicant_ids.remove(applicant.id)

                # Perform recursion
                score = self.pick_alone(housing, domain)
                if score > best_score:
                    best_score = score

                # Remove from stack
                housing.remove_last_applicant()
                self.available_applicant_ids.add(applicant.id)

        # Base case
        if best_score == -1:
            return housing.get_efficiency()
        return best_score

    def spla_picks(self):
        best_move = None
        best_spla_score = 0
        best_lahsa_score = 0
        for applicant in self.spla_domain:
            if applicant.id in self.available_applicant_ids and self.spla.is_days_available(applicant.days_required):
                # Add to stack
                self.spla.add_new_applicant(applicant)
                self.available_applicant_ids.remove(applicant.id)

                # Perform recursion
                (move, spla_score, lahsa_score) = self.lasha_picks()
                if spla_score > best_spla_score:
                    best_spla_score = spla_score
                    best_lahsa_score = lahsa_score
                    best_move = applicant

                # Remove from stack
                self.spla.remove_last_applicant()
                self.available_applicant_ids.add(applicant.id)

        # Base case
        if not best_move:
            best_spla_score = self.spla.get_efficiency()
            best_lahsa_score = self.pick_alone(self.lahsa, self.lahsa_domain)

        return best_move, best_spla_score, best_lahsa_score

    def lasha_picks(self):
        best_move = None
        best_spla_score = 0
        best_lahsa_score = 0
        for applicant in self.lahsa_domain:
            if applicant.id in self.available_applicant_ids and self.spla.is_days_available(applicant.days_required):
                # Add to stack
                self.lahsa.add_new_applicant(applicant)
                self.available_applicant_ids.remove(applicant.id)

                # Perform recursion
                (move, spla_score, lahsa_score) = self.spla_picks()
                if lahsa_score > best_lahsa_score:
                    best_spla_score = spla_score
                    best_lahsa_score = lahsa_score
                    best_move = applicant

                # Remove from stack
                self.lahsa.remove_last_applicant()
                self.available_applicant_ids.add(applicant.id)

        # Base case
        if not best_move:
            best_spla_score = self.pick_alone(self.spla, self.spla_domain)
            best_lahsa_score = self.lahsa.get_efficiency()

        return best_move, best_spla_score, best_lahsa_score

    def first_move(self):
        (first_move, spla_efficiency, lahsa_efficiency) = self.spla_picks()
        return first_move

    def _get_available_domain_ids(self):
        return set([x.id for x in self.spla_domain] + [x.id for x in self.lahsa_domain])


def get_input():
    f = open(INPUT_FILE_NAME, "r")
    number_of_beds = int(f.readline().strip())
    number_of_parking_lot = int(f.readline().strip())

    number_of_applicants_chosen_by_lahsa = int(f.readline().strip())
    lahsa_applicant_ids = [f.readline().strip() for _ in range(number_of_applicants_chosen_by_lahsa)]

    number_of_applicants_chose_by_spla = int(f.readline().strip())
    spla_applicants_ids = [f.readline().strip() for _ in range(number_of_applicants_chose_by_spla)]

    total_applicants = int(f.readline().strip())
    all_applicants = [Applicant.parse_applicant(f.readline().strip()) for _ in range(total_applicants)]

    application_dictionary = dict([(x.id, x) for x in all_applicants])

    lahsa_applicants = [application_dictionary[x] for x in lahsa_applicant_ids]
    spla_applicants = [application_dictionary[x] for x in spla_applicants_ids]

    return number_of_beds, number_of_parking_lot, all_applicants, lahsa_applicants, spla_applicants


def write_result_to_output(result):
    output_file = open(OUTPUT_FILE_NAME, 'w')
    output_file.write(str(result))
    output_file.close()


def assert_output(actual_output):
    print("Actual output : " + str(actual_output))
    f = open(OUTPUT_FILE_NAME, "r")
    expected_output = f.readline()
    print("Expected output : " + str(expected_output))
    assert actual_output == expected_output
    f.close()


def run_homework():
    (number_of_beds, number_of_parking_lot, all_applicants, lahsa_applicants, spla_applicants) = get_input()
    lahsa = Housing(number_of_beds, lahsa_applicants,
                    lambda applicant: applicant.is_female and applicant.age >= 17 and not applicant.has_pet)
    spla = Housing(number_of_parking_lot, spla_applicants,
                   lambda applicant: applicant.has_car and applicant.has_driver_license and not
                   applicant.has_medical_condition)
    min_max = MinMax(spla, lahsa, all_applicants)
    first_applicant = min_max.first_move()
    assert_output(first_applicant.id)
    # write_result_to_output(first_applicant.id)


if __name__ == "__main__":
    run_homework()
