from flask_wtf import FlaskForm
from wtforms import FileField, SearchField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class UploadForm(FlaskForm):
    upload_file = FileField(label='Upload a File', name='file')
    submit_btn = SubmitField(label="Upload", name='upload')


class SearchForm(FlaskForm):
    select_date = SelectField(
        label="Select Expenses Month:",
        name='dropdown',
        validators=[DataRequired()],
        # choices=get_drop_list()
    )
    search = SearchField(
        label='Search by airport code, city, or country (ex. YYZ, Canada, U.S.):',
        validators=[DataRequired(), Length(min=1, message='Please include a search query.')]
    )
    search_btn = SubmitField(label="Search", name='search')


class DeleteForm(FlaskForm):
    delete_btn = SubmitField(label="Delete", name='delete', id='delete')