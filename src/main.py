import subprocess
import sys

def run_all():
    # Step 1: Highlight bubbles / prepare outputs
    subprocess.run([sys.executable, "src/extract_multiple_answers.py"], check=True)

    # Step 2: Convert outputs to CSV
    subprocess.run([sys.executable, "src/omr_to_csv.py"], check=True)

if __name__ == "__main__":
    run_all()
