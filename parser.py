from PyPDF2 import PdfReader
from datetime import datetime
from main import YearMonth, Destination, db, app
from sqlalchemy import select
import re

display_year = None
display_month = None


def get_pdf_content_lines(file):
    # pdf --> lines
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        for line in page.extract_text().splitlines():
            yield line


def read_file_lines(path):
    # lines --> array of strings
    file_as_lines = []
    for line in get_pdf_content_lines(path):
        file_as_lines.append(line)
    # Beijing (PEK) CN PEK 246.42$     $0.00 *No Change 0.0% $49.93 $56.94 $108.29 $31.26 246.42 $
    # Havana (HAV) CU HAV 122.36$     -$0.51 -0.41% $24.56 $27.81 $55.09 $14.39 121.85 $
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
        if '$' not in line:
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
            price_list = re.findall(r'-?\$?\d{1,3}\.\d{1,2}%?', line)
            price_list = [re.sub('$', '', s) for s in price_list]
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
        # print(date_id)
        # if date_id:
        #     # entry_to_update = db.session.query(YearMonth).where(id=yearmonth_id).first()
        #     # db.session.
        #     print('pass')
        #     pass
        # else:
        db.session.add(new_entry)
        db.session.commit()
