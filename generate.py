"""
PDF to JSON Data Conversion Script
This script processes PDF files, extracts structured data from them, and saves the data in a JSON format.
The PDF files should be downloaded in the 'pdf' folder from any of Turkish 'Probel' hospital system

Requirements:
- chardet: Character encoding detection library
- pdf2htmlEX: PDF to HTML conversion tool in 'exe' folder

Usage:
1. Place your PDF files in the 'pdf' folder.
2. Run the script to process the PDF files and generate JSON data.

The script performs the following steps:
1. Converts PDF files to HTML format using pdf2htmlEX.
2. Extracts data from the generated HTML files.
3. Cleans and processes the extracted data.
4. Saves the cleaned data as a JSON file named 'data.json'.

Author: Eray Ozturk | erayozturk1@gmail.com 
URL: github.com/diffstorm
Date: 01/10/2023
"""

import subprocess
import chardet
import re
import os
import html
import json
import sys
import shutil
from datetime import datetime

# Exe directory is the folder where pdf2htmlEX is
exe_dir = "exe"

# csv directory is where the csv files are
csv_dir = "csv"

# pdf directory is where the pdf files are
pdf_dir = "pdf"

# Out directory is the temporary folder that pdf2htmlEX generates its data
out_dir = "out"

# Database file that all the parsed data recorded
data_file = "data.json"

def check_directory(directory_name):
    """
    Check if the specified directory exists.

    Args:
        directory_name (str): The name of the directory to check.

    Returns:
        bool: True if given directory exists, False otherwise.
    """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_directory = os.path.join(current_directory, directory_name)
    if not os.path.exists(target_directory) or not os.path.isdir(target_directory):
        return False
    return True

def remove_directory(directory_name):
    """
    Remove the specified directory if it exists.

    Args:
        directory_name (str): The name of the directory to remove.
    """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_directory = os.path.join(current_directory, directory_name)
    if os.path.exists(target_directory) and os.path.isdir(target_directory):
        shutil.rmtree(target_directory)
        print(f"'{directory_name}' directory removed.")

def run_process(command):
    """
    Run a shell command and capture its output.

    Args:
        command (str): The shell command to run.
    """
    print(command)
    current_directory = os.path.dirname(os.path.abspath(__file__))
    try:
        result = subprocess.run(os.path.join(current_directory, command), shell=True, capture_output=True, text=True, check=True)
        print("Output:", result.stdout)
        print("Errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("Error occurred with return code:", e.returncode)
        print("Error message:", e.stderr)

def save_as_json(data, file_path):
    """
    Save a list of data entries as a JSON file.

    Args:
        data (list): List of data entries (dictionaries).
        file_path (str): The path to the JSON file where data will be saved.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        existing_data = []

    # Create a dictionary to hold data with unique identifiers as keys
    data_dict = {(entry["date"], entry["name"]): entry for entry in existing_data}

    # Update the dictionary with new data
    for entry in data:
        identifier = (entry["date"], entry["name"])
        data_dict[identifier] = entry

    # Convert the dictionary back to a list of data entries
    existing_data = list(data_dict.values())

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)

def remove_attribute(text, attribute_name, quote_character='"'):
    """
    Remove a specified HTML attribute from the text.

    Args:
        text (str): The input text containing HTML attributes.
        attribute_name (str): The name of the attribute to remove.
        quote_character (str): The character used for attribute quoting.

    Returns:
        str: The text with the specified attribute removed.
    """
    pattern = r'{}={}[^{}]*{}'.format(attribute_name, quote_character, quote_character, quote_character)
    return re.sub(pattern, '', text)

def insert_newline_before_datetime(text):
    """
    Insert a newline character before datetime patterns in the text.

    Args:
        text (str): The input text.

    Returns:
        str: The text with newlines inserted before datetime patterns.
    """
    pattern = r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}'
    updated_text = re.sub(pattern, r'\n\g<0>', text)
    return updated_text

def extract_datetime_lines_with_text(text):
    """
    Extract lines with datetime patterns from the text.

    Args:
        text (str): The input text.

    Returns:
        str: Extracted lines with datetime patterns.
    """
    pattern = r'^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}.*)'
    datetime_lines = re.findall(pattern, text, re.MULTILINE)
    return "\n".join(datetime_lines)

def fix_floating_point_numbers(text):
    """
    Replace comma separators with dots in floating-point numbers.

    Args:
        text (str): The input text.

    Returns:
        str: The text with fixed floating-point numbers.
    """
    def replace_comma_with_dot(match):
        number = match.group(0)
        return number.replace(',', '.')
    pattern = r'\d+(?:,\d+)+|\d+,\d+'
    return re.sub(pattern, replace_comma_with_dot, text)

def is_valid_row(data):
    """
    Check if a row of data meets the validity criteria.

    Args:
        data (dict): A dictionary containing data for a row.

    Returns:
        bool: True if the row is valid, False otherwise.
    """
    return (
        data["date"] and
        re.match(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}', data["date"]) and
        re.match(r'^-?\d+\.\d*$', data["value"]) and
        data["name"]
    )

def extract_lines_with_specified_format(text):
    """
    Extract lines with a specified format from the text.

    Args:
        text (str): The input text.

    Returns:
        str: Extracted data in json format.
    """
    pattern = r'(?m)^(\d{2}/\d{2}/\d{4} \d{2}:\d{2})\|(\d+(?:[.,]\d+)?)\|([^|]+)\|([^|]+)\|(\d+(?:[.,]\d+)?)\|([^|]*)\|(.*)$'
    datetime_lines = re.findall(pattern, text)

    extracted_data = []
    for date, oldvalue, range, unit, value, name, rest in datetime_lines:
        data = {
            'date': date.strip(),
            'oldvalue': oldvalue.strip(),
            'range': range.strip(),
            'unit': unit.strip(),
            'value': value.strip(),
            'name': name.strip()
        }
        if is_valid_row(data):
            extracted_data.append(data)

    return extracted_data

def file_read(path):
    """
    Reads given file and returns the content

    Args:
        path (str): path to the file.
        
    Returns:
        str: File content
    """
    # Detect encoding
    with open(path, 'rb') as file:
        raw_data = file.read()

    result = chardet.detect(raw_data)
    encoding = result['encoding']

    # Read
    with open(path, 'r', encoding=encoding) as file:
        content = file.read()
    
    return content

def process_html_data(content):
    """
    Process data from an HTML file and save it as a text file.

    Args:
        content (str): Content if the HTML file.

    Returns:
        str: Extracted data in json format.
    """
    content = remove_attribute(content, "class")
    content = remove_attribute(content, "id")
    content = remove_attribute(content, "data-data", "'")
    content = remove_attribute(content, "data-page-no")
    while " >" in content:
        content = content.replace(" >", ">")
    content = content.replace("</div></div><div><div>", "|")
    content = content.replace("</div><div>", " ")
    content = content.replace("<div>", "")
    content = content.replace("</div>", "")
    content = content.replace("<span>", "")
    content = content.replace("</span>", "")
    content = html.unescape(content)# Decode HTML entities
    #content = content.replace(">", "").replace("<", "")# Remove any remaining < and > characters
    content = content.replace("*", "")
    content = content.replace("| ", "|")
    content = content.replace(" |", "|")
    content = insert_newline_before_datetime(content)
    content = extract_datetime_lines_with_text(content)
    content = fix_floating_point_numbers(content)
    json = extract_lines_with_specified_format(content)
    
    return json
    
def csv_extract_valid_rows(csv_data):
    """
    Extract lines with valid date-time patterns and a single semicolon at the end.

    Args:
        csv_data (str): The input CSV data as a string.

    Returns:
        list: A list of lines that meet the criteria.
    """
    # Clean unwanted characters
    csv_data = csv_data.replace("  ", " ").replace("  ", " ").replace(" >", ">").replace("*", "")
    # Fix numbers
    csv_data = fix_floating_point_numbers(csv_data)

    # Split the CSV data into lines
    csv_lines = csv_data.splitlines()

    # Regular expression pattern to match lines with date and a single semicolon at the end
    pattern = r'.*;\d{2}/\d{2}/\d{4} \d{2}:\d{2};'

    # Find lines that match the pattern and store them
    valid_lines = [line for line in csv_lines if re.match(pattern, line)]

    return valid_lines

def csv_parse_lines(lines):
    """
    Parse the valid CSV lines and extract relevant data.

    Args:
        lines (list): A list of valid CSV lines.

    Returns:
        list: A list of dictionaries containing parsed data.
    """
    parsed_data = []

    for line in lines:
        row = line.strip().split(';')
        data = {
            "name": row[0].strip(),
            "value": row[3].strip(),
            "unit": row[4].strip(),
            "range": row[5].strip(),
            "oldvalue": row[7].strip(),
            "date": row[12].strip()
        }
        if is_valid_row(data):
            parsed_data.append(data)

    return parsed_data

def csv_process():
    if(not check_directory(csv_dir)):
        print(f"ERROR: '{csv_dir}' folder does not exist.")
        return

    csv_files = [file for file in os.listdir(csv_dir) if file.lower().endswith('.csv')]
    if not csv_files:
        print(f"No CSV files found in the {csv_dir} directory")
        return

    print("CSV files in the directory: {}".format(len(csv_files)))
    csv_file_count = 0
    for csv_file in csv_files:
        csv_file_count = csv_file_count + 1
        print(f"----- processing {csv_file} {csv_file_count}/{len(csv_files)}")

        read_path = "{}/{}".format(csv_dir, csv_file)

        # Read file
        csv_data = file_read(read_path)

        # Extract valid rows from the CSV data
        content = csv_extract_valid_rows(csv_data)

        # Parse the valid lines
        json = csv_parse_lines(content)

        # Store
        save_as_json(json, data_file)

        print(f"----- {csv_file} done {csv_file_count}/{len(csv_files)}", flush=True)
    
    print(f"All CSV files done {csv_file_count}/{len(csv_files)}")

def pdf_process():
    if(not check_directory(exe_dir)):
        print(f"ERROR: '{exe_dir}' folder does not exist.")
        return

    if(not check_directory(pdf_dir)):
        print(f"ERROR: '{pdf_dir}' folder does not exist.")
        return

    # Remove out directory if exists
    remove_directory(out_dir)

    pdf_files = [file for file in os.listdir(pdf_dir) if file.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in the {pdf_dir} directory")
        return

    print("PDF files in the directory: {}".format(len(pdf_files)))
    pdf_file_count = 0
    for pdf_file in pdf_files:
        pdf_file_count = pdf_file_count + 1
        print(f"----- processing {pdf_file} {pdf_file_count}/{len(pdf_files)}")

        # Run a command and capture its output
        command = "{}/pdf2htmlEX.exe --embed cfijo --dest-dir \"{}\" --optimize-text 1 --process-nontext 0 \"{}/{}\"".format(exe_dir, out_dir, pdf_dir, pdf_file)
        run_process(command)

        fname = os.path.splitext(os.path.basename(pdf_file))[0]
        read_path = "{}/{}.html".format(out_dir, fname)

        # Read file
        content = file_read(read_path)

        # Modify
        json = process_html_data(content)

        # Store
        save_as_json(json, data_file)
        
        # Remove out directory
        remove_directory(out_dir)

        print(f"----- {pdf_file} done {pdf_file_count}/{len(pdf_files)}", flush=True)
    
    print(f"All PDF files done {pdf_file_count}/{len(pdf_files)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')

    csv_process()
    pdf_process()
    
    print("Fin.")