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

    Raises:
        SystemExit: Exits the script if the directory does not exist.
    """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    target_directory = os.path.join(current_directory, directory_name)
    if not os.path.exists(target_directory) or not os.path.isdir(target_directory):
        print(f"'{directory_name}' does not exist.")
        exit(1)

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
    except FileNotFoundError:
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

def extract_lines_with_specified_format(text):
    """
    Extract lines with a specified format from the text.

    Args:
        text (str): The input text.

    Returns:
        str: Extracted lines with the specified format.
    """
    pattern = r'(?m)^(\d{2}/\d{2}/\d{4} \d{2}:\d{2})\|(\d+(?:[.,]\d+)?)\|([^|]+)\|([^|]+)\|(\d+(?:[.,]\d+)?)\|([^|]*)\|(.*)$'
    datetime_lines = re.findall(pattern, text)

    extracted_data = []
    for date, oldvalue, range, unit, value, name, rest in datetime_lines:
        data_dict = {
            'date': date,
            'oldvalue': oldvalue,
            'range': range,
            'unit': unit,
            'value': value,
            'name': name
        }
        extracted_data.append(data_dict)
    save_as_json(extracted_data, data_file)

    return "\n".join(f"{date}|{oldvalue}|{range}|{unit}|{value}|{name}" for date, oldvalue, range, unit, value, name, rest in datetime_lines)

def process_html_data(read_path, write_path):
    """
    Process data from an HTML file and save it as a text file.

    Args:
        read_path (str): The path to the input HTML file.
        write_path (str): The path to the output text file.
    """
    # Detect encoding
    with open(read_path, 'rb') as file:
        raw_data = file.read()

    result = chardet.detect(raw_data)
    encoding = result['encoding']

    # Read
    with open(read_path, 'r', encoding=encoding) as file:
        content = file.read()

    # Modify
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
    content = extract_lines_with_specified_format(content)

    # Write
    with open(write_path, 'w', encoding=encoding) as file:
        file.write(content)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')

    # Check if directories exist
    check_directory(exe_dir)
    check_directory(pdf_dir)

    # Remove out directory if exists
    remove_directory(out_dir)

    pdf_files = [file for file in os.listdir(pdf_dir) if file.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in the {pdf_dir} directory")
        exit(1)

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
        write_path = "{}/{}.txt".format(out_dir, fname)

        process_html_data(read_path, write_path)

        # Remove out directory
        remove_directory(out_dir)

        print(f"----- {pdf_file} done {pdf_file_count}/{len(pdf_files)}", flush=True)
    
    print(f"All done {pdf_file_count}/{len(pdf_files)}")