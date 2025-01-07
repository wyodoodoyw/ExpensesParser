from datetime import datetime
from flask import Flask, render_template
from pre_search import pre_search
from forms import UploadForm, SearchForm, DeleteForm
from setup import *

app = Flask(__name__)
#
#
# # CREATE DB
# class Base(DeclarativeBase):
#     pass
#
#
# class YearMonth(Base):
#     __tablename__ = 'yearmonth'
#     id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True, autoincrement=True)
#     year: Mapped[int] = mapped_column(Integer, unique=False)
#     month: Mapped[int] = mapped_column(Integer, unique=False)
#
#     destinations: Mapped[List["Destination"]] = relationship(
#         back_populates="yearmonth", cascade='all, delete'
#     )
#
#     def __repr__(self) -> str:
#         return f'YearMonth (id={self.id!r}, date={self.year!r}-{self.month!r})'
#
#
# class Destination(Base):
#     __tablename__ = 'destination'
#     id: Mapped[int] = mapped_column(Integer, unique=True, primary_key=True, autoincrement=True)
#     destination: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
#     country_code: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
#     airport_code: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
#     bracelet_provided: Mapped[bool] = mapped_column(Boolean, unique=False, nullable=False, default=False)
#     prev_allowance: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
#     adjustment: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
#     # status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
#     percent_change: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
#     breakfast: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
#     lunch: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
#     dinner: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
#     snack: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
#     total: Mapped[str] = mapped_column(String(100), unique=False, nullable=True)
#
#     date_id: Mapped[int] = mapped_column(ForeignKey('yearmonth.id'), unique=False, nullable=True)
#     yearmonth: Mapped['YearMonth'] = relationship(back_populates='destinations')
#
#     def __repr__(self) -> str:
#         return f'Destination (name={self.destination!r})'


# months = {
#     '1': 'January',
#     '01': 'January',
#     '2': 'February',
#     '02': 'February',
#     '3': 'March',
#     '03': 'March',
#     '4': 'April',
#     '04': 'April',
#     '5': 'May',
#     '05': 'May',
#     '6': 'June',
#     '06': 'June',
#     '7': 'July',
#     '07': 'July',
#     '8': 'August',
#     '08': 'August',
#     '9': 'September',
#     '09': 'September',
#     '10': 'October',
#     '11': 'November',
#     '12': 'December',
# }

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI", 'sqlite:///expenses.db')
# # app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
# app.config['SECRET_KEY'] = 'secretk3y'


# # Create the extension
# db = SQLAlchemy(model_class=Base)
# # Initialize the app with the extension
# db.init_app(app)
# Bootstrap5(app)
#
# # Create table schema in the database. Require application context
# with app.app_context():
#     db.create_all()

# display_year = None
# display_month = None
#
#
# def get_pdf_content_lines(file):
#     # pdf --> lines
#     pdf_reader = PdfReader(file)
#     for page in pdf_reader.pages:
#         for line in page.extract_text().splitlines():
#             yield line
#
#
# def read_file_lines(path):
#     # lines --> array of strings
#     file_as_lines = []
#     for line in get_pdf_content_lines(path):
#         file_as_lines.append(line)
#     # Beijing (PEK) CN PEK 246.42$     $0.00 *No Change 0.0% $49.93 $56.94 $108.29 $31.26 246.42 $
#     # Havana (HAV) CU HAV 122.36$     -$0.51 -0.41% $24.56 $27.81 $55.09 $14.39 121.85 $
#     return file_as_lines
#
#
# def find_start_line(data):
#     # locate last line of header/column labels
#     for i in range(0, len(data)):
#         if "AllowanceAdjustment" in data[i]:
#             return i + 1
#
#
# def find_end_line(data):
#     # locate last line in pdf
#     return [idx for idx, s in enumerate(data) if 'Zurich' in s][0] + 1
#
#
# def parse(data, year, month):
#     new_entry = YearMonth(
#         year=year,
#         month=month,
#         destinations=[]
#     )
#     for i in range(find_start_line(data), find_end_line(data)):
#         new_destination = Destination()
#
#         line = data[i]
#
#         if 'Canada' in line:
#             new_destination.destination = 'Canada'
#         elif 'Jamaica' in line:
#             new_destination.destination = 'Jamaica'
#         elif 'Mexico - Other' in line:
#             new_destination.destination = 'Mexico'
#         elif 'U.S.' in line:
#             new_destination.destination = 'U.S.'
#         else:
#             dest_list = re.findall(r'[A-Z]{3}\)', line)
#             last_index_destination = line.index(dest_list[len(dest_list) - 1]) + 5
#             new_destination.destination = line[0:last_index_destination]
#
#         line = line[len(new_destination.destination):]
#         new_destination.country_code = re.findall(r'[A-Z]{2}', line)[0]
#         # station column could be Airport code (ex. ALG) or * for multiple
#         if re.search(r'[A-Z]{3}', line):
#             new_destination.airport_code = re.findall(r'[A-Z]{3}', line)[0]
#         else:
#             new_destination.airport_code = '*'
#         # destinations can be bracelet or per diem
#         if '$' not in line:
#             new_destination.bracelet_provided = True
#             new_destination.prev_allowance = None
#             new_destination.adjustment = None
#             new_destination.percent_change = None
#             new_destination.breakfast = None
#             new_destination.lunch = None
#             new_destination.dinner = None
#             new_destination.snack = None
#             new_destination.total = None
#         else:
#             new_destination.bracelet_provided = False
#             unprocessed_price_list = re.findall(r'-?\$?\d{1,3}\.\d{1,2}%?', line)
#             price_list = []
#             for j in unprocessed_price_list:
#                 j = j.replace('$', '')
#                 price_list.append(j)
#             new_destination.prev_allowance = price_list[0]
#             new_destination.adjustment = price_list[1]
#             new_destination.percent_change = re.findall(r'-?\d{1,2}\.\d{1,2}%', line)[0]
#             new_destination.breakfast = price_list[3]
#             new_destination.lunch = price_list[4]
#             new_destination.dinner = price_list[5]
#             new_destination.snack = price_list[6]
#             new_destination.total = price_list[7]
#
#         if 'Zurich' in new_destination.destination:
#             new_destination.airport_code = '*'
#
#         new_entry.destinations.append(new_destination)
#
#         with app.app_context():
#             db.session.add(new_destination)
#     with app.app_context():
#         db.session.add(new_entry)
#         db.session.commit()
#
#
# def upload():
#     uploaded_file = request.files['file']
#     if uploaded_file.filename != '':
#         uploaded_file.save(uploaded_file.filename)
#         data = read_file_lines(uploaded_file.filename)
#         year = uploaded_file.filename[0:4]
#         month = uploaded_file.filename[4:6]
#         parse(data, year, month)
#     return redirect(url_for('index'))
#
#
# def get_drop_list():
#     with app.app_context():
#         files_list = []
#         list_of_yearmonths = db.session.scalars(select(YearMonth).order_by(YearMonth.month)).all()
#         for i in list_of_yearmonths:
#             files_list.append((f'{i.month} {i.year}', f'{months[str(i.month)]} {i.year}'))
#         return files_list


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
        search_form = SearchForm()
        search_form.select_date.default = f'{datetime.now().month} {datetime.now().year}'
        search_form.select_date.choices = get_drop_list()
        delete_form = DeleteForm()
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
    app.run(debug=False)
