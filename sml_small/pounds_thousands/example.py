from csv import DictReader
from pounds_thousands import run, Response, Thousands_config
from pprint import pprint


# Load some local csvs into memory and then run the pounds thousands method
def invoke_process_with_local_csv():

    # Load the csvs into memory
    with open("tests/config.csv") as file:
        config_csv = file.read()

    with open("tests/linked_questions.csv") as file:
        linked_questions_csv = file.read()

    return invoke(config_csv, linked_questions_csv)


# Use some csvs strings already defined in memory and then run the pounds thousands method
def invoke_process_with_inmemory_csv_example():

    config_csv = """primary_question,current_value,previous_value,predicted,aux,threshold_upper,threshold_lower
100,50000000,60000,30000,15000,1350,350
200,60000000,,60000,15000,1350,350
300,70000000,,,70000,1350,350
400,80000000,,,5500,1350,350
500,,60000,30000,15000,1350,350
600,0,80000,50000,15100,1350,350
700,12345,,,,1350,250
,,,,,0,0"""

    linked_questions_csv = """primary_question,question,response
100,101,500
100,102,1000
100,103,1500
100,104,
500,510,6000
500,520,1200
600,650,1234
700,7a,456
700,7b,789"""

    return invoke(config_csv, linked_questions_csv)


# Can be called directly with csvs already loaded into strings or by using the above invoke to load local csvs
# Example function to take a dataset and wrangle it into a suitable format to support running the method
# Substitutes missing values with the Python 'None'
# Does not have any explicit exception/error handling
def invoke(config_csv: str, linked_question_csv: str):

    # Format:  primary_question, current_value, previous_value, predicted, aux, threshold_upper, threshold_lower
    config = []
    config_reader = DictReader(config_csv.splitlines())
    for config_row in config_reader:

        # print(f"Config row: {config_row}")

        # Format:  primary_question, question, response
        linked_questions = []
        linked_question_reader = DictReader(linked_question_csv.splitlines())
        for linked_row in linked_question_reader:
            # print(f"Linked row: {linked_row}")
            if linked_row["primary_question"] == config_row["primary_question"]:
                linked_questions.append(
                    Response(question=linked_row["question"], response=None if not linked_row["response"] else float(linked_row["response"]))
                )

        config.append(
            Thousands_config(
                primary_question=config_row["primary_question"],
                current_value=None if not config_row["current_value"] else float(config_row["current_value"]),
                previous_value=None if not config_row["previous_value"] else float(config_row["previous_value"]),
                predicted_value=None if not config_row["predicted"] else float(config_row["predicted"]),
                aux_value=None if not config_row["aux"] else float(config_row["aux"]),
                threshold_upper=float(config_row["threshold_upper"]),
                threshold_lower=float(config_row["threshold_lower"]),
                linked_questions=linked_questions,
            )
        )

    # print(config)
    return run(config)


if __name__ == "__main__":

    print("\nTesting using local csv:")
    output = invoke_process_with_local_csv()
    pprint(output)

    print("\nRunning using in-memory csv:")
    output = invoke_process_with_inmemory_csv_example()
    pprint(output)
