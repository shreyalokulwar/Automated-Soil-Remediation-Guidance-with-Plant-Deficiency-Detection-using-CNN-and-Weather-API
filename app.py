from flask import Flask, render_template, request, redirect, url_for, session
import os
import requests

app = Flask(__name__)
app.secret_key = "my_flask_secret"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Weather API
WEATHER_API_KEY = "2346a1e9bd0dca2e1c97fbc80fc9d1fa"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


# ✅ NEW: Reusable Weather Function
def get_weather():
    city = session.get("farmer_location", "Pune")

    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(WEATHER_URL, params=params)
    data = response.json()

    temp = data.get("main", {}).get("temp", 0)
    humidity = data.get("main", {}).get("humidity", 0)
    condition = data.get("weather", [{}])[0].get("description", "N/A")

    return temp, humidity, condition, city


# ✅ Recommendation Logic
def recommend_solution(predicted_class, temp, humidity):

    if predicted_class == "Nitrogen":
        if humidity < 40:
            return "Apply urea fertilizer and increase irrigation"
        else:
            return "Use organic compost"

    elif predicted_class == "Phosphorus":
        if temp < 20:
            return "Apply DAP fertilizer"
        else:
            return "Improve soil drainage"

    elif predicted_class == "Potassium":
        return "Apply potash fertilizer"

    else:
        return "Plant is healthy 🌿"


@app.route("/")
def home():
    return render_template("index.html")


# ✅ Dashboard (unchanged but now uses function)
@app.route("/dashboard")
def dashboard():
    total_analysis = 120
    healthy = 95
    deficiencies = 25

    temp, humidity, condition, city = get_weather()

    return render_template("dashboard.html",
                           total_analysis=total_analysis,
                           healthy=healthy,
                           deficiencies=deficiencies,
                           temperature=temp,
                           condition=condition,
                           city=city)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        location = request.form.get("location")
        session["farmer_location"] = location
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/upload")
def upload():
    return render_template("upload.html")


# ✅ UPDATED PREDICT ROUTE (MAIN FIX)
@app.route("/predict", methods=["POST"])
def predict():
    file = request.files["image"]

    if file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        # 🔹 Example prediction (replace with model later)
        predicted_class = "Nitrogen"

        # ✅ GET WEATHER HERE
        temp, humidity, condition, city = get_weather()

        # ✅ USE WEATHER IN RECOMMENDATION
        recommendation = recommend_solution(predicted_class, temp, humidity)

        return render_template("analysis.html",
                               image=filepath,
                               prediction=predicted_class,
                               recommendation=recommendation,
                               temp=temp,
                               humidity=humidity,
                               condition=condition,
                               city=city)

    return redirect(url_for("upload"))


# ✅ UPDATED ANALYSIS ROUTE
@app.route("/analysis")
def analysis():
    predicted_class = "Phosphorus"

    temp, humidity, condition, city = get_weather()
    recommendation = recommend_solution(predicted_class, temp, humidity)

    return render_template("analysis.html",
                           image="static/images/sample_leaf.png",
                           prediction=predicted_class,
                           recommendation=recommendation,
                           temp=temp,
                           humidity=humidity,
                           condition=condition,
                           city=city)


@app.route("/report")
def report():
    return render_template("report.html")


@app.route("/validation")
def validation():
    return render_template("validation.html")


if __name__ == "__main__":
    app.run(debug=True)