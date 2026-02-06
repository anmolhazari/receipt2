# Eco Receipt Analyzer

A Python tool to analyze purchase receipts and estimate the carbon footprint associated with each item and the total receipt.

## Features

- Parses receipt text (date, vendor, items, prices, quantities).
- Estimates carbon footprint (kg CO2e) using a customizable emission factors database.
- Provides eco-friendly alternatives for high-emission items.
- Outputs detailed JSON analysis.

## Usage

1. **Install Python**: Ensure you have Python installed.
2. **Prepare Receipt**: Create a text file (e.g., `receipt.txt`) with your receipt content.
3. **Run Analyzer**:
   
   **Windows (using Python Launcher):**
   ```bash
   py main.py receipt.txt
   ```
   
   **macOS / Linux:**
   ```bash
   python3 main.py receipt.txt
   ```

   Or simply run with the default sample:
   ```bash
   py main.py
   ```

## Web Application

You can also run the tool as a web application where you can upload photos of receipts.

1. **Install Dependencies**:
   ```bash
   py -m pip install flask pillow pytesseract
   ```

2. **Install Tesseract OCR**:
   - Download and install Tesseract-OCR for Windows from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
   - Ensure `tesseract.exe` is in your system PATH, or update `ocr_engine.py` with the direct path.

3. **Run Server**:
   ```bash
   py app.py
   ```
   Open http://localhost:5000 in your browser.

## Configuration

- `emission_factors.json`: Database of emission factors by category. You can add more items here to improve accuracy.

## Project Structure

- `app.py`: Web application entry point (Flask).
- `main.py`: CLI entry point.
- `ocr_engine.py`: OCR wrapper using Tesseract.
- `receipt_parser.py`: Logic to parse text receipts.
- `carbon_estimator.py`: Logic to calculate footprints and suggest alternatives.
- `schema.json`: JSON schema for the output.
- `templates/`: HTML templates for the web app.
- `static/`: CSS styles.

