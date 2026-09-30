from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path	
import os

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
GRAPH_FOLDER = BASE_DIR / "static" / "graphs"
DATA_FILE = BASE_DIR / "patients.csv"

UPLOAD_FOLDER.mkdir(exist_ok=True)
GRAPH_FOLDER.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = "hospital-patient-analysis-demo-key"

REQUIRED_COLUMNS = ["PatientID", "Name", "Age", "Gender", "Disease", "Department"]


def load_data():
    df = pd.read_csv(DATA_FILE)
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[REQUIRED_COLUMNS].copy()


def clean_data(df):
    cleaned = df.copy()

    cleaned["Age"] = pd.to_numeric(cleaned["Age"], errors="coerce")
    age_mean = cleaned["Age"].mean()
    if pd.isna(age_mean):
        age_mean = 0
    cleaned["Age"] = cleaned["Age"].fillna(age_mean).round().astype(int)

    for col in ["PatientID", "Name", "Gender", "Disease", "Department"]:
        cleaned[col] = cleaned[col].fillna("Unknown").astype(str).str.strip()
        cleaned.loc[cleaned[col] == "", col] = "Unknown"

    return cleaned


def missing_summary(df):
    return {
        col: int(df[col].isna().sum() + (df[col].astype(str).str.strip() == "").sum())
        for col in REQUIRED_COLUMNS
    }


def generate_graphs(df):
    plt.figure(figsize=(8, 4.8))
    df["Department"].value_counts().sort_values(ascending=False).plot(kind="bar")
    plt.title("Patients by Department")
    plt.xlabel("Department")
    plt.ylabel("Number of Patients")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(GRAPH_FOLDER / "department_bar.png", dpi=150)
    plt.close()

    plt.figure(figsize=(7, 7))
    disease = df["Disease"].value_counts()
    disease.plot(kind="pie", autopct="%1.1f%%", startangle=90, wedgeprops={"linewidth": 1, "edgecolor": "white"})
    plt.title("Disease Distribution")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(GRAPH_FOLDER / "disease_pie.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 4.8))
    plt.hist(df["Age"], bins=8, edgecolor="black")
    plt.title("Age Distribution")
    plt.xlabel("Age")
    plt.ylabel("Number of Patients")
    plt.tight_layout()
    plt.savefig(GRAPH_FOLDER / "age_histogram.png", dpi=150)
    plt.close()


def build_context():
    raw = load_data()
    cleaned = clean_data(raw)
    generate_graphs(cleaned)

    disease_counts = cleaned["Disease"].value_counts()
    department_counts = cleaned["Department"].value_counts()
    gender_counts = cleaned["Gender"].value_counts()

    ages = cleaned["Age"]
    age_groups = pd.cut(
        ages,
        bins=[0, 17, 30, 45, 60, 200],
        labels=["0–17", "18–30", "31–45", "46–60", "61+"],
        include_lowest=True
    ).value_counts().sort_index()

    return {
        "df": cleaned,
        "raw": raw,
        "total_patients": len(cleaned),
        "average_age": round(float(cleaned["Age"].mean()), 1) if len(cleaned) else 0,
        "disease_count": len(disease_counts),
        "department_count": len(department_counts),
        "missing_total": sum(missing_summary(raw).values()),
        "missing": missing_summary(raw),
        "department_data": department_counts.to_dict(),
        "disease_data": disease_counts.to_dict(),
        "gender_data": gender_counts.to_dict(),
        "age_group_data": {str(k): int(v) for k, v in age_groups.to_dict().items()},
        "patients": cleaned.to_dict(orient="records"),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    context = build_context()
    return render_template("dashboard.html", **context)


@app.route("/patients")
def patients():
    context = build_context()
    return render_template("patients.html", **context)


@app.route("/analysis")
def analysis():
    context = build_context()
    return render_template("analysis.html", **context)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("Please select a CSV file.", "danger")
            return redirect(url_for("upload"))

        if not file.filename.lower().endswith(".csv"):
            flash("Only CSV files are supported.", "danger")
            return redirect(url_for("upload"))

        try:
            uploaded = pd.read_csv(file)
            missing_columns = [c for c in REQUIRED_COLUMNS if c not in uploaded.columns]
            if missing_columns:
                flash("Missing required columns: " + ", ".join(missing_columns), "danger")
                return redirect(url_for("upload"))

            uploaded[REQUIRED_COLUMNS].to_csv(DATA_FILE, index=False)
            flash(f"Dataset uploaded successfully: {len(uploaded)} patient records.", "success")
            return redirect(url_for("dashboard"))
        except Exception as exc:
            flash(f"Could not process the file: {exc}", "danger")
            return redirect(url_for("upload"))

    return render_template("upload.html")


@app.route("/download-cleaned")
def download_cleaned():
    df = clean_data(load_data())
    output = UPLOAD_FOLDER / "cleaned_patients.csv"
    df.to_csv(output, index=False)
    return send_file(output, as_attachment=True, download_name="cleaned_patients.csv")


@app.route("/api/summary")
def api_summary():
    context = build_context()
    return jsonify({
        "total_patients": context["total_patients"],
        "average_age": context["average_age"],
        "disease_count": context["disease_count"],
        "department_count": context["department_count"],
        "missing_total": context["missing_total"],
    })


if __name__ == "__main__":
    app.run(debug=True)
