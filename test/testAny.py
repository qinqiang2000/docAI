import json
import re
from typing import List, Any

def extract_json(text: str) -> List[dict]:
    """Extracts JSON content from a string where JSON is embedded between ```json and ``` tags.

    Parameters:
        text (str): The text containing the JSON content.

    Returns:
        list: A list of extracted JSON objects.
    """
    # Define the regular expression pattern to match JSON blocks
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"

    # Find all non-overlapping matches of the pattern in the string
    matches = re.findall(pattern, text, re.DOTALL)

    # Attempt to parse the matches as JSON
    extracted_json = []
    for match in matches:
        print(match.strip())
        # Remove the 'json' string if present at the beginning
        cleaned_match = re.sub(r"^json\s*", "", match.strip(), flags=re.IGNORECASE)
        try:
            parsed_json = json.loads(cleaned_match)
            extracted_json.append(parsed_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {cleaned_match}. Error: {e}")

    return extracted_json

def flatten_if_single_nested_array(parsed_json: List[Any]) -> List[dict]:
    """Flattens the JSON if it is a single nested array.

    Parameters:
        parsed_json (list): The parsed JSON content.

    Returns:
        list: Flattened JSON content if applicable.
    """
    if len(parsed_json) == 1 and isinstance(parsed_json[0], list):
        return parsed_json[0]
    return parsed_json

str = """
 Here is the extracted information in JSON format:

```
json
[
  {
    "guest_name": "张君",
    "arrival": "2023-09-07",
    "departure": "",
    "total_amount": "380.00"
  }
]
```

Note: The `departure` field is left blank since there is no information about the departure date in the provided OCR text. The `hotel_name` field is also left blank since there is no information about the hotel name in the provided OCR text.

"""

print(extract_json(str))