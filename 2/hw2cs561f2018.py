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

    def can_accommodate(self, applicant):
        return self.is_compatible(applicant) and self.is_days_available(applicant.days_required)

    def filter_compatible_applicants(self, applicants):
        return [applicant for applicant in applicants if self.is_compatible(applicant)]

    def get_efficiency(self):
        return sum([self.number_of_resources - x for x in self.availability]) / (
                self.number_of_resources * NUMBER_OF_DAYS_IN_WEEK * 1.0)

    def __repr__(self):
        return "\n{\n Resources available : " + str(self.availability) + "\n Pre enrolled : " + str(
            self.pre_enrolled_applicants) + "\n Newly enrolled : " + str(
            self.new_applicants) + "\n Efficiency : " + str(self.get_efficiency()) + " \n } \n"


def get_input():
    f = open(INPUT_FILE_NAME, "r")
    number_of_beds = int(f.readline().strip())
    number_of_parking_lot = int(f.readline().strip())

    number_of_applicants_chosen_by_lahsa = int(f.readline().strip())
    lahsa_applicant_ids = [f.readline().strip() for _ in range(number_of_applicants_chosen_by_lahsa)]

    number_of_applicants_chose_by_spla = int(f.readline().strip())
    spla_applicants_ids = [f.readline().strip() for _ in range(number_of_applicants_chose_by_spla)]

    all_applicants = get_all_applicants(f)

    application_dictionary = dict([(x.id, x) for x in all_applicants])

    lahsa_applicants = [application_dictionary[x] for x in lahsa_applicant_ids]
    spla_applicants = [application_dictionary[x] for x in spla_applicants_ids]

    return number_of_beds, number_of_parking_lot, all_applicants, lahsa_applicants, spla_applicants


def get_all_applicants(f):
    next_line = f.readline().strip()
    if next_line.isdigit():
        total_applicants = int(next_line)
        all_applicants = [Applicant.parse_applicant(f.readline().strip()) for _ in range(total_applicants)]
    else:
        all_applicants = []
        for line in f:
            all_applicants.append(Applicant.parse_applicant(line.strip()))
    return all_applicants


def write_result_to_output(result):
    output_file = open(OUTPUT_FILE_NAME, 'w')
    output_file.write(str(result))
    output_file.close()


def assert_output(actual_output):
    print("Actual output : " + str(actual_output))
    f = open(OUTPUT_FILE_NAME, "r")
    expected_output = int(f.readline())
    print("Expected output : " + str(expected_output))
    assert actual_output == expected_output
    f.close()


def run_homework():
    (number_of_beds, number_of_parking_lot, all_applicants, lahsa_applicants, spla_applicants) = get_input()
    LAHSA = Housing(number_of_beds, lahsa_applicants,
                    lambda applicant: applicant.is_female and applicant.age >= 17 and not applicant.has_pet)
    SPLA = Housing(number_of_parking_lot, spla_applicants,
                   lambda applicant: applicant.has_car and applicant.has_driver_license and not
                   applicant.has_medical_condition)
    print(LAHSA)
    print(SPLA)
    print all_applicants
    pass


if __name__ == "__main__":
    run_homework()
