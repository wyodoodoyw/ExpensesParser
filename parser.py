from os.path import exists
from PyPDF2 import PdfReader
from tkinter import *
from tkinter.filedialog import askopenfile
from datetime import datetime
import re
import json

display_year = None
display_month = None


def get_pdf_content_lines(path):
    # pdf --> lines
    with open(path, 'rb') as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            for line in page.extract_text().splitlines():
                yield line


def read_file_lines(path):
    # lines --> array of strings
    file_as_lines = []
    for line in get_pdf_content_lines(path):
        file_as_lines.append(line)

    return file_as_lines


def find_start_line(data):
    # locate last line of header/column labels
    for i in range(0, len(data)):
        if "AllowanceAdjustment" in data[i]:
            return i + 1


def find_end_line(data):
    # locate last line in pdf
    return [idx for idx, s in enumerate(data) if 'Zurich' in s][0] + 1


def parse(data, year, month):
    for i in range(find_start_line(data), find_end_line(data)):

        line = data[i]

        if 'Canada' in line:
            destination = 'Canada'
        elif 'Jamaica' in line:
            destination = 'Jamaica - Other'
        elif 'Mexico - Other' in line:
            destination = 'Mexico - Other'
        elif 'U.S.' in line:
            destination = 'U.S.'
        else:
            dest_list = re.findall(r'[A-Z]{3}\)', line)
            last_index_destination = line.index(dest_list[len(dest_list) - 1]) + 5
            destination = line[0:last_index_destination]

        line = line[len(destination):]
        country_code = re.findall(r'[A-Z]{2}', line)[0]
        # station column could be Airport code (ex. ALG) or * for multiple
        if re.search(r'[A-Z]{3}', line):
            airport_code = re.findall(r'[A-Z]{3}', line)[0]
        else:
            airport_code = '*'
        # destinations can be bracelet or per diem
        if not '$' in line:
            bracelet_provided = True
            previous_allowance = None
            adjustment = None
            status = None
            percent_change = None
            breakfast = None
            lunch = None
            dinner = None
            snack = None
            total = None
        else:
            bracelet_provided = False
            price_list = re.findall(r'\d{1,3}\.\d{2}', line)
            percentage_list = re.findall(r'\d{1,2}\.\d{1,2}\%', line)
            previous_allowance = price_list[0]
            adjustment = price_list[1]
            status = ('*No Change' in line)
            percent_change = percentage_list[0]
            breakfast = price_list[2]
            lunch = price_list[3]
            dinner = price_list[4]
            snack = price_list[5]
            total = price_list[6]

        new_destination = {
            destination: {
                'country_code': country_code,
                'airport_code': airport_code,
                'bracelet_provided': bracelet_provided,
                'previous_allowance': previous_allowance,
                'adjustment': adjustment,
                'status': status,
                'percent_change': percent_change,
                'breakfast': breakfast,
                'lunch': lunch,
                'dinner': dinner,
                'snack': snack,
                'total': total
            }
        }
        if 'Zurich' in destination:
            new_destination[destination]['airport_code'] = '*'
        save(new_destination, year, month)


def save(new_destination, year, month):
    # save destination objects to json file
    file_name = f'{year}'+f'{month}'
    try:
        with open(f'{file_name}.json', 'r') as data_file:
            data = json.load(data_file)

    except FileNotFoundError:
        with open(f'{file_name}.json', 'w') as data_file:
            json.dump(new_destination, data_file, indent=4)

    else:
        data.update(new_destination)
        with open(f'{file_name}.json', 'w') as data_file:
            json.dump(data, data_file, indent=4)
    finally:
        pass


# def pre_search(year, month):
#     search_term = search_entry.get()
#     is_usa = search_term in ['SFO', 'LAX', 'SAN', 'PSP', 'SMF',
#                              'SNA', 'MCO', 'TPA', 'FLL', 'PBI',
#                              'MIA', 'RSW', 'SRQ', 'HNL', 'KOA',
#                              'OGG', 'LAS', 'ORD', 'DTW', 'MPS',
#                              'STL', 'CVG', 'CLE', 'CMH', 'IND',
#                              'EWR', 'BOS', 'LGA', 'PHL', 'PIT',
#                              'IAD', 'BDL', 'ATL', 'AUS', 'DFW',
#                              'IAH', 'BNA', 'MSY', 'CHS', 'DEN',
#                              'PHX', 'SEA', 'SLC', 'PDX', 'ANC']
#     if re.findall(r'Y[A-Z]{2}', search_term):
#         search('Canada', year, month)
#     elif is_usa:
#         search('U.S.', year, month)
#     elif search_term in ['MTY', 'TQO']:
#         search('Mexico - Other', year, month)
#     elif search_term in ['KIN', 'MBJ']:
#         search('Jamaica', year, month)
#     else:
#         year = datetime.today().year
#         month = f'{datetime.today().month:02d}'
#         search(search_term, year, month)


# def search(search_term, year, month):
#     file_name = f'{year}' + f'{month}'
#     try:
#         with (open(f'{file_name}.json', 'r') as data_file):
#             data = json.load(data_file)
#             for destination in data:
#                 if search_term in destination:
#                     destination_label.config(text=destination)
#                     if data[destination]['bracelet_provided']:
#                         B_label.config(text='')
#                         L_label.config(text='')
#                         D_label.config(text='')
#                         S_label.config(text='')
#                         total_label.config(text='Bracelet Provided')
#                         return
#                     else:
#                         B_label.config(text=f'${data[destination]['breakfast']}')
#                         L_label.config(text=f'${data[destination]['lunch']}')
#                         D_label.config(text=f'${data[destination]['dinner']}')
#                         S_label.config(text=f'${data[destination]['snack']}')
#                         total_label.config(text=f'${data[destination]['total']}')
#                         return
#                 else:
#                     destination_label.config(text='')
#                     B_label.config(text='')
#                     L_label.config(text='')
#                     D_label.config(text='')
#                     S_label.config(text='')
#                     total_label.config(text='Not Found')
#     except FileNotFoundError:
#         print("File not found.")

# def upload():
#     file = askopenfile()
#     full_file_name = file.name
#     file_name_suffix = re.split('/', full_file_name)[-1]
#     if re.findall(r'202\d{3}-Meal\s?Allowances\.\w{3}', file_name_suffix):
#         year = re.findall(r'\d{6}', file_name_suffix)[0][:4]
#         month = re.findall(r'\d{6}', file_name_suffix)[0][-2:]
#         data = read_file_lines(full_file_name)
#         parse(data, year, month)
#     else:
#         print(f'File does not match. You uploaded: {file_name_suffix}')
#         print('Filename format expected" 202xxx-MealAllowances.pdf')
#         pass

def get_expenses_file(year, month):
    file_name = f'{year}' + f'{month}'
    if not exists(f'{file_name}.json'):
        #upload()
        pass


# --- MAIN PROGRAM
year = datetime.today().year
month = f'{datetime.today().month:02d}'
# get_expenses_file(year=year, month=month)

# window = Tk()
# window.title('Pairing Expense Parser')
# #window.geometry('600x300')
# window.config(padx=10, pady=10)
#
# title_label = Label(text=f'Pairing Expenses for {month} {year}', pady=20)
# title_label.grid(column=0, row=0, columnspan=4)
#
# search_label = Label(text='Search: ')
# search_entry = Entry()
# search_btn = Button(text='Search', command= lambda: pre_search(year=year, month=month))
#
# destination_title_label = Label(text="Destination: ")
# destination_label = Label()
# B_title_label = Label(text='B: ')
# B_label = Label()
# L_title_label = Label(text='L: ')
# L_label = Label()
# D_title_label = Label(text='D: ')
# D_label = Label()
# S_title_label = Label(text='S: ')
# S_label = Label()
# line_label = Label(text='-----------------')
# total_title_label = Label(text='Total: ')
# total_label = Label()
# upload_btn = Button(text="Upload New Expenses pdf", command=upload)
#
# search_label.grid(column=0, row=1)
# search_entry.grid(column=1, row=1, columnspan=2)
# search_btn.grid(column=3, row=1)
# destination_title_label.grid(column=1, row=2)
# destination_label.grid(column=2, row=2)
# B_title_label.grid(column=1, row=3)
# B_label.grid(column=2, row=3)
# L_title_label.grid(column=1, row=4)
# L_label.grid(column=2, row=4)
# D_title_label.grid(column=1, row=5)
# D_label.grid(column=2, row=5)
# S_title_label.grid(column=1, row=6)
# S_label.grid(column=2, row=6)
# line_label.grid(column=1, row=7, columnspan=3)
# total_title_label.grid(column=1, row=8)
# total_label.grid(column=2, row=8)
# upload_btn.grid(column=2, row=9)

# window.mainloop()