import matplotlib.pyplot as plt
import os
from flask import send_file
import os

if not os.path.exists("users.txt"):
    open("users.txt", "w").close()

if not os.path.exists("students.txt"):
    open("students.txt", "w").close()

from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secret123"

# ----------- HELPER FUNCTION -----------

def calculate_grade(avg):
    if avg >= 90:
        return 'A'
    elif avg >= 75:
        return 'B'
    elif avg >= 60:
        return 'C'
    elif avg >= 50:
        return 'D'
    else:
        return 'F'

# ----------- HOME -----------

@app.route('/')
def home():
    return redirect('/login')

# ----------- REGISTER -----------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with open("users.txt", "a") as f:
            f.write(username + "," + password + "\n")

        return redirect('/login')

    return render_template('register.html')

# ----------- LOGIN -----------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with open("users.txt", "r") as f:
            users = f.readlines()

        for user in users:
            u, p = user.strip().split(",")
            if u == username and p == password:
                session['user'] = username
                return redirect('/dashboard')

        return "Invalid Credentials"

    return render_template('login.html')

# ----------- DASHBOARD -----------

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# ----------- ADD STUDENT -----------

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        m1 = int(request.form['m1'])
        m2 = int(request.form['m2'])
        m3 = int(request.form['m3'])

        avg = (m1 + m2 + m3) / 3
        grade = calculate_grade(avg)

        with open("students.txt", "a") as f:
            f.write(f"{name},{m1},{m2},{m3},{avg},{grade}\n")

        return redirect('/view')

    return render_template('add_student.html')

# ----------- VIEW STUDENTS -----------

@app.route('/view')
def view_students():
    students = []
    try:
        with open("students.txt", "r") as f:
            for line in f:
                students.append(line.strip().split(","))
    except:
        pass

    return render_template('view_students.html', students=students)

# ----------- PERFORMANCE -----------

@app.route('/analysis')
def analysis():
    total = 0
    count = 0
    highest = -1
    topper = "No Data"

    try:
        with open("students.txt", "r") as f:
            for line in f:
                data = line.strip().split(",")

                if len(data) < 6:
                    continue

                name, m1, m2, m3, avg, grade = data
                avg = float(avg)

                total += avg
                count += 1

                if avg > highest:
                    highest = avg
                    topper = name

        class_avg = round(total / count, 2) if count > 0 else 0

    except:
        class_avg = 0

    return render_template(
        "analysis.html",
        class_avg=class_avg,
        topper=topper,
        highest=highest
    )


@app.route('/bargraph')
def bargraph():
    names = []
    averages = []

    try:
        with open("students.txt", "r") as f:
            for line in f:
                data = line.strip().split(",")

                if len(data) < 6:
                    continue

                names.append(data[0])          # student name
                averages.append(float(data[4]))  # average marks

        if len(names) == 0:
            return "<h3>No data available</h3>"

        # Create bar graph
        plt.figure()
        plt.bar(names, averages)
        plt.xlabel("Students")
        plt.ylabel("Average Marks")
        plt.title("Student Performance Bar Graph")

        # Create static folder if not exists
        if not os.path.exists("static"):
            os.makedirs("static")

        # Save image
        file_path = "static/bargraph.png"
        plt.savefig(file_path)
        plt.close()

        return f"""
        <h2>Bar Graph</h2>
        <img src="/{file_path}" alt="Bar Graph">
        <br><a href='/dashboard'>Back</a>
        """

    except Exception as e:
        return f"<h3>Error: {str(e)}</h3>"
# ----------- LOGOUT -----------

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')
# ----------- RUN -----------

if __name__ == '__main__':
    app.run(debug=True)