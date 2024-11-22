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
model=genai.GenerativeModel('gemini-1.5-flash')

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
    pdf = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    # Define starting position and line height
    y_position = height - 100  # Set initial position lower for the header
    line_height = 14

    # Function to add wrapped text to the PDF with some improvements in text layout
    def draw_wrapped_text(pdf, text, x, y, max_width, font_size=12, bold=False):
        # Apply bold if specified
        if bold:
            pdf.setFont("Helvetica-Bold", font_size)
        else:
            pdf.setFont("Helvetica", font_size)
        
        # Wrap the text and display it
        lines = simpleSplit(text, 'Helvetica', font_size, max_width)
        for line in lines:
            pdf.drawString(x, y, line)
            y -= line_height
            if y < 50:  # Check if we need to start a new page
                pdf.showPage()
                pdf.setFont("Helvetica", font_size)
                y = height - 50
        return y

    # Adding a title or header
    pdf.setFont("Helvetica-Bold", 16)
    y_position = draw_wrapped_text(pdf, "Patient Diagnosis Report", 100, y_position, width - 150, font_size=16, bold=True)

    # Adding Patient Information section
    y_position = draw_wrapped_text(pdf, f"Patient Name: {name}", 100, y_position, width - 150, font_size=12, bold=True)
    y_position = draw_wrapped_text(pdf, f"Age: {age}", 100, y_position, width - 150, font_size=12)
    y_position = draw_wrapped_text(pdf, f"Gender: {gender}", 100, y_position, width - 150, font_size=12)

    # Adding Symptom Information
    y_position = draw_wrapped_text(pdf, "Symptoms:", 100, y_position, width - 150, font_size=12, bold=True)
    y_position = draw_wrapped_text(pdf, f"{symptoms}", 100, y_position, width - 150, font_size=12)
    
    y_position = draw_wrapped_text(pdf, "Symptom Start:", 100, y_position, width - 150, font_size=12, bold=True)
    y_position = draw_wrapped_text(pdf, f"{start}", 100, y_position, width - 150, font_size=12)

    y_position = draw_wrapped_text(pdf, "Changes Over Time:", 100, y_position, width - 150, font_size=12, bold=True)
    y_position = draw_wrapped_text(pdf, f"{changes}", 100, y_position, width - 150, font_size=12)

    y_position = draw_wrapped_text(pdf, "Factors Affecting Symptoms:", 100, y_position, width - 150, font_size=12, bold=True)
    y_position = draw_wrapped_text(pdf, f"{factors}", 100, y_position, width - 150, font_size=12)

    y_position = draw_wrapped_text(pdf, "Medications:", 100, y_position, width - 150, font_size=12, bold=True)
    y_position = draw_wrapped_text(pdf, f"{medications}", 100, y_position, width - 150, font_size=12)

    # Adding Diagnosis Section
    y_position = draw_wrapped_text(pdf, "Diagnosis & Recommendations:", 100, y_position, width - 150, font_size=12, bold=True)
    y_position = draw_wrapped_text(pdf, f"{diagnosis}", 100, y_position, width - 150, font_size=12)

    # Closing the PDF
    pdf.save()

    return pdf_filename


# Rendering loader page
@app.route("/", methods=['GET', 'POST'])
def load():
    print("Loading the loader page...")
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

@app.route("/bmi_calculator", methods=['GET', 'POST'])
def bmi_calculator():
    return render_template("bmi_calculator.html")


@app.route("/telemedicine", methods=['GET', 'POST'])
def telemedicine():
    return render_template("telemedicine.html")


@app.route("/resources", methods=['GET', 'POST'])
def resources():
    return render_template("resourcepage.html")

@app.route("/quiz", methods=['GET', 'POST'])
def quiz():
    return render_template("quiz.html")

@app.route("/chatbot", methods=['GET', 'POST'])
def chatbot():
    return render_template("chatbot.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

data = []

# Endpoint to handle text and store it in the session (chatbot)
@app.route('/form', methods=['GET', 'POST'])
def form():
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
    
def generate_content(input_text):
    predefined_responses = {
        "hello": "Hi there! How can I help you today?",
        "symptoms": "Please describe your symptoms in detail.",
        "thank you": "You're welcome! Feel free to ask if you have more questions.",
    }

    # Simple keyword-based response
    response = predefined_responses.get(input_text.lower(), "I'm not sure about that. Can you ask something else?")
    return response


@app.route("/gemini", methods=['GET', 'POST'])
def gemini():
    data = session.get('data', [])

    if request.method == "POST":
        input_text = request.form.get("text")

        if input_text:
            # Generate response using the generate_content function
            response = generate_content(input_text)

            # Append user input and bot response to session data
            data.append({'input': input_text, 'result': response})
            session['data'] = data

            return redirect(url_for('gemini'))

        else:
            flash("Please provide a valid input!", "error")

    return render_template("gemini.html", data=data[::-1])  # Reverse data for display
# ... Existing routes for logout, sending email (/logout, /send-mail)

if __name__ == '__main__':
    app.run(Debug=True)