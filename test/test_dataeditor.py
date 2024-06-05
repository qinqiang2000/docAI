import pandas as pd

# 假设df是你的DataFrame
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9]
})

# 将最后一行移动到第一行
df = pd.concat([df.iloc[-1:], df.iloc[:-1]], ignore_index=True)
print(df)