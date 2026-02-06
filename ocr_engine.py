import os
from PIL import Image
import pytesseract

class OCREngine:
    def __init__(self):
        # Attempt to locate Tesseract executable in common locations
        self._configure_tesseract()

    def _configure_tesseract(self):
        # Check if tesseract is already in PATH
        import shutil
        if shutil.which('tesseract'):
            return

        # Common installation paths on Windows
        common_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            os.path.expanduser(r'~\AppData\Local\Tesseract-OCR\tesseract.exe')
        ]

        for path in common_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"Tesseract found at: {path}")
                return
        
        print("Warning: Tesseract executable not found in common paths. OCR may fail.")

    def extract_text(self, image_path):
        """
        Extracts text from an image file using Tesseract OCR.
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            if "tesseract is not installed" in str(e).lower() or "not found" in str(e).lower():
                return "Error: Tesseract OCR is not installed or not in your PATH. Please install Tesseract-OCR."
            return f"Error processing image: {str(e)}"
