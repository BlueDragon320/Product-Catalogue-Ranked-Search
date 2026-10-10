from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, BooleanField, IntegerField, DateField, PasswordField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, Email, Optional, EqualTo


class CompanyForm(FlaskForm):
    """Form for managing company details."""
    name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Save Company')

class CompanyAccountForm(FlaskForm):
    """Form for creating a new company and provisioning its initial manager account."""
    name = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=100)])
    admin_username = StringField('Admin Username', validators=[DataRequired(), Length(min=3, max=64)])
    admin_email = StringField('Admin Email', validators=[DataRequired(), Email()])
    admin_password = PasswordField('Initial Password', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Provision Company & Manager Account')


class CategoryForm(FlaskForm):
    """Form for creating and editing categories (FR-2)."""
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Save Category')

class AttributeForm(FlaskForm):
    """Form for managing attributes (FR-4)."""
    name = StringField('Attribute Name', validators=[DataRequired(), Length(min=2, max=100)])
    data_type = SelectField('Data Type', choices=[('numeric', 'Numeric'), ('binary', 'Binary (Yes / No)')], default='numeric')
    min_value = FloatField('Minimum Value', validators=[Optional()])
    max_value = FloatField('Maximum Value', validators=[Optional()])
    weight = FloatField('Weight (%)', validators=[InputRequired(), NumberRange(min=0, max=100)])
    lower_is_better = BooleanField('Lower is Better')
    submit = SubmitField('Save Attribute')

class SponsorForm(FlaskForm):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired()])
    slot_position = IntegerField('Slot Position', validators=[DataRequired(), NumberRange(min=1)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Save Placement')

class UserPasswordResetForm(FlaskForm):
    """Form for platform administrator to reset a company user's password."""
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Update Password')

