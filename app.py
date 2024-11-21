from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, flash, redirect, url_for, session, send_file
import os
from flask_mail import Mail, Message
from config import Config  # Assuming config.py holds mail configuration
import google.generativeai as genai
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit

app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY","4f973a642c27d5b3ac367e1215b324a7")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model=genai.GenerativeModel('gemini-1.0-pro-latest')

class SymptomForm(FlaskForm):
    name = TextAreaField('What is your name?', validators=[DataRequired()])
    age = TextAreaField('How old are you?', validators=[DataRequired()])
    gender = TextAreaField('What is your gender?', validators=[DataRequired()])
    symptoms = TextAreaField('What are your symptoms?', validators=[DataRequired()])
    start = TextAreaField('When did your symptoms start?', validators=[DataRequired()])
    changes = TextAreaField('Have you experienced any changes in your symptoms over time?', validators=[DataRequired()])
    factors = TextAreaField('Is there anything that makes your symptoms worse or better?', validators=[DataRequired()])
    medications = TextAreaField('Are you currently taking any medications?', validators=[DataRequired()])

def generate_report(name, age, gender, symptoms, start, changes, factors, medications):
    response= model.generate_content(f"provide a detailed report,diagnosis and recommendations based on these information {symptoms},{age},{medications},{start},{changes},{factors},{name}")
    diagnosis_text = response.text
    return diagnosis_text

def create_report_pdf(name, age, gender, symptoms, start, changes, factors, medications, diagnosis):
    pdf_filename = "diagnosis_report.pdf"
    pdf = canvas.Canvas(pdf_filename,pagesize=letter)
    width,height=letter
    y_position = height - 50  # Starting y position
    line_height = 14 
    def draw_wrapped_text(pdf, text, x, y, max_width):
        lines = simpleSplit(text, 'Helvetica', 12, max_width)
        for line in lines:
            pdf.drawString(x, y, line)
            y -= line_height
            if y < 50:  # Check if we need to start a new page
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y = height - 50
        return y
    pdf.setFont("Helvetica", 12)
    y_position = draw_wrapped_text(pdf, f"Patient Name: {name}", 100, y_position, width - 150)
    y_position = draw_wrapped_text(pdf, f"Age: {age}", 100, y_position, width - 150)
    y_position = draw_wrapped_text(pdf, f"Gender: {gender}", 100, y_position, width - 150)
    y_position = draw_wrapped_text(pdf, f"Symptoms: {symptoms}", 100, y_position, width - 150)
    y_position = draw_wrapped_text(pdf, f"Symptom Start: {start}", 100, y_position, width - 150)
    y_position = draw_wrapped_text(pdf, f"Changes: {changes}", 100, y_position, width - 150)
    y_position = draw_wrapped_text(pdf, f"Factors: {factors}", 100, y_position, width - 150)
    y_position = draw_wrapped_text(pdf, f"Medications: {medications}", 100, y_position, width - 150)
    y_position = draw_wrapped_text(pdf, f"Diagnosis: {diagnosis}", 100, y_position, width - 150)
    y_position = draw_wrapped_text(pdf, "Based on these inputs, a preliminary diagnosis suggests that the patient might be experiencing these conditions.", 100, y_position, width - 150)
    y_position = draw_wrapped_text(pdf, "Please consult with a healthcare professional for an accurate diagnosis.", 100, y_position, width - 150)
    pdf.save()
    return pdf_filename

# Rendering loader page
@app.route("/", methods=['GET', 'POST'])
def load():
    return render_template("loader.html")

# Rendering home page
@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template("home.html")

# Rendering about page
@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html")

# Rendering contact page
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    return render_template("contact.html")

data = []

# Endpoint to handle text and store it in the session (chatbot)
@app.route('/form', methods=['GET', 'POST'])
def gemini():
    form = SymptomForm()
    if form.validate_on_submit():
        name = form.name.data
        age = form.age.data
        gender = form.gender.data
        symptoms = form.symptoms.data
        start = form.start.data
        changes = form.changes.data
        factors = form.factors.data
        medications = form.medications.data

        diagnosis = generate_report(name, age, gender, symptoms, start, changes, factors, medications)
        session['diagnosis'] = diagnosis
        session['patient_data'] = {
            "name": name,
            "age": age,
            "gender": gender,
            "symptoms": symptoms,
            "start": start,
            "changes": changes,
            "factors": factors,
            "medications": medications
        }

        return redirect(url_for('generate_pdf'))
    return render_template('form.html', form=form)
@app.route('/generate-pdf')
def generate_pdf():
    diagnosis = session.get('diagnosis')
    patient_data = session.get('patient_data')
    if diagnosis and patient_data:
        pdf_filename = create_report_pdf(
            patient_data['name'], patient_data['age'], patient_data['gender'], patient_data['symptoms'],
            patient_data['start'], patient_data['changes'], patient_data['factors'], patient_data['medications'], diagnosis
        )
        return send_file(pdf_filename, as_attachment=True)
    else:
        flash("No diagnosis found. Please provide symptoms first.", "error")
        return redirect(url_for('gemini'))
@app.route("/gemini", methods=['GET', 'POST'])
def text():

    data = session.get('data', [])

    if request.method == "POST":
        input_text = request.form.get("text")

        if input_text:
            # Using generative AI model to generate content

            response = model.generate_content(input_text)

            text_result = response.text

            data.append({'input': input_text, 'result': text_result})
            session['data'] = data

            return redirect(url_for('text'))

        else:
            flash("Please provide a valid input!", "error")

    return render_template("index.html", data=data[::-1])  # Reverse data for display

# ... Existing routes for logout, sending email (/logout, /send-mail)

if __name__ == '__main__':
    app.run(debug=True)
