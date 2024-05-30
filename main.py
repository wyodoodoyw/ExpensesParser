from os.path import exists
from PyPDF2 import PdfReader
from tkinter import *
from tkinter.filedialog import askopenfile
import re
import json

path = '/Users/wyodoodoyw/Local Documents/Python/Expenses Parser/202403-MealAllowances.pdf'


def get_pdf_content_lines(path):
    with open(path, 'rb') as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            for line in page.extract_text().splitlines():
                yield line


def read_file_lines(path):
    #convert pdf file to array of strings, one string per line
    file_as_lines = []
    #global path
    for line in get_pdf_content_lines(path):
        file_as_lines.append(line)

    return file_as_lines


def find_start_line(data):
    #locate last line of header/column labels
    for i in range(0, len(data)):
        if "AllowanceAdjustment" in data[i]:
            return i + 1


def find_end_line(data):
    return [idx for idx, s in enumerate(data) if 'Zurich' in s][0] + 1


def parse(data):
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
        #station column could be Airport code (ex. ALG) or * for multiple
        if re.search(r'[A-Z]{3}', line):
            airport_code = re.findall(r'[A-Z]{3}', line)[0]
        else:
            airport_code = '*'
        #destinations can be bracelet or per diem
        if not '$' in line:
            bracelet_provided = True
            # price_list = None
            # percentage_list = None
            # previous_allowance = None
            # adjustment = None
            # status = None
            # percent_change = None
            # breakfast = None
            # lunch = None
            # dinner = None
            # snack = None
            # total = None
        else:
            bracelet_provided = False
            price_list = re.findall(r'\d{1,3}\.\d{2}', line)
            percentage_list = re.findall(r'\d\.\d\%', line)
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
        elif new_destination[destination]['bracelet_provided']:
            new_destination[destination]['previous_allowance'] = None
            new_destination[destination]['adjustment'] = None
            new_destination[destination]['status'] = None
            new_destination[destination]['percent_change'] = None
            new_destination[destination]['breakfast'] = None
            new_destination[destination]['lunch'] = None
            new_destination[destination]['dinner'] = None
            new_destination[destination]['snack'] = None
            new_destination[destination]['total'] = None
        save(new_destination)


def save(new_destination):
    try:
        with open('data.json', 'r') as data_file:
            data = json.load(data_file)

    except FileNotFoundError:
        with open('data.json', 'w') as data_file:
            json.dump(new_destination, data_file, indent=4)

    else:
        data.update(new_destination)
        with open('data.json', 'w') as data_file:
            json.dump(data, data_file, indent=4)
    finally:
        pass


def pre_search():
    search_term = search_entry.get()
    is_usa = search_term in ['SFO', 'LAX', 'SAN', 'PSP', 'SMF',
                'SNA', 'MCO', 'TPA', 'FLL', 'PBI',
                'MIA', 'RSW', 'SRQ', 'HNL', 'KOA',
                'OGG', 'LAS', 'ORD', 'DTW', 'MPS',
                'STL', 'CVG', 'CLE', 'CMH', 'IND',
                'EWR', 'BOS', 'LGA', 'PHL', 'PIT',
                'IAD', 'BDL', 'ATL', 'AUS', 'DFW',
                'IAH', 'BNA', 'MSY', 'CHS', 'DEN',
                'PHX', 'SEA', 'SLC', 'PDX', 'ANC']
    if re.findall(r'Y[A-Z]{2}', search_term):
        search('Canada')
    elif is_usa:
        search('U.S.')
    elif search_term in ['MTY', 'TQO']:
        search('Mexico - Other')
    elif search_term in ['KIN', 'MBJ']:
        search('Jamaica')
    else:
        search(search_term)


def search(search_term):
    try:
        with (open('data.json', 'r') as data_file):
            data = json.load(data_file)
            for destination in data:
                if search_term in destination:
                    destination_label.config(text=destination)
                    if data[destination]['bracelet_provided']:
                        B_label.config(text='')
                        L_label.config(text='')
                        D_label.config(text='')
                        S_label.config(text='')
                        total_label.config(text='Bracelet Provided')
                        return
                    else:
                        B_label.config(text=f'${data[destination]['breakfast']}')
                        L_label.config(text=f'${data[destination]['lunch']}')
                        D_label.config(text=f'${data[destination]['dinner']}')
                        S_label.config(text=f'${data[destination]['snack']}')
                        total_label.config(text=f'${data[destination]['total']}')
                        return
                else:
                    destination_label.config(text='')
                    B_label.config(text='')
                    L_label.config(text='')
                    D_label.config(text='')
                    S_label.config(text='')
                    total_label.config(text='Not Found')
    except FileNotFoundError:
        print("File not found.")

def getExpensesFile():
    curr_dir = os.getcwd()
    json_exists = exists(data.json)
    file = askopenfile()
    full_file_name = file.name
    file_name_suffix = re.split('/', full_file_name)[-1]
    if re.findall('202\d{3}-MealAllowances\.\w{3}', file_name_suffix):
        data = read_file_lines(full_file_name)
        parse(data)
    else:
        print(f'File does not match: {file_name}')

# --- MAIN PROGRAM
window = Tk()
window.title('Pairing Expense Parser')
window.config(padx=10, pady=10)

getExpensesFile()
#data = read_file_lines(path)
#parse()

title_label = Label(text='Pairing Expenses', pady=20)
title_label.grid(column=0, row=0, columnspan=4)

search_label = Label(text='Search: ')
search_entry = Entry()
search_btn = Button(text='Search', command=pre_search)

destination_title_label = Label(text="Destination: ")
destination_label = Label()
B_title_label = Label(text='B: ')
B_label = Label()
L_title_label = Label(text='L: ')
L_label = Label()
D_title_label = Label(text='D: ')
D_label = Label()
S_title_label = Label(text='S: ')
S_label = Label()
line_label = Label(text='-----------------')
total_title_label = Label(text='Total: ')
total_label = Label()

search_label.grid(column=0, row=1)
search_entry.grid(column=1, row=1, columnspan=2)
search_btn.grid(column=3, row=1)
destination_title_label.grid(column=1, row=2)
destination_label.grid(column=2, row=2)
B_title_label.grid(column=1, row=3)
B_label.grid(column=2, row=3)
L_title_label.grid(column=1, row=4)
L_label.grid(column=2, row=4)
D_title_label.grid(column=1, row=5)
D_label.grid(column=2, row=5)
S_title_label.grid(column=1, row=6)
S_label.grid(column=2, row=6)
line_label.grid(column=1, row=7, columnspan=3)
total_title_label.grid(column=1, row=8)
total_label.grid(column=2, row=8)

window.mainloop()
