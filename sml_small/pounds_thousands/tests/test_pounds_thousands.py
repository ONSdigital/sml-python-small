from pounds_thousands import run, Response, Thousands_config, Thousands_output


def test__run__given_valid_config__returns_adjusted_figures():

    config = [
        Thousands_config(
            primary_question="100",
            current_value=50000000,
            previous_value=60000,
            predicted_value=30000,
            aux_value=15000,
            threshold_upper=1350,
            threshold_lower=250,
            linked_questions=[
                Response(question="101", response=500),
                Response(question="102", response=1000),
                Response(question="103", response=1500),
                Response(question="104", response=None),
            ],
        ),
        Thousands_config(
            primary_question="200",
            current_value=60000000,
            previous_value=None,
            predicted_value=60000,
            aux_value=15000,
            threshold_upper=1350,
            threshold_lower=250,
            linked_questions=[],
        ),
        Thousands_config(
            primary_question="300",
            current_value=70000000,
            previous_value=None,
            predicted_value=None,
            aux_value=70000,
            threshold_upper=1350,
            threshold_lower=250,
            linked_questions=[],
        ),
        Thousands_config(
            primary_question="400",
            current_value=80000000,
            previous_value=None,
            predicted_value=None,
            aux_value=55000,
            threshold_upper=1350,
            threshold_lower=250,
            linked_questions=[],
        ),
    ]

    expected_output = [
        Thousands_output(question="100", original_value=50000000, adjusted_value=50000.0, is_adjusted=True),
        Thousands_output(question="101", original_value=500, adjusted_value=0.5, is_adjusted=True),
        Thousands_output(question="102", original_value=1000, adjusted_value=1.0, is_adjusted=True),
        Thousands_output(question="103", original_value=1500, adjusted_value=1.5, is_adjusted=True),
        Thousands_output(question="104", original_value=None, adjusted_value=None, is_adjusted=True),
        Thousands_output(question="200", original_value=60000000, adjusted_value=60000.0, is_adjusted=True),
        Thousands_output(question="300", original_value=70000000, adjusted_value=70000.0, is_adjusted=True),
        Thousands_output(question="400", original_value=80000000, adjusted_value=80000000.0, is_adjusted=False),
    ]

    output = run(config)
    assert output == expected_output


def test__run__given_missing_current_value__returns_unadjusted_figures():

    config = [
        Thousands_config(
            primary_question="100",
            current_value=None,
            previous_value=60000,
            predicted_value=30000,
            aux_value=15000,
            threshold_upper=1350,
            threshold_lower=250,
            linked_questions=[
                Response(question="101", response=500),
                Response(question="102", response=1000),
            ],
        ),
        Thousands_config(
            primary_question="200",
            current_value=0,
            previous_value=80000,
            predicted_value=60000,
            aux_value=15000,
            threshold_upper=1350,
            threshold_lower=250,
            linked_questions=[],
        ),
    ]

    expected_output = [
        Thousands_output(question="100", original_value=None, adjusted_value=None, is_adjusted=None),
        Thousands_output(question="101", original_value=500, adjusted_value=500.0, is_adjusted=None),
        Thousands_output(question="102", original_value=1000, adjusted_value=1000.0, is_adjusted=None),
        Thousands_output(question="200", original_value=0, adjusted_value=0, is_adjusted=False),
    ]

    output = run(config)
    assert output == expected_output


def test__run__given_missing_previous_values__returns_unadjusted_figures():

    config = [
        Thousands_config(
            primary_question="100",
            current_value=123456,
            previous_value=None,
            predicted_value=None,
            aux_value=None,
            threshold_upper=1350,
            threshold_lower=250,
            linked_questions=[
                Response(question="101", response=500),
                Response(question="102", response=1000),
            ],
        )
    ]

    expected_output = [
        Thousands_output(question="100", original_value=123456, adjusted_value=123456, is_adjusted=None),
        Thousands_output(question="101", original_value=500, adjusted_value=500.0, is_adjusted=None),
        Thousands_output(question="102", original_value=1000, adjusted_value=1000.0, is_adjusted=None),
    ]

    output = run(config)
    assert output == expected_output


def test__run__given_empty_config__returns_unadjusted_figures():

    config = [
        Thousands_config(
            primary_question="",
            current_value=None,
            previous_value=None,
            predicted_value=None,
            aux_value=None,
            threshold_upper=0,
            threshold_lower=0,
            linked_questions=[],
        )
    ]

    expected_output = [Thousands_output(question="", original_value=None, adjusted_value=None, is_adjusted=None)]

    output = run(config)
    assert output == expected_output
