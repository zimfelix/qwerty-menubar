import pytest

from tools.measure_process import time_seconds


@pytest.mark.parametrize(
    "value, expected",
    [
        ("0:00.00", 0),
        ("0:01.25", 1.25),
        ("1:02.50", 62.5),
        ("01:02:03", 3723),
        ("2-01:02:03", 176523),
    ],
)
def test_cpu_time_parser(value, expected):
    assert time_seconds(value) == expected
