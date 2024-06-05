import re

from core.evaluator.json_custom_evl import compare_values, is_regex

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


ret = compare_values("//.*房费.*//", "[1702]房费jessie")
print(ret)

print(is_regex('06.07.2023'))