import subprocess
import sys

def run_all():
    # Highlight bubbles and save annotated images (Stage 1)
    subprocess.run([sys.executable, "src/process_input_images.py"], check=True)
    # Convert highlighted/annotated images to CSV answers (Stage 2)
    subprocess.run([sys.executable, "src/extract_answers_csv.py"], check=True)

if __name__ == "__main__":
    run_all()
