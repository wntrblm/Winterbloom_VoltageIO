# Copyright (c) 2019 Alethea Flowers for Winterbloom
# Licensed under the MIT License

import math

import pytest

import winterbloom_voltageio


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        (-1, (0, 0)),
        (0, (0, 1)),
        (1, (1, 2)),
        (4, (4, 5)),
        (5, (5, 5)),

        (0.2, (0, 1)),
        (4.5, (4, 5)),
        (5.1, (5, 5)),
    ]
)
def test__take_nearest_pair_integral(target, expected):
    assert winterbloom_voltageio._take_nearest_pair(
        [0, 1, 2, 3, 4, 5],
        target
    ) == expected


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        (-6, (-5, -5)),
        (-5, (-5, -4)),
        (-1, (-1, 0)),
        (0, (0, 1)),
        (1, (1, 2)),
        (5, (5, 5)),
        (6, (5, 5)),

        (-0.2, (-1, 0)),
        (-4.5, (-5, -4)),
        (-5.1, (-5, -5)),
    ]
)
def test__take_nearest_pair_integral_bipolar(target, expected):
    assert winterbloom_voltageio._take_nearest_pair(
        [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5],
        target
    ) == expected


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        (-1, (0, 0)),
        (0, (0, 0.2)),
        (0.2, (0.2, 1.8)),
        (5.3, (5.3, 5.3)),
        (10, (5.3, 5.3)),

        (4.5, (4.1, 5.3)),
        (2.1, (1.8, 2.3)),
    ]
)
def test__take_nearest_pair_fractional(target, expected):
    assert winterbloom_voltageio._take_nearest_pair(
        [0, 0.2, 1.8, 2.3, 3.9, 4.1, 5.3],
        target
    ) == expected


class AnalogOut:
    def __init__(self):
        self.value = 0


@pytest.mark.parametrize(
    ("voltage", "value"),
    [
        (0, 0),
        (0.25, 16384),
        (0.5, 32768),
        (0.75, 49151),
        (1.0, 65535),
        (2.0, 65535),
    ]
)
def test_out_linear_calibration_normalized(voltage, value):
    analog_out = AnalogOut()
    voltage_out = winterbloom_voltageio.VoltageOut(analog_out)

    voltage_out.linear_calibration(0.0, 1.0)

    voltage_out.voltage = voltage
    assert analog_out.value == value


@pytest.mark.parametrize(
    ("voltage", "value"),
    [
        # 0%
        (0, 0),
        # 25%
        (0.825, 16384),
        # 50%
        (1.65, 32768),
        # 75%,
        (2.475, 49151),
        # 100%
        (3.3, 65535),
        (4.0, 65535),
    ]
)
def test_out_linear_calibration_real_range(voltage, value):
    analog_out = AnalogOut()
    voltage_out = winterbloom_voltageio.VoltageOut(analog_out)

    voltage_out.linear_calibration(0.0, 3.3)

    voltage_out.voltage = voltage
    assert analog_out.value == value


@pytest.mark.parametrize(
    ("voltage", "value"),
    [
        (-1.0, 0),
        (-0.5, 0),
        (-0.25, 16384),
        (0, 32768),
        (0.25, 49151),
        (0.5, 65535),
        (1.0, 65535),
    ]
)
def test_out_linear_calibration_bipolar(voltage, value):
    analog_out = AnalogOut()
    voltage_out = winterbloom_voltageio.VoltageOut(analog_out)

    voltage_out.linear_calibration(-0.5, 0.5)

    voltage_out.voltage = voltage
    assert analog_out.value == value


@pytest.mark.parametrize(
    ("voltage", "value"),
    [
        (0, 0),
        (0.5, 16384),
        (1.0, 32768),
        (5.5, 49152),
        (10, 65535),
        (11, 65535),
    ]
)
def test_out_direct_calibration(voltage, value):
    analog_out = AnalogOut()
    voltage_out = winterbloom_voltageio.VoltageOut(analog_out)

    # Very non-linear. The first volt takes up half of the range.
    voltage_out.direct_calibration({
        0: 0,
        1.0: 32768,
        10: 65535,
    })

    voltage_out.voltage = voltage
    assert analog_out.value == value


class AnalogIn:
    def __init__(self):
        self.value = 0


@pytest.mark.parametrize(
    ("voltage", "value"),
    [
        (0, 0),
        (0.25, 16384),
        (0.5, 32768),
        (0.75, 49151),
        (1.0, 65535),
    ]
)
def test_in_linear_calibration_normalized(voltage, value):
    analog_in = AnalogIn()
    voltage_in = winterbloom_voltageio.VoltageIn(analog_in)

    voltage_in.linear_calibration(0.0, 1.0)

    analog_in.value = value
    assert math.isclose(voltage_in.voltage, voltage, rel_tol=1e-4)


@pytest.mark.parametrize(
    ("voltage", "value"),
    [
        # 0%
        (0, 0),
        # 25%
        (0.825, 16384),
        # 50%
        (1.65, 32768),
        # 75%,
        (2.475, 49151),
        # 100%
        (3.3, 65535),
    ]
)
def test_in_linear_calibration_real_range(voltage, value):
    analog_in = AnalogIn()
    voltage_in = winterbloom_voltageio.VoltageIn(analog_in)

    voltage_in.linear_calibration(0.0, 3.3)

    analog_in.value = value
    assert math.isclose(voltage_in.voltage, voltage, rel_tol=1e-4)


@pytest.mark.parametrize(
    ("voltage", "value"),
    [
        (0, 0),
        (0.5, 16384),
        (1.0, 32768),
        (5.5, 49152),
        (10, 65535),
    ]
)
def test_in_direct_calibration(voltage, value):
    analog_in = AnalogIn()
    voltage_in = winterbloom_voltageio.VoltageIn(analog_in)

    # Very non-linear. The first volt takes up half of the range.
    voltage_in.direct_calibration({
        0: 0,
        32768: 1.0,
        65535: 10,
    })

    analog_in.value = value
    assert math.isclose(voltage_in.voltage, voltage, rel_tol=1e-4)
