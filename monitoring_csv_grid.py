#!/usr/bin/env python3
###########################################################################
######## Script to get maintance Detailswith API                         ##
######## Created By    : MATHAPATI Siddharamayya                         ##
######## Creation Date : 15th March 2024                                 ##
######## Email         : msidrm455@gmail.com							               ##
######## Version       : 2.0                                             ##
###########################################################################

import os
import csv
import sys
import random
import requests
import requests
import textwrap
import subprocess
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from prettytable import PrettyTable, ALL
from tabulate import tabulate
from colorama import Fore, Back, Style

class Color:
    RESET = "\033[0m"
    GREEN = "\033[32m"
    MANGENTA = "\033[35m"
    CYAN = "\033[36m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
def convert_minutes(duration_minutes):
    # Calculate days, hours, and remaining minutes
    days = duration_minutes // (24 * 60)
    remaining_minutes = duration_minutes % (24 * 60)
    hours = remaining_minutes // 60
    minutes = remaining_minutes % 60

    # Print the result
    duration = f"{days} days, {hours} hours, and {minutes} minutes"
    return duration


def caremafunc(hostname, csv_file):
    carema_uri = "https://monitoring.mydomain.org/monitoring/maintenances/"
    url = f"{carema_uri}/{hostname}"
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)

    try:
        response = session.get(url)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
    except requests.exceptions.RequestException as e:
        #print(f"Failed to connect to {url}: {e}")
        return

    hostdetails = data.get(hostname, {}).get("unitary", [])

    #for maintainance in hostdetails:
     #   print(f"ID:{Color.GREEN}{maintainance.get('maintenanceId')}{Color.RESET} SERVER:{Color.RED}{maintainance.get('label')}{Color.RESET} STATUS:{Color.MANGENTA}{maintainance.get('statutMaintenance')}{Color.RESET} USER:{Color.CYAN}{maintainance.get('creationUser')}{Color.RESET} COMMENT:{Color.YELLOW}{maintainance.get('comments')}{Color.RESET} FROM:{Color.CYAN}{maintainance.get('startTime')}{Color.RESET} TO:{Color.CYAN}{maintainance.get('endTime')}{Color.RESET}")
    # Generate a random number for the file name
    #random_number = random.randint(1000, 9999)

    # Save data to CSV file with random number in the name
    #csv_file = f"INPUTFILES/maintenance_data_{random_number}.csv"
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists or os.stat(csv_file).st_size == 0:
            writer.writerow(['ID', 'SERVER', 'STATUS', 'USER', 'COMMENT', 'FROM', 'TO', 'DURATION'])
        for maintainance in hostdetails:
            writer.writerow([
                maintainance.get('maintenanceId'),
                maintainance.get('label'),
                maintainance.get('statutMaintenance'),
                maintainance.get('creationUser'),
                maintainance.get('comments'),
                maintainance.get('startTime'),
                maintainance.get('endTime'),
                convert_minutes(maintainance.get('durationMinutes'))


            ])

    #print(f"The data saved to {csv_file}..")

def wrap_and_color_text(text, width, bg_color, fg_color, num_lines):
    wrapped_lines = textwrap.wrap(str(text), width=width)
    #PADDed_lines = [line.ljust(width) for line in wrapped_lines]
    wrapped = wrapped_lines[:num_lines] + [''] * (num_lines - len(wrapped_lines))
    colored_lines = []
    for line in wrapped:
        padded = line.ljust(width)
        colored = f"{bg_color}{fg_color}{padded}{Style.RESET_ALL}"
        colored_lines.append(colored)
    #colored_lines = f"{color}{wrapped_lines}{Style.RESET_ALL}"
    #return '\n'.join([f"{color}{line}{Style.RESET_ALL}" for line in padded_lines])
    return '\n'.join(colored_lines)

def colorize_headers(text, width):
    padded_text = text.ljust(width)
    return f"{Fore.WHITE}{Style.BRIGHT}{Back.BLUE}{padded_text}{Style.RESET_ALL}"


def print_table(csv_file):
    data = []
    table = PrettyTable()
    max_width = 50
    table.border = True
    table.hrules = True
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        colored_headers = [ wrap_and_color_text(col, 30, Back.LIGHTRED_EX, Style.BRIGHT + Fore.WHITE, num_lines=1) for col in headers]
        table.field_names = colored_headers


        for field in table.field_names:
            table.max_width[field] = max_width

        #FOR header in headers:
            #table.max_width[header] = max_width
            #table.min_width[header] = max_width
        #table_row = []
        for i, row in enumerate(reader):
            if  i % 2 == 0:
                #bg  = "\033[48;5;195m"
                bg = Back.LIGHTWHITE_EX
                fg = Style.BRIGHT + Fore.BLACK
                #colored_row = [f"{Fore.LIGHTCYAN_EX}{val}{Style.RESET_ALL}" for val in row]
            else:
                bg = Back.LIGHTBLACK_EX
                #bg = "\033[48;5;153m"
                fg = "\033[1m\033[1m"
                #fg = Style.BRIGHT + Fore.WHITE
                #colored_row = [f"{Fore.LIGHTGREEN_EX}{val}{Style.RESET_ALL}" for val in row]
            wrapped_cell = [textwrap.wrap(cell, max_width) for cell in row]
            max_lines = max(len(lines) for lines in wrapped_cell)
            colored = [wrap_and_color_text(val, 30, bg, fg, max_lines) for val in row]
            table.add_row(colored)
    # Set max width for each column
        #print(tabulate(tABLE_row, headers=colored_headers, tablefmt="grid"))
        #print(table)
        tablei_str = table.get_string()
        with subprocess.Popen(["less", "-S", "-R", "-X"], stdin=subprocess.PIPE) as pager:
            pager.stdin.write(tablei_str.encode("utf-8"))
            pager.stdin.close()

        print(f"The data saved to {csv_file}..")

def main():
    random_number = random.randint(1000, 9999)
    csv_file = f"INPUTFILES/maintenance_data_{random_number}.csv"
    for hostname in sys.argv[1:]:
        if os.path.isfile(hostname):
            try:
                with open(hostname, 'r') as file:
                    for host in file:
                        caremafunc(host.strip(), csv_file)

            except FileNotFoundError:
                print(f"ERROR: File Not Found...")
        else:
            caremafunc(hostname, csv_file)

    print_table(csv_file)


if __name__ == "__main__":
        main()

