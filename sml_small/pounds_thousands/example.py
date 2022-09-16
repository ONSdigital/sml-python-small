from csv import DictReader

from pounds_thousands import Target_variable, run


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
    config_csv = """principle_identifier,principle_variable,predicted,auxiliary,upper_limit,lower_limit
100,50000000,60000,30000,1350,350"""

    linked_questions_csv = """identifier,value
101,500
102,1000
103,1500
104,
"""

    return invoke(config_csv, linked_questions_csv)


# Can be called directly with csvs already loaded into strings or by using the above invoke to load local csvs
# Example function to take a dataset and wrangle it into a suitable format to support running the method
# Substitutes missing values with the Python 'None'
# Does not have any explicit exception/error handling
def invoke(config_csv: str, linked_question_csv: str):

    # Format:  principle_identifier,principle_variable,predicted,auxiliary,upper_limit,lower_limit
    config_reader = DictReader(config_csv.splitlines())
    config = []
    for config_row in config_reader:
        print(f"Config row: {config_row}")
        config = config_row  # We assume we are dealing with only 1 principle variable

    # Format:  identifier, value
    linked_question_reader = DictReader(linked_question_csv.splitlines())
    linked_questions = []
    for linked_row in linked_question_reader:
        # print(f"Linked row: {linked_row}")
        linked_questions.append(Target_variable(identifier=linked_row["identifier"], value=None if not linked_row["value"] else float(linked_row["value"])))

    return run(
        principle_identifier=config["principle_identifier"],
        principle_variable=None if not config["principle_variable"] else float(config["principle_variable"]),
        predicted=None if not config["predicted"] else float(config["predicted"]),
        auxiliary=None if not config["auxiliary"] else float(config["auxiliary"]),
        upper_limit=float(config["upper_limit"]),
        lower_limit=float(config["lower_limit"]),
        target_variables=linked_questions,
    )


if __name__ == "__main__":

    print("\nTesting using local csv:")
    output = invoke_process_with_local_csv()
    print(f"Output: {output}")

    print("\nRunning using in-memory csv:")
    output = invoke_process_with_inmemory_csv_example()
    print(f"Output: {output}")

    print("\nRunning directly without using csv")
    output = run(
        principle_identifier="q100",
        principle_variable=50000000,
        predicted=60000,
        auxiliary=30000,
        upper_limit=1350,
        lower_limit=350,
        target_variables=[
            Target_variable(identifier="q101", value=500),
            Target_variable(identifier="q102", value=1000),
            Target_variable(identifier="q103", value=1500),
            Target_variable(identifier="q104", value=None),
        ],
    )
    print(f"Output: {output}")
