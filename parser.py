from os.path import exists
from PyPDF2 import PdfReader
from datetime import datetime
from main import YearMonth, Destination, db, app
import re

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
    # Beijing (PEK) CN PEK 246.42$     $0.00 *No Change 0.0% $49.93 $56.94 $108.29 $31.26 246.42 $
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
    new_entry = YearMonth(
        id=f'{datetime.now()}',
        year=year,
        month=month,
        destinations=[]
    )
    for i in range(find_start_line(data), find_end_line(data)):
        new_destination = Destination()
        new_destination.id = f'{year}{month}{i}'

        line = data[i]

        if 'Canada' in line:
            new_destination.destination = 'Canada'
        elif 'Jamaica' in line:
            new_destination.destination = 'Jamaica'
        elif 'Mexico - Other' in line:
            new_destination.destination = 'Mexico'
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
            new_destination.percent_change = None
            new_destination.breakfast = None
            new_destination.lunch = None
            new_destination.dinner = None
            new_destination.snack = None
            new_destination.total = None
            new_destination.date_id = new_entry.id
        else:
            new_destination.bracelet_provided = False
            price_list = re.findall(r'-?\d{1,3}\.\d{1,2}', line)
            # ['238.66', '0.00', '0.00', '42.36', '75.39', '94.22', '26.69', '238.66']
            # ['238.66', '0.00', '0.0', '42.36', '75.39', '94.22', '26.69', '238.66']
            # print(f'else: {price_list}')
            new_destination.prev_allowance = price_list[0]
            new_destination.adjustment = price_list[1]
            new_destination.percent_change = re.findall(r'-?\d{1,2}\.\d{1,2}%', line)[0]
            new_destination.breakfast = price_list[3]
            new_destination.lunch = price_list[4]
            new_destination.dinner = price_list[5]
            new_destination.snack = price_list[6]
            new_destination.total = price_list[7]
            new_destination.date_id = new_entry.id

        if 'Zurich' in new_destination.destination:
            new_destination.airport_code = '*'

        new_entry.destinations.append(new_destination)
        # print(new_entry)

        with app.app_context():
            db.session.add(new_destination)
    with app.app_context():
        db.session.add(new_entry)
        db.session.commit()


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
        # upload()
        pass
