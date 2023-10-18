import dataclasses
import json
from csv import DictReader

from thousand_pounds import Target_variable, thousand_pounds


# Load some local csvs into memory and then run the pounds thousands method
def invoke_process_with_local_csv():
    # Load the csvs into memory
    with open("tests/config.csv") as file:
        config_csv = file.read()

    with open("tests/linked_questions.csv") as file:
        target_questions_csv = file.read()

    return invoke(config_csv, target_questions_csv)


# Use some csvs strings already defined in memory and then run the pounds thousands method
def invoke_process_with_inmemory_csv_example():
    config_csv = """unique_identifier,principal_variable,predictive,auxiliary,upper_limit,lower_limit
100,50000000,60000,30000,1350,350"""

    target_questions_csv = """identifier,value
101,500
102,1000
103,1500
104,
"""

    return invoke(config_csv, target_questions_csv)


# Can be called directly with csvs already loaded into strings or by using the above invoke to load local csvs
# Example function to take a dataset and wrangle it into a suitable format to support running the method
# Substitutes missing values with the Python 'None'
# Does not have any explicit exception/error handling
def invoke(config_csv: str, linked_question_csv: str):
    # Format:  unique_identifier,principal_variable,predicted,auxiliary,upper_limit,lower_limit
    config_reader = DictReader(config_csv.splitlines())
    config = []
    for config_row in config_reader:
        print(f"Config row: {config_row}")
        config = config_row  # We assume we are dealing with only 1 principal variable

    # Format:  identifier, value
    linked_question_reader = DictReader(linked_question_csv.splitlines())
    linked_questions = []
    for linked_row in linked_question_reader:
        # print(f"Linked row: {linked_row}")
        linked_questions.append(
            Target_variable(
                identifier=linked_row["identifier"],
                original_value=None
                if not linked_row["value"]
                else float(linked_row["value"]),
            )
        )

    return thousand_pounds(
        unique_identifier=config["unique_identifier"],
        principal_variable=None
        if not config["principal_variable"]
        else float(config["principal_variable"]),
        predictive=None if not config["predictive"] else float(config["predictive"]),
        auxiliary=None if not config["auxiliary"] else float(config["auxiliary"]),
        upper_limit=float(config["upper_limit"]),
        lower_limit=float(config["lower_limit"]),
        target_variables=linked_questions,
    )


def invoke_directly_writing_output_to_csv_example():
    output = thousand_pounds(
        unique_identifier="q100",
        principal_variable=50000000,
        predictive=60000,
        auxiliary=30000,
        upper_limit=1350,
        lower_limit=350,
        target_variables=[
            Target_variable(identifier="q101", original_value=500),
            Target_variable(identifier="q102", original_value=1000),
            Target_variable(identifier="q103", original_value=1500),
            Target_variable(identifier="q104", original_value=None),
        ],
    )
    print(f"\nOutput: {output}")
    print(f"\nOutput json: {json.dumps(dataclasses.asdict(output),indent=4)}")

    header = "unique_identifier,principal_original_value,principal_adjusted_value,tpc_ratio,tpc_marker,error_description"
    row = f"{output.unique_identifier},{output.principal_original_value},{output.principal_final_value}," \
          f"{output.tpc_ratio},{output.tpc_marker},{output.error_description}"

    for linkedq in output.target_variables:
        header += (
            f",{linkedq.identifier}_original_value,{linkedq.identifier}_adjusted_value"
        )
        row += f",{linkedq.original_value},{linkedq.final_value}"

    print("\nOutput csv:")
    print(f"{header}")
    print(f"{row}")

    # now we will open a file for writing
    with open("output1.csv", "w") as file:
        file.write(header)
        file.write("\n")
        file.write(row)


def invoke_process_with_inmemory_single_csv_example():
    config_csv = """unique_identifier,principal_variable,predictive,auxiliary,upper_limit,lower_limit,q101,q102,q103,q104
123A-202203,50000000,60000,30000,1350,250,500,1000,1500,
123B-202203,50000000,60000,30000,1350,250,500,1000,1500,12345
124A-202204,50000,600,300,1350,250,200,5000,3500,300
125A-202204,0,0,12 0,1350,250,200,5000,3500,300
126A-202205,,,,1350,250,100,1000,1500,100
127A-202205,,1,2,1350,250,100,1000,1500,100
127B-202206,5000,10,2,1350,250,100,1000,abc,100
127C-202207,5000,10,2,13 50,250,100,1000,4,100
128A-202207,5000,10,2,1350,2 50,100,1000,2,100
128B-202208,5000,10,2,,250,100,1000,6,100
128C-202208,5000,10,2,100,,100,1000,7,100"""

    config_reader = DictReader(config_csv.splitlines())
    configs = []
    question_list = []
    for config_row in config_reader:
        question_list = {key: v for key, v in config_row.items() if "q" in key}
        linked_questions = []
        for question in question_list:
            linked_questions.append(
                Target_variable(
                    identifier=question, original_value=question_list[question]
                )
            )
        config_row["target_variables"] = linked_questions
        configs.append(config_row)

    print(f"configs: {configs}")

    output_question_header = ""
    for question in question_list:
        output_question_header += f",{question}_original_value,{question}_final_value"
    output_header = f"unique_identifier,principal_original_value,principal_final_value,tpc_ratio,tpc_marker,error_description{output_question_header}"
    output_row = ""
    for config in configs:
        output = thousand_pounds(
            unique_identifier=config["unique_identifier"],
            principal_variable=config["principal_variable"],
            predictive=config["predictive"],
            auxiliary=config["auxiliary"],
            upper_limit=config["upper_limit"],
            lower_limit=config["lower_limit"],
            target_variables=config["target_variables"],
        )

        output_row += f"{output.unique_identifier},{output.principal_original_value},{output.principal_final_value}," \
                      f"{output.tpc_ratio},{output.tpc_marker},{output.error_description}"
        for question in output.target_variables:
            output_row += f",{question.original_value},{question.final_value}"
        output_row += "\n"

    print("\nSingle_output csv:")
    print(f"{output_header}")
    print(f"{output_row}")

    # now we will open a file for writing
    with open("single_output.csv", "w") as file:
        file.write(output_header)
        file.write("\n")
        file.write(output_row)


if __name__ == "__main__":
    print("\nTesting using local csv:")
    output = invoke_process_with_local_csv()
    print(f"Output: {output}")

    print("\nRunning using in-memory csv:")
    output = invoke_process_with_inmemory_csv_example()
    print(f"Output: {output}")

    print("\nRunning directly without using csv")
    invoke_directly_writing_output_to_csv_example()

    print("\nRunning directly using single csv format")
    invoke_process_with_inmemory_single_csv_example()
