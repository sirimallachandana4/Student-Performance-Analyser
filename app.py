from flask import Flask, render_template, request, redirect, session
from database import db, User, Student
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "student123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ----------------------------
# Grade Calculator
# ----------------------------
def calculate_grade(avg):
    if avg >= 90:
        return "A"
    elif avg >= 75:
        return "B"
    elif avg >= 60:
        return "C"
    elif avg >= 50:
        return "D"
    else:
        return "F"


# ----------------------------
# HOME
# ----------------------------
@app.route("/")
def home():
    return redirect("/login")


# ----------------------------
# REGISTER
# ----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user:
            return "Username Already Exists"

        new_user = User(
            username=username,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ----------------------------
# LOGIN
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session["user"] = username

            return redirect("/dashboard")

        return "Invalid Credentials"

    return render_template("login.html")


# ----------------------------
# LOGOUT
# ----------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# ----------------------------
# DASHBOARD
# ----------------------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    total = Student.query.count()

    students = Student.query.all()

    class_avg = 0
    topper = "No Data"

    if total > 0:

        class_avg = round(
            sum(s.average for s in students) / total,
            2
        )

        top = max(students, key=lambda x: x.average)

        topper = top.name

    return render_template(
        "dashboard.html",
        total=total,
        class_avg=class_avg,
        topper=topper
    )


# ----------------------------
# ADD STUDENT
# ----------------------------
@app.route("/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]

        m1 = int(request.form["m1"])

        m2 = int(request.form["m2"])

        m3 = int(request.form["m3"])

        avg = round((m1 + m2 + m3) / 3, 2)

        grade = calculate_grade(avg)

        student = Student(
            name=name,
            m1=m1,
            m2=m2,
            m3=m3,
            average=avg,
            grade=grade
        )

        db.session.add(student)

        db.session.commit()

        return redirect("/view")

    return render_template("add_student.html")


# ----------------------------
# VIEW STUDENTS
# ----------------------------
@app.route("/view")
def view_students():

    students = Student.query.all()

    return render_template(
        "view_students.html",
        students=students
    )


# ----------------------------
# SEARCH
# ----------------------------
@app.route("/search")
def search():

    keyword = request.args.get("keyword", "")

    students = Student.query.filter(
        Student.name.contains(keyword)
    ).all()

    return render_template(
        "view_students.html",
        students=students
    )


# ----------------------------
# DELETE
# ----------------------------
@app.route("/delete/<int:id>")
def delete_student(id):

    student = Student.query.get(id)

    if student:

        db.session.delete(student)

        db.session.commit()

    return redirect("/view")


# ----------------------------
# ANALYSIS
# ----------------------------
@app.route("/analysis")
def analysis():

    students = Student.query.all()

    if len(students) == 0:

        return render_template(
            "analysis.html",
            class_avg=0,
            topper="No Data",
            highest=0
        )

    total = sum(s.average for s in students)

    class_avg = round(total / len(students), 2)

    top = max(students, key=lambda x: x.average)

    return render_template(
        "analysis.html",
        class_avg=class_avg,
        topper=top.name,
        highest=top.average
    )


# ----------------------------
# BAR GRAPH
# ----------------------------
@app.route("/bargraph")
def bargraph():

    students = Student.query.all()

    if len(students) == 0:

        return "No Student Data"

    names = [s.name for s in students]

    averages = [s.average for s in students]

    plt.figure(figsize=(8,5))

    plt.bar(names, averages, color="royalblue")

    plt.xlabel("Students")

    plt.ylabel("Average")

    plt.title("Student Performance")

    if not os.path.exists("static/images"):

        os.makedirs("static/images")

    plt.savefig("static/images/bargraph.png")

    plt.close()

    return render_template("graph.html")


# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":

    app.run(debug=True)