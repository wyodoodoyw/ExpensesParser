from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Boolean
from flask_wtf import FlaskForm
from wtforms import DateField, FileField, SearchField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from os import listdir
from os.path import isfile, join
from parser import *
import requests

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///202410.db"
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# Create the extension
db = SQLAlchemy(model_class=Base)

# Initialize the app with the extension
db.init_app(app)
Bootstrap5(app)

year = datetime.today().year
month = f'{datetime.today().month:02d}'


# CREATE TABLE
class Destination(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination: Mapped[str] = mapped_column(String(250), nullable=False)
    country_code: Mapped[str] = mapped_column(String(250), nullable=False)
    airport_code: Mapped[str] = mapped_column(String(250), nullable=False)
    bracelet_provided: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    prev_allowance: Mapped[str] = mapped_column(String(250), nullable=True)
    adjustment: Mapped[str] = mapped_column(String(250), nullable=True)
    # status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    percent_change: Mapped[str] = mapped_column(String(250), nullable=True)
    breakfast: Mapped[str] = mapped_column(String(250), nullable=True)
    lunch: Mapped[str] = mapped_column(String(250), nullable=True)
    dinner: Mapped[str] = mapped_column(String(250), nullable=True)
    snack: Mapped[str] = mapped_column(String(250), nullable=True)
    total: Mapped[str] = mapped_column(String(250), nullable=True)

    def __repr__(self):
        return f'<Destination {self.destination}>'


# Create table schema in the database. Require application context
with app.app_context():
    db.create_all()


def upload():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
        data = read_file_lines(uploaded_file.filename)
        parse(data, year, month)
    return redirect(url_for('index'))


def get_drop_list():
    files_list = []
    path = 'instance'
    # files_list = [f for f in listdir(path) if isfile(join(path, f))]
    for file in listdir(path):
        if isfile(join(path, file)):
            files_list.append((file, file))
    files_list.append((None, 'Upload New File'))
    return files_list


class ExpensesForm(FlaskForm):
    select_date = SelectField(label="Select Expenses Month:", choices=get_drop_list())
    upload_file = FileField(label='Upload a File', name='file')
    submit_btn = SubmitField(label="Upload", name='upload')
    search = SearchField(label='Search destination (ex. YYZ, Canada, U.S.):')
    search_btn = SubmitField(label="Search", name='search')


def pre_search(search_term):
    usa_airports = ['SFO', 'LAX', 'SAN', 'PSP', 'SMF',
                    'SNA', 'MCO', 'TPA', 'FLL', 'PBI',
                    'MIA', 'RSW', 'SRQ', 'HNL', 'KOA',
                    'OGG', 'LAS', 'ORD', 'DTW', 'MPS',
                    'STL', 'CVG', 'CLE', 'CMH', 'IND',
                    'EWR', 'BOS', 'LGA', 'PHL', 'PIT',
                    'IAD', 'BDL', 'ATL', 'AUS', 'DFW',
                    'IAH', 'BNA', 'MSY', 'CHS', 'DEN',
                    'PHX', 'SEA', 'SLC', 'PDX', 'ANC',
                    'U.S.A', 'US', 'USA']
    hawaii_airports = ['LIH', 'Lihue', 'OGG', 'Maui']
    can_airports = ['YYC', 'YEG', 'YFC', 'YQX', 'YHZ',
                    'YUL', 'YOW', 'YQB', 'YYT', 'YYZ',
                    'YVR', 'YYJ', 'YWG', 'YDF', 'YXX',
                    'YYR', 'ZBF']
    if search_term in usa_airports and search_term not in hawaii_airports:
        return {'type': 'destination', 'q': 'U.S.'}
    elif search_term in ['BNE', 'MEL', 'Brisbane', 'Melbourne', 'Australia']:
        return {'type': 'country', 'q': 'AU'}
    elif search_term in ['BRU', 'LGG', 'Brussels', 'Liège', 'Liege', 'Belgium']:
        return {'type': 'country', 'q': 'BE'}
    elif search_term in ['DEL', 'BOM', 'Delhi', 'Mumbai', 'Bombay', 'India']:
        return {'type': 'country', 'q': 'IN'}
    elif search_term in ['DUB', 'SNN', 'Dublin', 'Shannon', 'Ireland']:
        return {'type': 'country', 'q': 'IE'}
    elif search_term in ['FRA', 'MUC', 'TXL', 'Frankfort', 'Munich', 'Berlin', 'Germany']:
        return {'type': 'country', 'q': 'DE'}
    elif search_term in ['Hong Kong', 'HK', 'HKG']:
        return {'type': 'country', 'q': 'HK'}
    elif search_term in ['KIN', 'MBJ']:
        return {'type': 'country', 'q': 'JM'}
    elif search_term in ['LIS', 'OPO', 'Lisbon', 'Porto', 'Portugal']:
        return {'type': 'country', 'q': 'PT'}
    elif search_term in ['LHR', 'LGW', 'London', 'Heathrow', 'Gatwick', 'England', 'UK', 'U.K.']:
        return {'type': 'country', 'q': 'GB'}
    elif search_term in ['MAD', 'BCN', 'Madrid', 'Barcelona', 'Spain']:
        return {'type': 'country', 'q': 'ES'}
    elif search_term in ['MTY', 'TQO']:
        return {'type': 'country', 'q': 'MX'}
    elif search_term in ['NRT', 'HND', 'KIX', 'Narita', 'Haneda', 'Osaka', 'Tokyo', 'Japan']:
        return {'type': 'country', 'q': 'JP'}
    elif search_term in ['CDG', 'LYS', 'NCE', 'TLS', 'Paris', 'Lyon', 'Nice', 'Toulouse', 'France']:
        return {'type': 'country', 'q': 'FR'}
    elif search_term in ['FCO', 'MXP', 'VCE', 'Rome', 'Milan', 'Venice', 'Italy']:
        return {'type': 'country', 'q': 'IT'}
    elif search_term in ['GRU', 'GIG', 'Sao Paulo', 'Rio de Janeiro', 'Rio', 'Brazil']:
        return {'type': 'country', 'q': 'BR'}
    elif search_term in ['SIN', 'QPG', 'Singapore']:
        return {'type': 'country', 'q': 'SG'}
    elif search_term in ['ZRH', 'GVA', 'BSL', 'Zurich', 'Geneva', 'Basel', 'Swiss', 'Switzerland']:
        return {'type': 'country', 'q': 'CH'}
    elif re.findall(r'Y[A-Z]{2}', search_term) or search_term in ['Canada']:
        return {'type': 'destination', 'q': 'Canada'}
    elif re.search(r'[A-Z]{3}', search_term):
        return {'type': 'airport_code', 'q': search_term}
    else:
        return {'type': 'destination', 'q': search_term}
        # year = datetime.today().year
        # month = f'{datetime.today().month:02d}'


@app.route("/", methods=["GET"])
def index():
    expenses_form = ExpensesForm()
    search_query = request.args.get('q')
    if search_query:
        search_query = pre_search(search_query)
        if search_query['type'] == 'airport_code':
            data = Destination.query.filter_by(airport_code=search_query['q']).first()
        elif search_query['type'] == 'destination':
            data = Destination.query.filter_by(destination=search_query['q']).first()
        elif search_query['type'] == 'country':
            data = Destination.query.filter_by(country_code=search_query['q']).first()
        else:
            data = None
        return render_template("index.html", form=expenses_form, data=data)
    return render_template("index.html", form=expenses_form, data=None)



@app.route("/", methods=["POST"])
def upload_file():
    uploaded_file = request.files['file']
    upload_btn = request.form.get('upload')
    search_query = request.form.get('search')
    if upload_btn and uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
        data = read_file_lines(uploaded_file.filename)
        parse(data, year, month)
        return redirect(url_for('index'))
    elif search_query:
        return redirect(url_for('index', q=search_query))


if __name__ == '__main__':
    app.run(debug=True)
