INPUT_FILE_NAME = "io/input.txt"
OUTPUT_FILE_NAME = "io/output.txt"


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
        return "{ id : " + str(self.id) + \
               "\n days_required : " + str(self.days_required) + " } \n"

    @staticmethod
    def parse_applicant(raw_applicant):
        raw_applicant = raw_applicant.strip()

        def is_yes(x):
            return x.lower() == 'y'

        def is_female(x):
            return x.lower() == 'f'

        return Applicant(raw_applicant[0:5],
                         is_female(raw_applicant[5:6]),
                         int(raw_applicant[6:9]),
                         is_yes(raw_applicant[9:10]),
                         is_yes(raw_applicant[10:11]),
                         is_yes(raw_applicant[11:12]),
                         is_yes(raw_applicant[12:13]),
                         raw_applicant[13:])


def get_input():
    f = open(INPUT_FILE_NAME, "r")
    number_of_beds = int(f.readline())
    number_of_parking_lot = int(f.readline())

    number_of_applicants_chosen_by_lahsa = int(f.readline())
    lahsa_applicant_ids = [f.readline().strip() for _ in range(number_of_applicants_chosen_by_lahsa)]

    number_of_applicants_chose_by_spla = int(f.readline())
    spla_applicants_ids = [f.readline().strip() for _ in range(number_of_applicants_chose_by_spla)]

    total_applicants = int(f.readline())
    all_applicants = [Applicant.parse_applicant(f.readline()) for _ in range(total_applicants)]

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
    expected_output = int(f.readline())
    print("Expected output : " + str(expected_output))
    assert actual_output == expected_output
    f.close()


def run_homework():
    (number_of_beds, number_of_parking_lot, all_applicants, lahsa_applicants, spla_applicants) = get_input()
    print spla_applicants
    pass


if __name__ == "__main__":
    run_homework()
