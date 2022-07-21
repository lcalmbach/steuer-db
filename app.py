from flask import Flask, send_from_directory, render_template, request, redirect, url_for, g, flash

from werkzeug.utils import secure_filename
import pdb
import pandas as pd
import os
import datetime
from secrets import token_hex
from queries import qry
import helper
import const as cn
from forms import ProjectForm, ProjectFilterForm, ProjectTeamForm

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"
conn = helper.get_connection()

@app.route("/projekt_detail/<int:prj_id>", methods=["GET"])
def projekt_detail(prj_id):
    sql = f"SELECT * FROM vProjektDetail WHERE AufgabeID = {prj_id}"
    df, ok, err_msg = helper.get_recordset(conn, sql)
    if len(df)>0:
        record = df.iloc[0]
        df_team = get_team_data(prj_id)
        return render_template("projekt_detail.html", prj=dict(record), df_team=df_team)

def get_team_data(prj_id):
    sql = qry['project_team'].format(prj_id)
    df, ok, err_msg = helper.get_recordset(conn, sql)
    return df

@app.route("/projekt_edit/<int:prj_id>", methods=['GET', 'POST'])
def projekt_edit(prj_id):

    def fill_form_from_db():
        df, ok, err_msg = helper.get_recordset(conn, qry['project_detail'].format(prj_id))
        if len(df) > 0:
            record = df.iloc[0]
            form = ProjectForm()
            form.id.data            = record["AufgabeId"]
            form.title.data         = record["Bezeichnung"]
            form.description.data   = record["Bemerkungen"]
            form.project_start.data = record["Datum_Start"]
            form.project_end.data   = record["Datum_Ende"] if record["Datum_Ende"] else None
            form.project_planend.data = record["Datum_Ende_Geplant"]
            form.project_type.data  = record["ProjektTyp"]
            return form
        else: 
            return  None

    def get_team():
        df = get_team_data(prj_id)

        forms = {}
        for i, row in df.iterrows():
            form = ProjectTeamForm()
            form.name.data = row['mitarbeiterid']
            form.role.data = row['rolleid']
            form.remarks.data = row['bemerkungen']
            forms[i]=form
        return df, forms

    def update_aufgabe_sql(form):
        sql = f"""UPDATE Aufgabe SET
            Bezeichnung = '{form.title.data}', 
            Bemerkungen = '{form.description.data}',
            Datum_Start = {'Null' if form.project_start.data == None else "'" + form.project_start.data.strftime(cn.DB_DATE_FORMAT) + "'"},
            Datum_Ende = {'Null' if form.project_end.data == None else "'" + form.project_end.data.strftime(cn.DB_DATE_FORMAT) + "'"},
            Datum_Ende_Geplant = {'Null' if form.project_planend.data == None else "'" + form.project_planend.data.strftime(cn.DB_DATE_FORMAT) + "'"}
            WHERE AufgabeID = {prj_id}
        """
        return sql
            
    def update_project_sql(form):
        return False, 'todo'

    def save_record(form):
        """ 
        called on post
        """
        # data for project is stored in 2 tables: aufgabe and project having a 1:1 relation
        ok, err_msg = helper.execute_cmd(conn, update_aufgabe_sql(form))
        ok, err_msg = helper.execute_cmd(conn, update_project_sql(form))
        conn.commit()
        flash("Project '{}' wurde erfolgreich gespeichert".format(form.title.data), "success")
    
    def delete_record(prj_id:int):
        sql = f"delete from aufgabe where AufgabeID = {prj_id}"
        ok, err_msg = helper.execute_cmd(conn, sql)

    if request.method == 'POST':
        form = ProjectForm(request.form)
        if form.save.data:
            save_record(form)
            team, team_forms = get_team()
            return render_template("projekt_edit.html", form=form, df_team=team, team_forms=team_forms)
        if form.close.data:
            return redirect(url_for("projekte"))
        if form.delete.data:
            delete_record(prj_id)
            flash("Project '{}' wurde erfolgreich gelöscht".format(form.title.data), "success")
            return redirect(url_for("projekte"))

    elif request.method == 'GET':
        team, team_forms = get_team()
        form = fill_form_from_db()
        return render_template("projekt_edit.html", form=form, df_team=team, team_forms=team_forms)


@app.route("/", methods=["GET"])
def home():
    df, ok, err_msg = helper.get_recordset(conn, qry['apps'])
    
    return render_template("home.html", df=df)


@app.route("/projekte", methods=['GET'])
def projekte():
    form = ProjectFilterForm(request.args, meta={"crsf": False}) 
    filter_queries = ""
    # if form.validate():
    if len(request.args) > 1:
        if form.title.data.strip():
            filter_queries += f" AND Bezeichnung like '%{form.title.data}%'"
        if form.leitung.data>0:
            filter_queries += f" AND Verantw_Fachlich_ID = {form.leitung.data}"
        if form.isactive.data != 'alle':
            filter_queries += f" AND istaktiv = '{form.isactive.data}'"
    df, ok, err_msg = helper.get_recordset(conn, qry['project_list'].format(filter_queries))
    return render_template("/projekt_liste.html", df=df, form=form, num_of_records = len(df))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
