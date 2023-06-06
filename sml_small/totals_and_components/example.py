# In this python file, we are calling the T&C method and passing in the
# test data to be processed by the T&C method and return the result

from totals_and_components import totals_and_components, Component_list
from tabulate import tabulate
import os

test_data = [
    # ["A",
    # "202301",
    # 1625,
    # [Component_list(632, None), Component_list(732, None), Component_list(99, None), Component_list(162, None)],
    # True,
    # 1625,
    # "202301",
    # None,
    # 11,
    # None],
    
    ["B",
    "202301",
    10811,
    [Component_list(9201, None), Component_list(866, None), Component_list(632, None), Component_list(112, None)],
    True,
    10817,
    "202301",
    None,
    11,
    None]
]

def invoke_process():
    for data in test_data:
        # print("Test_data", *data)
        result = totals_and_components(*data)
        format_result(result, data)

def format_result(result, original_data):
    new_result = [
        result.identifier,
        result.period,
        result.absolute_difference,
        result.low_percent_threshold,
        result.high_percent_threshold,
        result.final_total,
        result.tcc_marker,
        ]
    new_result_comp = []
    for component in result.final_components:
            new_result_comp.append(component.original_value)    
    
    # original_data_comp = original_data[3].copy()
    print(original_data)
    original_data_comp = original_data[3]
    original_data.pop(3)
    print("O", original_data_comp)

    new_original_result_comp = []
    for component in original_data_comp:
            new_original_result_comp.append(component.original_value)  

    # print("N", new_result_comp)
    # print(f"Original data: {original_data}")
    # print(f"Processed result: {new_result}")
    # print(tabulate(new_result, 
    #                headers=[
    #                    "Identifier",
    #                    "Period",
    #                    "Absolute Difference",
    #                    "Low Percent Threshold",
    #                    "High Percent Threshold"
    #                    "Final Total",
    #                    "Final Components",
    #                    "Original Value",
    #                    "Final Value",
    #                    "TCC Marker"]
    #                 )
    #     )

    # new_original_data = [original_data[0], original_data[1], original_data[2], original_data[0], original_data[0]]
    # table_1 = [original_data]
    # print(tabulate(table_1, 
    #                 headers=[
    #                         "Identifier",
    #                         "Period",
    #                         "Absolute Difference",
    #                         "Low Percent Threshold",
    #                         "High Percent Threshold",
    #                         "Final Total",
    #                         "TCC Marker"
    #                         ]
    #                     )
    #         )

    os.system("clear")

    table_1 = [original_data]
    print("Original Input: ")
    print("====================")
    # print(f"Original data: {original_data}")
    print(tabulate(table_1, 
                   headers=[
                        "Identifier",
                        "Period",
                        "Total",
                        "Amend Total",
                        "Predictive",
                        "Predictive Period",
                        "Auxiliary Variable",
                        "Absolute Difference Threshold",
                        "Percentage Difference Threshold"
                        ]
                    )
        )






    table_2 = [new_result]
    print("\n")
    print("Final Results: ")
    print("==============")
    print(tabulate(table_2,
                   headers=[
                        "Identifier",
                        "Period",
                        "Absolute Difference",
                        "Low Percent Threshold",
                        "High Percent Threshold",
                        "Final Total",
                        "TCC Marker"
                        ]
                    )
        )
    
    print("\n")
    print("Original Input Components: ")
    print("==========================")
    table_3 = [new_original_result_comp]
    print(table_3)
    print(tabulate(table_3,
                    headers=[
                        "Final Comp 1",
                        "Final Comp 2",
                        "Final Comp 3",
                        "Final Comp 4"
                            ]
                        )
            )
    

    print("\n")
    print("Final Results Components: ")
    print("=========================")
    table_4 = [new_result_comp]
    print(tabulate(table_4, 
                   headers=[
                        "Final Comp 1",
                        "Final Comp 2",
                        "Final Comp 3",
                        "Final Comp 4"
                        ]
                    )
        )



invoke_process()
