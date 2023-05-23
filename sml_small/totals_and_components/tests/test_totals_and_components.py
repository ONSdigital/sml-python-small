import random

import pytest  # noqa

from sml_small.totals_and_components.totals_and_components import Component_list, totals_and_components


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
