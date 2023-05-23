import random

import pytest

from sml_small.totals_and_components.totals_and_components import (Component_list, check_absolute_difference_threshold,
                                                                   check_percentage_difference_threshold,
                                                                   check_predictive_value,
                                                                   check_sum_components_predictive, check_zero_errors,
                                                                   correct_components, correct_total,
                                                                   determine_error_detection, error_correction,
                                                                   sum_components, totals_and_components,
                                                                   validate_input)


def test_validate_input():
    try:
        test_components: Component_list = []

        for _ in range(12):
            random_float = random.uniform(0, 12)
            component = Component_list(original_value=random_float, final_value=None)
            test_components.append(component)

        validate_input(identifier="A",
                       period="202312",
                       total=100.0,
                       components=test_components,
                       amend_total=True,
                       predictive=100.0,
                       predictive_period="202312",
                       auxiliary=None,
                       absolute_difference_threshold=20,
                       percentage_difference_threshold=0.1,
                       )

    except Exception as e:
        pytest.fail(f"Expected no exception, but got {type(e).__name__}: {str(e)}")


def test_check_predictive_value():
    try:
        check_predictive_value(predictive=100.0, auxiliary=None)

    except Exception as e:
        pytest.fail(f"Expected no exception, but got {type(e).__name__}: {str(e)}")


def test_check_zero_errors():
    try:
        test_components: Component_list = []

        for _ in range(12):
            random_float = random.uniform(0, 12)
            component = Component_list(original_value=random_float, final_value=None)
            test_components.append(component)

        components_sum = sum_components(test_components)

        check_zero_errors(predictive=100.0, components_sum=components_sum)

    except Exception as e:
        pytest.fail(f"Expected no exception, but got {type(e).__name__}: {str(e)}")


def test_check_sum_components_predictive():
    try:
        test_components: Component_list = []

        for _ in range(12):
            random_float = random.uniform(0, 12)
            component = Component_list(original_value=random_float, final_value=None)
            test_components.append(component)

        components_sum = sum_components(test_components)

        check_sum_components_predictive(predictive=components_sum, components_sum=components_sum)

    except Exception as e:
        pytest.fail(f"Expected no exception, but got {type(e).__name__}: {str(e)}")


def test_determine_error_detection():
    try:
        test_components: Component_list = []

        for _ in range(12):
            random_float = random.uniform(0, 12)
            component = Component_list(original_value=random_float, final_value=None)
            test_components.append(component)

        components_sum = sum_components(test_components)

        determine_error_detection(absolute_difference_threshold=0,
                                  percentage_difference_threshold=0.1,
                                  absolute_difference=10,
                                  components_sum=components_sum)

    except Exception as e:
        pytest.fail(f"Expected no exception, but got {type(e).__name__}: {str(e)}")


def test_check_absolute_difference_threshold():
    try:
        check_absolute_difference_threshold(absolute_difference_threshold=9,
                                            absolute_difference=10)

    except Exception as e:
        pytest.fail(f"Expected no exception, but got {type(e).__name__}: {str(e)}")


def test_check_percentage_difference_threshold():
    try:
        check_percentage_difference_threshold(percentage_difference_threshold=0.1,
                                              components_sum=100.0)

    except Exception as e:
        pytest.fail(f"Expected no exception, but got {type(e).__name__}: {str(e)}")


def test_error_correction():
    try:
        test_components: Component_list = []

        for _ in range(10):
            component = Component_list(original_value=10.0, final_value=None)
            test_components.append(component)

        error_correction(amend_total=True,
                         components_sum=100.0,
                         original_components=test_components,
                         predictive=82.0
                         )

    except Exception as e:
        pytest.fail(f"Expected no exception, but got {type(e).__name__}: {str(e)}")


def test_correct_total():
    try:
        test_components: Component_list = []

        for _ in range(10):
            component = Component_list(original_value=10.0, final_value=None)
            test_components.append(component)

        correct_total(components_sum=100.0,
                      original_components=test_components
                      )

    except Exception as e:
        pytest.fail(f"Expected no exception, but got {type(e).__name__}: {str(e)}")


def test_correct_components():
    try:
        test_components: Component_list = []

        for _ in range(10):
            component = Component_list(original_value=9.0, final_value=None)
            test_components.append(component)

        correct_components(components_sum=90.0,
                           original_components=test_components,
                           predictive=100.0
                           )

    except Exception as e:
        pytest.fail(f"Expected no exception, but got {type(e).__name__}: {str(e)}")


def test_totals_and_components(capfd):
    test_components: Component_list = []

    for _ in range(12):
        random_float = random.uniform(0, 12)
        component = Component_list(original_value=random_float, final_value=None)
        test_components.append(component)

    results = totals_and_components(identifier="A",
                                    period="202312",
                                    total=100.0,
                                    components=test_components,
                                    amend_total=True,
                                    predictive=100.0,
                                    predictive_period="202312",
                                    auxiliary=None,
                                    absolute_difference_threshold=20,
                                    percentage_difference_threshold=0.1,
                                    )
    print(results)

    # On test error capture the printed output and remove any leading or trailing whitespace
    # Run with pytest -s to get output even for passing tests
    captured = capfd.readouterr()
    printed_output = captured.out.strip()
    print(printed_output)

    assert results.tcc_marker == "T"
