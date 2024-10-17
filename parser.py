from os.path import exists
from PyPDF2 import PdfReader
from datetime import datetime
from main import Destination, db, app
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
        new_destination = Destination()
        new_destination.id = i

        line = data[i]

        if 'Canada' in line:
            new_destination.destination = 'Canada'
        elif 'Jamaica' in line:
            new_destination.destination = 'Jamaica - Other'
        elif 'Mexico - Other' in line:
            new_destination.destination = 'Mexico - Other'
        elif 'U.S.' in line:
            new_destination.destination = 'U.S.'
        else:
            dest_list = re.findall(r'[A-Z]{3}\)', line)
            last_index_destination = line.index(dest_list[len(dest_list) - 1]) + 5
            new_destination.destination = line[0:last_index_destination]

        line = line[len(new_destination.destination):]
        new_destination.country_code = re.findall(r'[A-Z]{2}', line)[0]
        # station column could be Airport code (ex. ALG) or * for multiple
        if re.search(r'[A-Z]{3}', line):
            new_destination.airport_code = re.findall(r'[A-Z]{3}', line)[0]
        else:
            new_destination.airport_code = '*'
        # destinations can be bracelet or per diem
        if not '$' in line:
            new_destination.bracelet_provided = True
            new_destination.prev_allowance = None
            new_destination.adjustment = None
            # new_destination.status = None
            new_destination.percent_change = None
            new_destination.breakfast = None
            new_destination.lunch = None
            new_destination.dinner = None
            new_destination.snack = None
            new_destination.total = None
        else:
            new_destination.bracelet_provided = False
            price_list = re.findall(r'-?\d{1,3}\.\d{2}', line)
            # print(f'{new_destination.destination}, Price List: {price_list}')
            # percentage_list = re.findall(r'\d{1,2}\.\d{1,2}\%', line)
            new_destination.prev_allowance = price_list[0]
            new_destination.adjustment = price_list[1]
            # new_destination.status = ('*No Change' in line)
            # new_destination.percent_change = percentage_list[0]
            new_destination.percent_change = price_list[2]
            new_destination.breakfast = price_list[3]
            new_destination.lunch = price_list[4]
            new_destination.dinner = price_list[5]
            new_destination.snack = price_list[6]
            new_destination.total = price_list[7]

        if 'Zurich' in new_destination.destination:
            new_destination.airport_code = '*'

        with app.app_context():
            # db.session.add(new_destination)
            # db.session.commit()
            pass


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
