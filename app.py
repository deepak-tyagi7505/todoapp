from flask import Flask,render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import date
import os
import openpyxl
from werkzeug.utils import secure_filename
import csv
import ast
import pandas as pd
import numpy as np

app = Flask(__name__)


#Innitializing the db start
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# app.app_context()

class Todo(db.Model):
    #app.app_context()
    sno=db.Column(db.Integer, primary_key=True)
    taskname=db.Column(db.String(200), nullable=False)
    assignedby=db.Column(db.String(500), nullable=False)
    assigneddate=db.Column(db.Date, default=date.today())
    delevereddate=db.Column(db.Date, nullable=False)
    description=db.Column(db.String(500), nullable=False)
    taskstatus=db.Column(db.String(500), default="Assigned")

    app.app_context()

    def __repr__(delf) -> str:
        return f"sno = {self.sno}|taskname = {self.taskname}|assignedby = {self.assignedby}|assigneddate = {self.assigneddate}|delevereddate = {self.delevereddate}|description = {self.description}|Taskstatus = {self.taskstatus}"
    
with app.app_context():
    db.create_all()



@app.route('/', methods=['GET','POST'])
def home():    
    # todo = Todo(taskname = "Task First", assignedby = "Me",delevereddate=datetime.now() ,description = "Website")
    # db.session.add(todo)
    # db.session.commit()
    # allTodo = Todo.query.all()
    # # print(allTodo)

    todaydate = date.today()
    if request.method == 'POST':
        taskname = request.form['taskname']
        assignedby = request.form['assignedby']
        description = request.form['description']
        delevereddate_str = request.form['delevereddate']
        delevereddate = datetime.strptime(delevereddate_str, '%Y-%m-%d')
        todo = Todo(taskname = taskname, assignedby = assignedby, description = description, delevereddate=delevereddate)
        db.session.add(todo)
        db.session.commit()
    allTodo = Todo.query.all()
    return render_template('home.html',allTodo = allTodo)

@app.route('/assigned')
def assigned():
    # todo = Todo.query.filter(Todo.taskstatus != 'Done').all()
    todo = Todo.query.filter_by(taskstatus="Assigned").all()
    return render_template('assigned.html', todo = todo)


@app.route('/complete')
def complete():
    todo = Todo.query.filter_by(taskstatus="Done").all()
    return render_template('complete.html', todo = todo)

@app.route('/future')
def future():
    todo = Todo.query.filter_by(taskstatus="Future").all()
    return render_template('future.html', todo = todo)

@app.route('/performance')
def performance():
    return render_template('performance.html')

@app.route('/role')
def role():
    return render_template('role.html')

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect ('/')

@app.route('/done/<int:sno>')
def done(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    todo.taskstatus = "Done"
    db.session.add(todo)
    db.session.commit()
    return redirect ('/')

@app.route('/update/<int:sno>',  methods=['GET','POST'])
def update(sno):
    if request.method == 'POST':
        taskname = request.form['taskname']
        assignedby = request.form['assignedby']
        description = request.form['description']
        delevereddate_str = request.form['delevereddate']
        delevereddate = datetime.strptime(delevereddate_str, '%Y-%m-%d')
        assigneddate_str = request.form['assigneddate']
        assigneddate = datetime.strptime(assigneddate_str, '%Y-%m-%d')
        taskstatus = request.form['taskstatus']
        todo = Todo.query.filter_by(sno=sno).first()
        todo.taskname = taskname
        todo.assignedby = assignedby
        todo.description = description
        todo.delevereddate = delevereddate
        todo.assigneddate = assigneddate
        todo.taskstatus = taskstatus
        db.session.add(todo)
        db.session.commit()
        return redirect ('/')

    todo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html', todo = todo)

@app.route('/upload')
def upload():
    return render_template('upload.html')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/processing', methods=['POST'])
def upload_file():
    if 'excelFile' not in request.files:
        return "No file part"

    file = request.files['excelFile']

    if file.filename == '':
        return "No selected file"

    # Save the file to the specified directory
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Process the uploaded file and save data to CSV
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    # Get the header and data from the sheet
    header = [cell.value for cell in sheet[1]]
    data = [list(row) for row in sheet.iter_rows(min_row=2, values_only=True)]

    # Save data to CSV
    csv_filename = os.path.splitext(filename)[0] + '.csv'
    csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
    with open(csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header)
        csv_writer.writerows(data)
    if os.path.exists(file_path):
        os.remove("uploads/Try_File.xlsx")

    return render_template('extraction.html')

@app.route('/process', methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        eninput = request.form['enterinput']
        print(eninput)
        print(type(eninput))
        
        # Corrected line to create a tuple with a single element
        cntnsini = ast.literal_eval(f"({eninput})")
    
        print(cntnsini)
        print(type(cntnsini))
        
        data = pd.read_csv("uploads/Try_File.csv")
        data1 = pd.DataFrame(data)
        data1['URL_Category_2'] = 'Others'  # Default category

        # Check if the URL contains certain patterns and update the category
        cntns = cntnsini
        for itm in cntns:
            data1.loc[data1['Urls'].str.contains(itm), 'URL_Category_2'] = itm
        
        df = pd.DataFrame(data1)
        df.to_csv('static/FinalOutput.csv', index=False)
        return render_template('download.html')
if __name__ == "__main__":
    app.run()


# add filteration in assignedby
# status
