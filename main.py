import os
import sys

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey, select
from parser import *
from pre_search import pre_search
from typing import List
from forms import UploadForm, SearchForm, DeleteForm

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


class YearMonth(Base):
    __tablename__ = 'yearmonth'
    id: Mapped[str] = mapped_column(String, unique=True, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, unique=False)
    month: Mapped[int] = mapped_column(Integer, unique=False)

    destinations: Mapped[List["Destination"]] = relationship(
        back_populates="yearmonth", cascade='all, delete'
    )

    def __repr__(self) -> str:
        return f'YearMonth (id={self.id!r}, date={self.year!r}-{self.month!r})'


class Destination(Base):
    __tablename__ = 'destination'
    id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True, autoincrement=True)
    destination: Mapped[str] = mapped_column(String(10), unique=False, nullable=False)
    country_code: Mapped[str] = mapped_column(String(10), unique=False, nullable=False)
    airport_code: Mapped[str] = mapped_column(String(10), unique=False, nullable=False)
    bracelet_provided: Mapped[bool] = mapped_column(Boolean, unique=False, nullable=False, default=False)
    prev_allowance: Mapped[str] = mapped_column(String(10), unique=False, nullable=True)
    adjustment: Mapped[str] = mapped_column(String(10), unique=False, nullable=True)
    # status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    percent_change: Mapped[str] = mapped_column(String(10), unique=False, nullable=True)
    breakfast: Mapped[str] = mapped_column(String(10), unique=False, nullable=True)
    lunch: Mapped[str] = mapped_column(String(10), unique=False, nullable=True)
    dinner: Mapped[str] = mapped_column(String(10), unique=False, nullable=True)
    snack: Mapped[str] = mapped_column(String(10), unique=False, nullable=True)
    total: Mapped[str] = mapped_column(String(10), unique=False, nullable=True)

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

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI", 'sqlite:///expenses.db')
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')



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
        list_of_yearmonths = db.session.scalars(select(YearMonth).order_by(YearMonth.month)).all()
        for i in list_of_yearmonths:
            files_list.append((f'{i.month} {i.year}', f'{months[str(i.month)]} {i.year}'))
        return files_list





def delete_db():
    print('delete')

@app.route("/", methods=["GET"])
def index():
    now = datetime.now().year
    if q := request.args.get('q'):
        search_query = pre_search(q)
        year = request.args.get('year')
        month = request.args.get('month')
        date_id = db.session.scalar(select(YearMonth).where(YearMonth.year == year and YearMonth.month == month)).id
        # print(date_id)
        # 2024-10-23 16:31:02.360807
        if search_query['type'] == 'airport_code':
            data = db.session.scalar(select(Destination).where(
                Destination.airport_code == search_query['q'],
                Destination.date_id == date_id
            ))
        elif search_query['type'] == 'destination':
            data = db.session.scalar(select(Destination).where(
                Destination.destination == search_query['q'],
                Destination.date_id == date_id

            ))
        elif search_query['type'] == 'country_code':
            data = db.session.scalar(select(Destination).where(
                Destination.country_code == search_query['q'],
                Destination.date_id == date_id
            ))
        else:
            data = None
        return render_template("result.html", data=data, year=year, month=(months[str(month)]), now=now)
    else:
        upload_form = UploadForm()
        # upload_form.validate_on_submit()
        search_form = SearchForm()
        search_form.select_date.default = f'{datetime.now().month} {datetime.now().year}'
        search_form.select_date.choices = get_drop_list()
        # search_form.select_date.default = f'{datetime.now().month} {datetime.now().year}'
        # search_form.validate_on_submit()
        delete_form = DeleteForm()
        # search_form.process()
        return render_template(
            "index.html",
            upload_form=upload_form,
            search_form=search_form,
            delete_form=delete_form,
            now=now
        )


@app.route("/", methods=["POST"])
def index_post():
    now = datetime.now().year
    if 'upload' in request.form:
        uploaded_file = request.files['file']
        year = uploaded_file.filename[0:4]
        month = uploaded_file.filename[4:6]
        # check if the file has already been uploaded
        date_id = db.session.scalar(select(YearMonth).where(
            YearMonth.month == month,
            YearMonth.year == year
        ))
        if not date_id and uploaded_file.filename != '':
            data = read_file_lines(uploaded_file)
            parse(data, year, month)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))

    elif 'search' in request.form:
        search_query = request.form.get('search')
        year = request.form.get('dropdown')[-4:]
        month = re.search(r'\d{1,2}', request.form.get('dropdown'))[0]
        return redirect(url_for('index', q=search_query, year=year, month=month))

    elif 'delete' in request.form:
        list_of_yearmonths = db.session.scalars(select(YearMonth).order_by(YearMonth.month)).all()
        for yearmonth in list_of_yearmonths:
            db.session.delete(yearmonth)
        db.session.commit()
        return redirect(url_for('index'))


if __name__ == '__main__':
    #app.run(debug=True)
    print(os.environ.get('FLASK_KEY'))
    app.run()
