from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "intellifit_secret"

# 1. DATABASE CONNECTION
# Fix: '_file_' ko '__file__' (double underscore) hona chahiye
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'intellifit.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 2. TABLES KI DESIGN
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# 3. TABLES KO ACTUALLY BANANA
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        n = request.form.get("name")
        e = request.form.get("email")
        p = request.form.get("password")

        # Naya user save karna
        naya_user = User(name=n, email=e, password=p)
        db.session.add(naya_user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        e = request.form.get("email")
        p = request.form.get("password")
        user = User.query.filter_by(email=e, password=p).first()
        if user:
            session["name"] = user.name
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "name" not in session:
        return redirect("/login")
    return render_template("dashboard.html", name=session.get("name"))

@app.route("/bmi", methods=["GET", "POST"])
def bmi():
    if "name" not in session:
        return redirect("/login")

    bmi_result = None
    category = ""

    if request.method == "POST":
        h = float(request.form.get("height"))
        w = float(request.form.get("weight"))

        h_m = h / 100
        bmi_val = round(w / (h_m ** 2), 2)
        bmi_result = bmi_val

        if bmi_val < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi_val <= 24.9:
            category = "Normal"
        else:
            category = "Overweight"

    return render_template("bmi.html", bmi=bmi_result, category=category)

@app.route("/logout")
def logout():
    session.pop("name", None)
    return redirect("/login")
@app.route("/diet")
def diet():
    # Agar banda login hai (Dashboard tak pahunch gaya hai),
    # toh seedha diet page dikhao, koi aur check mat karo.
    if "name" in session:
        return render_template("diet.html")
    else:
        # Agar galti se koi bina login kiye aaye toh hi login par bhejo
        return redirect("/login")

@app.route("/workout")
def workout():
    if "name" in session:
        return render_template("workout.html")
    return redirect("/login")
@app.route("/debug_data")
def debug_data():
    all_users = User.query.all()
    output = ""
    for u in all_users:
        output += f"Name: {u.name}, Email: {u.email} <br>"
    return output if output else "Database khali hai bhai!"

# Fix: "_main_" ko "__main__" (double underscore) karein
if __name__ == "__main__":
    app.run(debug=True, port=5001)