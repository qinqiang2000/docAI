import json

from core.evaluator.json_custom_evl import evaluate_json, evaluate_json_str, flatten_json

# 示例测试用例
prediction2 = [
  {
    "guest_name": "赵伟斌",
    "arrival": "2024.3.4",
    "departure": "2024.3.5",
    "total_amount": "",
    "hotel_name": "城市便捷南宁琅东长湖店",
    "details": [
      {
        "accommodation_date": "2024.3.4",
        "expense_item": "标准房租",
        "expense_amount": "142.00"
      }
    ]
  }
]

reference2 = [
  {
    "guest_name": "赵伟斌1111",
    "arrival": "2024.3.4",
    "departure": "2024.3.5",
    "total_amount": "",
    "hotel_name": "城市便捷南宁琅东长湖店1111",
    "details": [
      {
        "accommodation_date": "2024.3.4",
        "expense_item": "标准房租",
        "expense_amount": "142.00"
      }
    ]
  }
]

# 示例使用
prediction3 = {
    "name": "John",
    "age": 30,
    "children": [
        {"name": "Alice", "age": 10},
        {"name": "Bob", "age": 8}
    ],
    "address": {
        "street": "123 Main St",
        "city": "Anytown"
    }
}

reference3 = {
    "name": "John",
    "age": 30,
    "children1111": [
        {"name": "Alice", "age": 10},
        {"name": "Bob", "age": 8}
    ],
    "address": {
        "street": "123 Main St",
        "city": "Anytown"
    }
}

# 测试evaluate_json函数
result = evaluate_json(prediction2, reference2)
print(result)

result = evaluate_json(prediction3, reference3)
print(result)


# 示例测试
prediction_str1 = json.dumps(prediction2)
reference_str1 = json.dumps(reference2)

# 调用evaluate_json_str函数
result_str1 = evaluate_json_str(prediction_str1, reference_str1)
print(result_str1)

# 测试无法转换为JSON的字符串比较
prediction_str2 = "2024/02/04"
reference_str2 = "2024-02-04"

# 调用evaluate_json_str函数
result_str2 = evaluate_json_str(prediction_str2, reference_str2)
print(result_str2)



# 示例使用
json_data = [{
  "name": "John",
  "age": 30,
  "children": [
    {"name": "Alice", "age": 10},
    {"name": "Bob", "age": 8}
  ],
  "address": {
    "street": "123 Main St",
    "city": "Anytown"
  }
}]

flattened_list = flatten_json(json_data)
print(flattened_list)