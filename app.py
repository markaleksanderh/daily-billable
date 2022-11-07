from os import environ as env
from flask import Flask, render_template

from daily_billable import get_team

app = Flask(__name__)
app.secret_key = env.get('APP_SECRET_KEY')
app.debug = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///daily_billable.db"


from models import db, Employee
from timetastic import get_absences, add_absences
from harvest import add_tracked_entries, get_tracked, tracked_length


db.init_app(app)

date = '2022-11-03'

@app.before_first_request
def initialize_database():

    db.create_all()
    add_team_to_db()
    absences = get_absences(date)
    add_absences(absences)
    
    for i in range(1, 100):
        tracked = get_tracked(date, i)
        length = tracked_length(tracked)
        if length == 0 :
            break
        else:   
            add_tracked_entries(tracked)
    


def add_team_to_db():
    team = get_team('team.txt')

    for e in team:
        employee = Employee.query.filter_by(name=e).first()
        if employee is None:
            new_employee = Employee(
                name = e,
            )
            db.session.add(new_employee)
            db.session.commit()
            print(f'{new_employee} added to db')


@app.route('/')
def index():
    team = Employee.query.all()
    return render_template('index.html', team=team, date=date)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=env.get('PORT', 8008))