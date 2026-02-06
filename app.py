import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from ocr_engine import OCREngine
from receipt_parser import ReceiptParser
from carbon_estimator import CarbonEstimator

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB max

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Process the file
            ocr = OCREngine()
            extracted_text = ocr.extract_text(filepath)
            
            if extracted_text.startswith("Error"):
                flash(extracted_text)
                return redirect(request.url)
                
            # Parse Text
            parser = ReceiptParser()
            parsed_data = parser.parse(extracted_text)
            
            # Estimate Carbon
            estimator = CarbonEstimator()
            enriched_items = []
            total_footprint = 0.0
            
            for item in parsed_data['items']:
                analysis = estimator.estimate_item(
                    name=item['name'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                enriched_items.append(analysis)
                total_footprint += analysis['carbon_footprint_kg_co2e']
            
            # Identify top contributor
            top_item = max(enriched_items, key=lambda x: x['carbon_footprint_kg_co2e']) if enriched_items else None
            summary = f"Total estimated carbon footprint is {round(total_footprint, 2)} kg CO2e."
            if top_item:
                summary += f" The largest contributor is '{top_item['name']}' with {top_item['carbon_footprint_kg_co2e']} kg CO2e."

            result = {
                "receipt_details": {
                    "vendor": parsed_data['vendor'],
                    "date": parsed_data['date'],
                    "total_price": parsed_data['total_price'],
                    "currency": parsed_data['currency']
                },
                "items": enriched_items,
                "total_carbon_footprint_kg_co2e": round(total_footprint, 2),
                "analysis_summary": summary,
                "raw_text": extracted_text
            }
            
            # Cleanup uploaded file
            try:
                os.remove(filepath)
            except:
                pass

            return render_template('result.html', result=result)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
