from os import read
import chatterbot
from flask import Flask, render_template, request, redirect, url_for, flash, session, escape
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot import filters
from chatterbot.comparisons import levenshtein_distance
from chatterbot.response_selection import get_first_response
import sqlite3 as sql
#from pythainlp import word_tokenize

app = Flask(__name__)
app.secret_key = 'random string'

bot = ChatBot("MyBot",
    filters=[filters.get_recent_repeated_responses],
    logic_adapters=[
    {
        'import_path':'chatterbot.logic.BestMatch',
        "statement_comparison_function": chatterbot.comparisons.levenshtein_distance,
        "response_selection_method": chatterbot.response_selection.get_first_response,
        'default_response': 'ผมขอโทษ ข้อมูลที่ท่านถาม ไม่มีอยู่ในระบบ',
        'maximum_similarity_threshold': 0.90
    }],read_only = False)
    
# trainer = ChatterBotCorpusTrainer(bot)
# trainer.train("document")

#----------------------------------- ChatBot -----------------------------------#
@app.route('/') 
def index():
    return render_template("index.html")

@app.route('/get')
def get_bot_response():
    userText = request.args.get('msg')
    return str(bot.get_response(userText))

#--------------------------------------------------------------------------------#

#---------------------------------- Login ---------------------------------------#
@app.route('/login')
def loginform():
    return redirect(url_for('index'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    username ='admin'
    password = 'admin'
    user_login = request.form.get('username')
    pass_login = request.form.get('password')
    if user_login == username and pass_login == password:
        session['logged_in'] = True
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('logout'))

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        con = sql.connect("db.sqlite3")

        curlist = con.cursor()
        curlist.execute("select * from statement")

        curtag = con.cursor()
        curtag.execute("select * from tag")


        rowslist = len(curlist.fetchall())
        rowstag = len(curtag.fetchall())
        return render_template('./admin/admin.html', rowslist = rowslist, rowstag = rowstag)
#--------------------------------------------------------------------------------#

#-------------------------------- Admin Page ------------------------------------#
@app.route('/list')
def list():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        con = sql.connect("db.sqlite3")
        con.row_factory = sql.Row

        cur = con.cursor()
        cur.execute("select id, text, search_text, in_response_to, search_in_response_to from statement")

        rows = cur.fetchall()
        return render_template('./admin/list.html', rows = rows)

@app.route('/tags')
def tags():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        con = sql.connect("db.sqlite3")
        con.row_factory = sql.Row

        cur = con.cursor()
        cur.execute("select id, name from tag")

        rows = cur.fetchall()
        return render_template('./admin/tag.html', rows = rows)

# ---------------------------------- SQL Func ------------------------------------- #
@app.route('/deleteData', methods=['POST'])
def deleteData():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        con = sql.connect("db.sqlite3")

        cur = con.cursor()
        cur.execute("delete from statement where id=?",[request.form['deleteListData']])

        con.commit()
        return redirect(url_for('list'))

@app.route('/editdata', methods = ['GET','POST'])
def editdata():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        if request.method == 'POST':
            try:
                editID = request.form['Eid']
                editText = request.form['Etext']
                editHyperlink = request.form['Ehyperlink']
                editStext = request.form['Estext']
                editIrt = request.form['Eirt']
                editSirt = request.form['Esirt']

                with sql.connect("db.sqlite3") as con:
                    cur = con.cursor()
                    if request.form.get('Ehyperlink'):
                        url = '<a href="{}">{}</a>'
                        cur.execute("update statement set text = ?, search_text = ?, in_response_to = ?, search_in_response_to = ? where id = ?", (url.format(editHyperlink, editText), editStext, editIrt, editSirt, editID))
                        con.commit()
                    else:
                        cur.execute("update statement set text = ?, search_text = ?, in_response_to = ?, search_in_response_to = ? where id = ?", (editText, editStext, editIrt, editSirt, editID))
                        con.commit()
                    
            except:
                con.rollback()
            
            finally:
                con.close()
                return redirect(url_for('list'))

@app.route('/addtext')
def addtextbot():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        return render_template('./admin/addtext.html')

@app.route('/getaddtext', methods = ['GET','POST'])
def getaddtext():
    if not session.get('logged_in'):
        return redirect(url_for('logout'))
    else:
        if request.method == 'POST':
            try:
                hyperlink = request.form['hyperlink']
                text = request.form['text']
                setext = request.form['search_text']
                inresto = request.form['in_response_to']
                seinresto = request.form['search_in_response_to']

                with sql.connect("db.sqlite3") as con:
                    cur = con.cursor()
                    if request.form.get('hyperlink'):
                        url = '<a href="{}">{}</a>'
                        cur.execute("insert into statement (text, search_text, in_response_to, search_in_response_to) values (?,?,?,?)", (url.format(hyperlink, text), setext, inresto, seinresto))
                        con.commit()
                    else:
                        cur.execute("insert into statement (text, search_text, in_response_to, search_in_response_to) values (?,?,?,?)", (text, setext, inresto, seinresto))
                        con.commit()
                    msg = 'Record successfully added'

            except:
                con.rollback()
                msg = "error in insert operation"

            finally:
                con.close()
                return render_template("./admin/addtext.html", msg = msg)
#--------------------------------------------------------------------------------#

if __name__=="__main__":
    app.run(debug=True)