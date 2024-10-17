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


def get_drop_list():
    path = 'instance'
    return [f for f in listdir(path) if isfile(join(path, f))]


class ExpensesForm(FlaskForm):
    select_date = SelectField(label="Select Expenses Month:", choices=get_drop_list())
    upload_file = FileField(label='Upload a File', name='file')
    submit_btn = SubmitField(label="Upload", name='upload')
    search = SearchField(label='Search destination (ex. YYZ, Canada, U.S.):')
    search_btn = SubmitField(label="Search", name='search')


# def allowed_file(filename):
#     return '.' in filename and \
#         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# def pre_search(year, month):
#     # make dynamic
#     search_term = 'YYZ'
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
#         search_term = 'Canada'
#     elif is_usa:
#         search_term = 'U.S.'
#     elif search_term in ['MTY', 'TQO']:
#         search_term = 'Mexico - Other'
#     elif search_term in ['KIN', 'MBJ']:
#         search_term = 'Jamaica'
#     else:
#         year = datetime.today().year
#         month = f'{datetime.today().month:02d}'
#     return search(search_term, year, month)


# def search(search_term, year, month):
#     file_name = f'{year}' + f'{month}'
#     destination_to_display = {"Canada": {
#         # "country_code": "",
#         # "airport_code": "",
#         "bracelet_provided": False,
#         # "previous_allowance": "",
#         # "adjustment": "",
#         # "status": True,
#         # "percent_change": "",
#         "breakfast": "",
#         "lunch": "",
#         "dinner": "",
#         "snack": "",
#         "total": ""}
#     }
#     try:
#         with (open(f'{file_name}.json', 'r') as data_file):
#             data = json.load(data_file)
#             for destination in data:
#
#                 if search_term in destination:
#                     #destination_label.config(text=destination)
#                     if data[destination]['bracelet_provided']:
#                         destination_to_display[search_term]["breakfast"] = ''
#                         destination_to_display[search_term]["lunch"] = ''
#                         destination_to_display[search_term]["dinner"] = ''
#                         destination_to_display[search_term]["snack"] = ''
#                         destination_to_display[search_term]["total"] = ''
#                         destination_to_display[{search_term}]["total"] = 'Bracelet Provided'
#                     else:
#                         destination_to_display[search_term]["breakfast"] = f'${data[destination]['breakfast']}'
#                         destination_to_display[search_term]["lunch"] = f'${data[destination]['lunch']}'
#                         destination_to_display[search_term]["dinner"] = f'${data[destination]['dinner']}'
#                         destination_to_display[search_term]["snack"] = f'${data[destination]['snack']}'
#                         destination_to_display[search_term]["total"] = f'${data[destination]['total']}'
#                 else:
#                     pass
#                     destination_to_display[search_term]["breakfast"] = ''
#                     destination_to_display[search_term]["lunch"] = ''
#                     destination_to_display[search_term]["dinner"] = ''
#                     destination_to_display[search_term]["snack"] = ''
#                     destination_to_display[search_term]["total"] = ''
#                     destination_to_display[search_term]["total"] = 'Not Found'
#         return destination_to_display
#     except FileNotFoundError:
#         print("File not found.")


@app.route("/")
def index():
    # print(request.args)
    expenses_form = ExpensesForm()
    search_query = request.args.get('q')
    print(search_query)
    if search_query:
        # data = db.get_or_404(Destination, search_query)
        # data = db.session.execute(db.select(Destination).where(Destination.airport_code == search_query)).one()
        data = Destination.query.first()
        print(f'data: {data}')
    else:
        data = None
    return render_template("index.html", form=expenses_form, data=data)


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
        # data = db.session.execute(db.select(Destination).where(Destination.airport_code == search_btn)).scalar()
        # data = db.get_or_404(Destination, search_query)
        # print(data)
        return redirect(url_for('index', q=search_query))


if __name__ == '__main__':
    app.run(debug=True)
