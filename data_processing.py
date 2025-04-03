from dataclasses import dataclass
from data_structures import *


LOW_EXTRAPOLATION_FORMULA = lambda x: 95220 + -20661 * x + 1269 * (x**2)

RESISTANCES = [
    3.5,
    4.2,
    5.1,
    6,
    7,
    8,
    9,
    10,
    11,
    13,
    15.5,
    19,
    20,
    30,
    40,
    50,
    60,
    70,
    80,
    90,
    100,
    200,
    300,
    400,
    500,
    600,
    700,
]

FORCE = [
    40000,
    30000,
    20000,
    18000,
    14000,
    12000,
    11000,
    10000,
    9000,
    8000,
    7000,
    6000,
    5500,
    4500,
    4000,
    3500,
    3300,
    3200,
    3100,
    3000,
    2900,
    2100,
    1900,
    1800,
    1700,
    1600,
    1500,
]

SCALE = 100  # Pixels to CM

PRESSURE_LOCATIONS = [
    (197, 211),
    (561, 326),
    (120, 705),
    (473, 760),
    (769, 860),
    (670, 1379),
    (253, 2185),
    (552, 2185),
]

FOOT_DIM = (900, 2350)


def get_center_of_pressure(forces: list[float]) -> tuple[float, float]:

    sum_forces = sum(forces)
    sum_x = 0
    sum_y = 0
    included_count = 0
    for i, (force, (loc_x, loc_y)) in enumerate(zip(forces, PRESSURE_LOCATIONS)):
        if force < 1:
            continue
        included_count += 1
        rel_x = loc_x - FOOT_DIM[0] / 2
        rel_y = loc_y - FOOT_DIM[1] / 2
        sum_x += force * (rel_x / 100)
        sum_y += force * (rel_y / 100)
    if included_count == 0:
        return (0, 0)
    cx = sum_x / sum_forces
    cy = sum_y / sum_forces
    return (cx, cy)


def linear_interpolate(resistance: float) -> float:
    detected = None
    for i, res in enumerate(RESISTANCES):
        res = res * 1000
        if res > resistance:
            detected = i
            break
    if detected == 0:
        # Need to extrapolate using best fit curve
        return LOW_EXTRAPOLATION_FORMULA(resistance)
    if detected is None:
        # Zero force is the best guess we can have
        return 0.0
    (x0, y0) = (RESISTANCES[i - 1] * 1000, FORCE[i - 1])
    (x1, y1) = (RESISTANCES[i] * 1000, FORCE[i])

    return y0 + ((resistance - x0) * (y1 - y0) / (x1 - x0))


@dataclass
class ProcessedInsoleData:
    nodeId: int
    raw: InsoleData
    calculatedForces: tuple[float, float, float, float, float, float, float, float]
    forceCenterX: float  # In cm
    forceCenterY: float  # In cm


@dataclass
class ProcessedFlexData:
    nodeId: int
    raw: FlexData
    bendAngleDegrees: float


def process_flex_data(flex_data: FlexData) -> ProcessedFlexData:
    resistance = flex_data.flexData.calculatedResistance

    return ProcessedFlexData(
        nodeId=flex_data.nodeId, raw=flex_data, bendAngleDegrees=resistance
    )


def process_insole_data(insole_data: InsoleData, left_foot) -> ProcessedInsoleData:
    insolePressures = tuple(res[2] for res in insole_data.insoleData)

    calculatedForces = list(linear_interpolate(force) for force in insolePressures)

    cx, cy = get_center_of_pressure(calculatedForces)

    if left_foot:
        cx *= -1
    # print(calculatedForces)
    return ProcessedInsoleData(
        nodeId=insole_data.nodeId,
        raw=insole_data,
        calculatedForces=calculatedForces,
        forceCenterX=cx,
        forceCenterY=cy,
    )


if __name__ == "__main__":
    print(linear_interpolate(50000))
