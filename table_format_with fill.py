from prettytable import PrettyTable
from colorama import Fore, Back, Style, init
import csv
import textwrap

# Initialize Colorama
init(autoreset=True)

COLUMN_WIDTH = 20  # Set your desired width

def process_cell(text, width, bg_color, fg_color):
    """Create cells with full-width background coloring"""
    # Wrap text into lines
    wrapped = textwrap.wrap(str(text), width=width)
    
    # Pad each line to exact width
    processed_lines = []
    for line in wrapped:
        padded = line.ljust(width)  # Fill remaining space with background color
        processed_lines.append(f"{bg_color}{fg_color}{padded}{Style.RESET_ALL}")
    
    return '\n'.join(processed_lines)

# Configure the table
table = PrettyTable()
table.border = True
table.hrules = True  # Show horizontal lines between rows

with open("data.csv", "r") as file:
    reader = csv.reader(file)
    headers = next(reader)
    
    # Set headers with yellow background
    table.field_names = [
        process_cell(
            header.upper(), 
            COLUMN_WIDTH,
            Back.YELLOW + Fore.BLACK,
            Fore.BLACK
        ) for header in headers
    ]
    
    # Set column widths (ONLY use max_width)
    for header in headers:
        table.max_width[header] = COLUMN_WIDTH  # ✅ Correct attribute
    
    # Add rows with alternating colors
    for row_idx, row in enumerate(reader):
        # Choose colors
        if row_idx % 2 == 0:
            bg_color, fg_color = Back.LIGHTCYAN_EX, Fore.BLACK  # Even rows
        else:
            bg_color, fg_color = Back.LIGHTBLACK_EX, Fore.WHITE  # Odd rows (gray)
        
        # Process each cell
        colored_row = [
            process_cell(
                cell, 
                COLUMN_WIDTH,
                bg_color,
                fg_color
            ) for cell in row
        ]
        table.add_row(colored_row)

print(table)
