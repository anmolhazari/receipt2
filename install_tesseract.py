import urllib.request
import os
import subprocess
import sys

def install_tesseract():
    url = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    installer_name = "tesseract_installer.exe"
    
    print(f"Downloading Tesseract from {url}...")
    try:
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        with urllib.request.urlopen(req) as response, open(installer_name, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print("Download complete.")
    except Exception as e:
        print(f"Failed to download: {e}")
        return

    print("Installing Tesseract (this may take a minute)...")
    try:
        # Run installer silently
        # /S for silent
        # /D=path to specify path
        install_dir = os.path.join(os.getcwd(), "Tesseract-OCR")
        print(f"Installing to {install_dir}...")
        subprocess.run([installer_name, "/S", f"/D={install_dir}"], check=True)
        print("Installation command finished.")
    except Exception as e:
        print(f"Installation failed: {e}")
    finally:
        if os.path.exists(installer_name):
            os.remove(installer_name)
            print("Installer removed.")

    # Verify installation
    expected_path = os.path.join(os.getcwd(), "Tesseract-OCR", "tesseract.exe")
    if os.path.exists(expected_path):
        print(f"Tesseract successfully installed at {expected_path}")
    else:
        print("Could not find tesseract.exe after installation.")

if __name__ == "__main__":
    install_tesseract()
