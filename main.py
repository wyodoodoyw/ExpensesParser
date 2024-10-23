from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey, select
from flask_wtf import FlaskForm
from wtforms import FileField, SearchField, SelectField, SubmitField
from wtforms.validators import DataRequired
from parser import *
from pre_search import pre_search
from typing import List

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


class YearMonth(Base):
    __tablename__ = 'yearmonth'
    id: Mapped[str] = mapped_column(String, unique=True, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, unique=False)
    month: Mapped[int] = mapped_column(Integer, unique=False)

    destinations: Mapped[List["Destination"]] = relationship(
        back_populates="yearmonth", cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return f'YearMonth (id={self.id!r}, date={self.year!r}-{self.month!r})'


class Destination(Base):
    __tablename__ = 'destination'
    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True)
    destination: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    country_code: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    airport_code: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    bracelet_provided: Mapped[bool] = mapped_column(Boolean, unique=False, nullable=False, default=False)
    prev_allowance: Mapped[str] = mapped_column(String(250), unique=False, nullable=True)
    adjustment: Mapped[str] = mapped_column(String(250), unique=False, nullable=True)
    # status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    percent_change: Mapped[str] = mapped_column(String(250), unique=False, nullable=True)
    breakfast: Mapped[str] = mapped_column(String(250), unique=False, nullable=True)
    lunch: Mapped[str] = mapped_column(String(250), unique=False, nullable=True)
    dinner: Mapped[str] = mapped_column(String(250), unique=False, nullable=True)
    snack: Mapped[str] = mapped_column(String(250), unique=False, nullable=True)
    total: Mapped[str] = mapped_column(String(250), unique=False, nullable=True)

    date_id: Mapped[int] = mapped_column(ForeignKey('yearmonth.id'), unique=False, nullable=True)
    yearmonth: Mapped['YearMonth'] = relationship(back_populates='destinations')

    def __repr__(self) -> str:
        return f'Destination (name={self.destination!r})'


months = {
    '1': 'January',
    '01': 'January',
    '2': 'February',
    '02': 'February',
    '3': 'March',
    '03': 'March',
    '4': 'April',
    '04': 'April',
    '5': 'May',
    '05': 'May',
    '6': 'June',
    '06': 'June',
    '7': 'July',
    '07': 'July',
    '8': 'August',
    '08': 'August',
    '9': 'September',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December',
}

# db_url = f'{year}{datetime.now().month}'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///expenses.db'
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# Create the extension
db = SQLAlchemy(model_class=Base)

# Initialize the app with the extension
db.init_app(app)
Bootstrap5(app)

# Create table schema in the database. Require application context
with app.app_context():
    db.create_all()


def upload():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
        data = read_file_lines(uploaded_file.filename)
        year = uploaded_file.filename[0:4]
        month = uploaded_file.filename[4:6]
        parse(data, year, month)
    return redirect(url_for('index'))


def get_drop_list():
    with app.app_context():
        files_list = []
        list = db.session.scalars(select(YearMonth).order_by(YearMonth.month)).all()
        for i in list:
            files_list.append((f'{i.month} {i.year}', f'{months[str(i.month)]} {i.year}'))
        files_list.append(('upload', 'Upload New File'))
        return files_list


class ExpensesForm(FlaskForm):
    select_date = SelectField(
        label="Select Expenses Month:",
        name='dropdown',
        validators=[DataRequired()],
        choices=get_drop_list()
    )
    submit_btn2 = SubmitField(label='Submit', name='submit_dropdown')
    upload_file = FileField(label='Upload a File', name='file')
    submit_btn = SubmitField(label="Upload", name='upload')
    search = SearchField(label='Search destination (ex. YYZ, Canada, U.S.):')
    search_btn = SubmitField(label="Search", name='search')


@app.route("/", methods=["GET"])
def index():
    expenses_form = ExpensesForm()
    search_query = request.args.get('q')
    year = '2024'
    month = 'October'
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
        return render_template("index.html", form=expenses_form, data=data, year=year, month=month)
    return render_template("index.html", form=expenses_form, data=None, year=year, month=month)


@app.route("/", methods=["POST"])
def upload_file():
    uploaded_file = request.files['file']
    upload_btn = request.form.get('upload')
    dropdown = request.form.get('submit_dropdown')
    search_query = request.form.get('search')
    if upload_btn and uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
        data = read_file_lines(uploaded_file.filename)
        year = uploaded_file.filename[0:4]
        month = uploaded_file.filename[4:6]
        parse(data, year, month)
        return redirect(url_for('index'))
    elif search_query:
        return redirect(url_for('index', q=search_query))
    elif dropdown:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
