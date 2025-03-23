# https://www.google.com/about/careers/applications/jobs/results?target_level=EARLY&degree=BACHELORS&location=India

import html
import random
import requests
from bs4 import BeautifulSoup
import re
import subprocess
import json
import copy


url = f"https://www.google.com/about/careers/applications/jobs/results?location=South%20Africa"
# url = f"https://www.google.com/about/careers/applications/jobs/results?target_level=EARLY&degree=BACHELORS&location=India"
response = requests.get(url,verify = False)
# print(response.text)
soup = BeautifulSoup(response.text, "html.parser")

# Pretty print the HTML
# print(soup.prettify())

# Extract all links
# links = [a["href"] for a in soup.find_all("a", href=True)]
# print(links)
# temp = soup.find_all('script')
# for elements in soup.script.next_siblings:
#     print(elements)
#     print("                         ========================================                               ===========================")

# that_class = soup.find(class_="ds:1")
# # print(soup.find(class_="ds:1"))
# print(that_class.contents)


# match = re.search(r"AF_initDataCallback\((\{.*?\})\);", response.text, re.DOTALL)

# if match:
#     print(match)
#     json_data = match.group(1)  # Extract JSON-like data
#     data = json.loads(json_data)  # Convert to Python dictionary
#     print(data)
# else:
#     print("AF_initDataCallback data not found")

# match = re.search(r"AF_initDataCallback\((\{.*?\})\);", response.text, re.DOTALL)

# if match:
#     json_data = match.group(1)  # Extract raw JSON-like data
    
#     # Fix JSON formatting:
#     json_data = re.sub(r"(\w+):", r'"\1":', json_data)  # Add quotes around keys
#     json_data = json_data.replace("'", '"')  # Replace single quotes with double quotes

#     # Convert to Python dictionary
#     try:
#         data = json.loads(json_data)
#         print(data)
#     except json.JSONDecodeError as e:
#         print("JSON Decode Error:", e)
# else:
#     print("AF_initDataCallback data not found")

# Extract the AF_initDataCallback data
match = re.search(r"AF_initDataCallback\((\{.*?\})\);", response.text, re.DOTALL)

if match:
    json_data = match.group(1)  # Extract raw JSON-like data
    print(json_data)
    # Step 1: Ensure keys are enclosed in double quotes
    json_data = re.sub(r"([{,]\s*)(\w+)(\s*):", r'\1"\2":', json_data)  

    # Step 2: Convert single quotes to double quotes
    json_data = json_data.replace("'", '"')

    # Step 3: Remove trailing commas which are not valid in JSON
    json_data = re.sub(r",\s*}", "}", json_data)
    json_data = re.sub(r",\s*]", "]", json_data)

    # Convert to Python dictionary
    try:
        data = json.loads(json_data)
        print("===================================================")
        print(json.dumps(data, indent=4))  # Pretty-print the JSON
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
else:
    print("AF_initDataCallback data not found")


def replace_str_index(text,index=0,replacement=''):
    return f'{text[:index]}{replacement}{text[index+1:]}'

# Regular expression to find the AF_initDataCallback block with key: 'ds:1'
pattern = r"AF_initDataCallback\(\s*\{\s*key:\s*'ds:1',.*?\}\s*\);"

match = re.search(pattern, response.text, re.DOTALL)


if match:
    json_data = match.group(0)  
    print("Extracted Data:", json_data)  # Debugging step

    match = re.search(r"AF_initDataCallback\((\{.*\})\);?$", json_data, re.DOTALL)

    json_text = match.group(1)  # Extracted JSON-like text
    # json_text = json_text.replace("',", '",')  # Replace single quotes with double quotes
    # # json_text = json_text.replace('", "', '", "')  # Ensure proper JSON syntax
    # json_text = json_text.replace(",'", ',"')
    json_text = re.sub(r"([{,]\s*)(\w+)(\s*):", r'\1"\2":', json_text)
    # 🔹 Fix invalid JSON format
    # json_text = json_text.replace('*"s', "*'s")#.replace('"s', "'s")
    # for i in range(0,len(json_text)):
    #     if((json_text[i] == '"') and (json_text[i-1].isalpha()) and (json_text[i+1].isalpha())):
    #         print("here")
    #         # json_text[i] = "'"
    #         json_text = replace_str_index(json_text,i,"'")
    #         i = i+2
    #         pass
    # 🔹 Convert escaped HTML characters back (like `\u003c` → `<`)
    json_text = html.unescape(json_text)

    # extracted_data = re.sub(r"([{,])\s*(\w+)\s*:", r'\1"\2":', json)  # Add quotes around keys
    # extracted_data = extracted_data.replace("'", '"')  # Convert single quotes to double quotes
    # extracted_data = re.sub(r",\s*}", "}", extracted_data)
    print(json_text)
    # Convert to Python dictionary
    try:
        data = json.loads(json_text)
        print(json.dumps(data, indent=4))  # Pretty-print the JSON
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
else:
    print("No match found for AF_initDataCallback with key: 'ds:1'")




