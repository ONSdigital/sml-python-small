
# dataclasses module provides a decorator and functions for automatically adding generated special methods
import dataclasses
# We'll be using json module to convert a subset of python objects into json string
import json
# Importing DictReader() class from the CSV module to map the information into a dictionary
from csv import DictReader
# Importing the thousand_pounds method from the thousand_pounds.py file
from thousand_pounds import thousand_pounds


# Load some local CSVs into memory and then run the pounds thousands method
def invoke_process_with_local_csv():
    # Load the CSVs into memory
    with open("../../../tests/editing/thousand_pounds/tests/config.csv") as file:
        config_csv = file.read()

    with open(
            "../../../tests/editing/thousand_pounds/tests/linked_questions.csv"
    ) as file:
        target_questions_csv = file.read()

    return invoke(config_csv, target_questions_csv)


# Use some CSVs strings already defined in memory and then run the pounds thousands method
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


# Can be called directly with CSVs already loaded into strings or by using the above invoke to load local CSVs
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
    linked_questions = {}
    for linked_row in linked_question_reader:
        print(f"Linked row: {linked_row}")
        if not linked_row["value"]:
            linked_questions[linked_row["identifier"]] = "nan"
        else:
            linked_questions[linked_row["identifier"]] = linked_row["value"]

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

# In this function we pass in the test data directly into the thousand_pounds function
# and write the output into a CSV file
def invoke_directly_writing_output_to_csv_example():
    output = thousand_pounds(
        unique_identifier="q100",
        principal_variable=50000000,
        predictive=60000,
        auxiliary=30000,
        upper_limit=1350,
        lower_limit=350,
        target_variables={"q101": 500, "q102": 1000, "q103": 1500, "q104": None},
    )
    print(f"\nOutput: {output}")
    print(f"\nOutput json: {json.dumps(dataclasses.asdict(output), indent=4)}")

    header = "unique_identifier,principal_original_value,principal_adjusted_value,tpc_ratio,tpc_marker,error_description"
    row = (
        f"{output.unique_identifier},{output.principal_final_value},"
        f"{output.tpc_ratio},{output.tpc_marker}"
    )

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

# In this function we have a in memory CSV data containing the config data and linked questions data in one
# We also write the output into a CSV file
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
        question_list = {key: v for key, v in config_row.items() if "q1" in key}
        linked_questions = {}
        for question in question_list:
            if not question_list[question]:
                linked_questions[question] = "nan"
            else:
                linked_questions[question] = question_list[question]
        config_row["target_variables"] = linked_questions
        configs.append(config_row)

    print(f"configs: {configs}")

    output_question_header = ""
    for question in question_list:
        output_question_header += f",{question}_original_value,{question}_final_value"
    output_header = f"unique_identifier,principal_original_value,principal_final_value,tpc_ratio,tpc_marker,error_description{output_question_header}"
    output_row = ""
    for config in configs:
        try:
            output = thousand_pounds(
                unique_identifier=config["unique_identifier"],
                principal_variable=config["principal_variable"],
                predictive=config["predictive"],
                auxiliary=config["auxiliary"],
                upper_limit=config["upper_limit"],
                lower_limit=config["lower_limit"],
                target_variables=config["target_variables"],
            )
            output_row += (
                f"{output.unique_identifier},{output.principal_final_value},"
                f"{output.tpc_ratio},{output.tpc_marker}"
            )
            for question in output.target_variables:
                output_row += f",{question.original_value},{question.final_value}"
            output_row += "\n"
        except Exception as error:
            output_row += f"\nerror in row {config['unique_identifier']}"
            output_row += f"\n {error}"

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
