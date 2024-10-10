from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import DateField, FileField, SearchField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired #, FileRequired, FileAllowed
from parser import *
import requests, os

app = Flask(__name__)
Bootstrap5(app)

UPLOAD_FOLDER = '/data/'
ALLOWED_EXTENSIONS = {'json'}
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

year = datetime.today().year
month = f'{datetime.today().month:02d}'

choices = [f'{year} - {month}']


class ExpensesForm(FlaskForm):
    select_date = SelectField(label="Select Expenses Month:", choices=choices)
    upload_file = FileField(label='Upload a File', name='file')
    submit_btn = SubmitField("Upload")
    search = SearchField(label='Search destination (ex. YYZ, Canada, U.S.):')
    search_btn = SubmitField("Search")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pre_search(year, month):
    # make dynamic
    search_term = 'YYZ'
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
        search_term = 'Canada'
    elif is_usa:
        search_term = 'U.S.'
    elif search_term in ['MTY', 'TQO']:
        search_term = 'Mexico - Other'
    elif search_term in ['KIN', 'MBJ']:
        search_term = 'Jamaica'
    else:
        year = datetime.today().year
        month = f'{datetime.today().month:02d}'
    return search(search_term, year, month)


def search(search_term, year, month):
    file_name = f'{year}' + f'{month}'
    destination_to_display = {"Canada": {
        # "country_code": "",
        # "airport_code": "",
        "bracelet_provided": False,
        # "previous_allowance": "",
        # "adjustment": "",
        # "status": True,
        # "percent_change": "",
        "breakfast": "",
        "lunch": "",
        "dinner": "",
        "snack": "",
        "total": ""}
    }
    try:
        with (open(f'{file_name}.json', 'r') as data_file):
            data = json.load(data_file)
            for destination in data:

                if search_term in destination:
                    #destination_label.config(text=destination)
                    if data[destination]['bracelet_provided']:
                        destination_to_display[search_term]["breakfast"] = ''
                        destination_to_display[search_term]["lunch"] = ''
                        destination_to_display[search_term]["dinner"] = ''
                        destination_to_display[search_term]["snack"] = ''
                        destination_to_display[search_term]["total"] = ''
                        destination_to_display[{search_term}]["total"] = 'Bracelet Provided'
                    else:
                        destination_to_display[search_term]["breakfast"] = f'${data[destination]['breakfast']}'
                        destination_to_display[search_term]["lunch"] = f'${data[destination]['lunch']}'
                        destination_to_display[search_term]["dinner"] = f'${data[destination]['dinner']}'
                        destination_to_display[search_term]["snack"] = f'${data[destination]['snack']}'
                        destination_to_display[search_term]["total"] = f'${data[destination]['total']}'
                else:
                    pass
                    destination_to_display[search_term]["breakfast"] = ''
                    destination_to_display[search_term]["lunch"] = ''
                    destination_to_display[search_term]["dinner"] = ''
                    destination_to_display[search_term]["snack"] = ''
                    destination_to_display[search_term]["total"] = ''
                    destination_to_display[search_term]["total"] = 'Not Found'
        return destination_to_display
    except FileNotFoundError:
        print("File not found.")

@app.route("/")
def index():
    expenses_form = ExpensesForm()
    data = pre_search(year, month)
    return render_template("index.html", form=expenses_form, data=data)


@app.route("/", methods=["POST"])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
        #uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename))
        data = read_file_lines(uploaded_file.filename)
        parse(data, year, month)
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
