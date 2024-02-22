import os

import pandas as pd


def update_csv():
    test_data_original = os.listdir("tpc_test_data_original/")
    for file in test_data_original:
        if file.endswith("output.csv"):
            print(file)
            df_original_output = pd.read_csv("tpc_test_data_original/" + file)

            df_original_output.drop("period", axis=1, inplace=True)

            df_original_output.rename(
                columns={
                    "final_principal": "principal_final_value",
                    "final_q42": "q42_final_value",
                    "final_q43": "q43_final_value",
                },
                inplace=True,
            )

            # Rearrange the columns in the DataFrame
            column_order = [
                "RU",
                "principal_val",
                "q42",
                "q43",
                "threshold_upper",
                "threshold_lower",
                "predictive_val",
                "aux_val",
                "principal_final_value",
                "tpc_ratio",
                "q42_final_value",
                "q43_final_value",
                "tpc_marker",
                # Add other column names here in the desired order
            ]
            df_original_output = df_original_output.reindex(columns=column_order)

            # Write the modified DataFrame back to the CSV file
            df_original_output.to_csv("tpc_test_data_original/" + file, index=False)


update_csv()
