# Hospital Patient Data Analysis System

A professional academic web application built with Python, Flask, Pandas, Matplotlib, HTML, CSS, Bootstrap and JavaScript.

## Features
- Patient CSV reading
- Missing-value detection and cleaning
- Disease-wise analysis
- Department-wise analysis
- Average age calculation
- Gender and age-group analysis
- Patient search and filtering
- CSV upload
- Cleaned CSV export
- Department bar graph
- Disease distribution pie chart
- Age distribution histogram
- Responsive professional dashboard

## Required CSV columns
PatientID, Name, Age, Gender, Disease, Department

## Installation

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Linux/macOS:
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run:
```bash
python app.py
```

Open:
http://127.0.0.1:5000

## Project flow

CSV -> Flask -> Pandas -> Data Cleaning -> Analysis -> Matplotlib -> Dashboard

## Academic note
This project is intended for educational/demo use. It does not store or process real patient medical records.
