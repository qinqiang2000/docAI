from core.common import compare_values

vals = [
    # ("2019-02-18", "02/18/19"),
    # ("2023-08-04", "4-Aug-23"),
    ("2023/7/6", "06.07.2023"),  #
    # (1698.68, "1698.68"),
    # (1698.68, "1698.6800"),
]

for v in vals:
    ret = compare_values(v[0], v[1])
    print(f"{v} : {ret}")
