from flask import Flask, render_template, request
import cv2
import pytesseract
import re
import os

app = Flask(__name__)

# Path to Tesseract executable (adjust accordingly)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist('images[]')
    extracted_numbers = []

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.filename != '':
                image_path = os.path.join('uploads', uploaded_file.filename)
                uploaded_file.save(image_path)

                numbers = extract_numbers_from_image(image_path)
                extracted_numbers.extend(numbers)
        unique_numbers = list(sorted(set(extracted_numbers)))
        return render_template('index.html', numbers=unique_numbers)
    return render_template('index.html')

def preprocess_image(image_path):
    # Read the image using OpenCV
    img = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding to create a binary image
    adaptive_threshold = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

    return adaptive_threshold

def extract_numbers_from_image(image_path):
    preprocessed_img = preprocess_image(image_path)

    # Use Tesseract OCR to extract text from the preprocessed image
    text = pytesseract.image_to_string(preprocessed_img)

    # Find numbers attached to 'BILLB-'
    numbers = re.findall(r'\b\d{4}\b', text)

    return numbers

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
