import pandas as pd
import os

def test_values_tcc():
    tcc_test_data_original = os.listdir("tcc_test_data_original/")
    for file in tcc_test_data_original:
        if file.endswith("output.csv"):
            print(file)
            df_original_output = pd.read_csv("tcc_test_data_original/" + file)

            df_original_output.drop("period", axis=1, inplace=True)

            df_original_output.rename(columns={
                "TCC_marker": "tcc_marker",
                "final_comp_1": "final_component_1",
                "final_comp_2": "final_component_2",
                "final_comp_3": "final_component_3",
                "final_comp_4": "final_component_4",
                }, inplace=True)

            # Move the "tcc_marker" column to the end
            tcc_marker_column = df_original_output.pop("tcc_marker")
            df_original_output.insert(len(df_original_output.columns), "tcc_marker", tcc_marker_column)

            # Write the modified DataFrame back to the CSV file
            df_original_output.to_csv("tcc_test_data_original/" + file, index=False)

test_values_tcc()
