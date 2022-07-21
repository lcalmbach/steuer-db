from email.policy import default
from flask_wtf import FlaskForm
from wtforms import FileField, IntegerField, StringField, TextAreaField, SubmitField, SelectField, DecimalField, DateField
from wtforms.validators import InputRequired, DataRequired, Length
import helper
import const as cn
from queries import qry

conn = helper.get_connection()

def emp_list():
    df, ok, err_msg = helper.get_recordset(conn, qry['ma_liste'])
    emps = list(zip(list(df['id']), list(df['name'])))
    return [(-1,'---')] + emps
    
class ProjectForm(FlaskForm):
    def project_type_list():
        query = qry['lookup_list'].format(cn.LU_PROJECT_TYPE)
        df, ok, err_msg = helper.get_recordset(conn,query)
        return list(zip(list(df['id']), list(df['name'])))

    id = IntegerField("Projekt-Nummer",validators=[], default=0)
    title = StringField("Bezeichnung", validators=[InputRequired("Input is required!"), DataRequired("Data is required!"), Length(min=5, max=500, message="Input must be between 5 and 500 characters long")])
    project_type = SelectField("Typ", coerce=int, choices=[])
    description = TextAreaField("Beschreibung", validators=[InputRequired("Input is required!"), DataRequired("Data is required!"), Length(min=5, max=1000, message="Input must be between 5 and 1000 characters long")])
    project_start = DateField("Projekt Beginn", format=cn.DB_DATE_FORMAT, validators=[])
    project_end = DateField("Projekt Ende", format=cn.DB_DATE_FORMAT, validators=[])
    project_planend = DateField("Projekt Plan-Ende", format=cn.DB_DATE_FORMAT, validators=[])

    query = qry['lookup_list'].format(cn.LU_PROJECT_TYPE)
    df, ok, err_msg = helper.get_recordset(conn,query)
    project_type = SelectField("Typ", coerce=int, choices=project_type_list())

    save = SubmitField("Speichern")
    close = SubmitField("Schliessen")
    delete = SubmitField("Löschen")
    

class ProjectTeamForm(FlaskForm):
    def role_types():
        query = qry['lookup_list'].format(cn.LU_PROJECT_MEMBER_ROLE)
        df, ok, err_msg = helper.get_recordset(conn, query)
        return list(zip(list(df['id']), list(df['name'])))
    
    name = SelectField("Name", coerce=int, choices=emp_list())
    remarks = TextAreaField("Bemerkungen")
    role = SelectField("Typ", coerce=int, choices=role_types())
    
    save      = SubmitField("Speichern")
    delete    = SubmitField("Löschen")


class ProjectFilterForm(FlaskForm):
    title       = StringField("Title")
    leitung     = SelectField("Leitung", coerce=int, choices=emp_list())
    isactive    = SelectField("Projekt aktiv", choices=['ja', 'nein', 'alle'])
    submit      = SubmitField("Filter")