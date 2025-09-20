import argparse
from evaluator import evaluate_omr

def main():
    parser = argparse.ArgumentParser(description="OMR Sheet Evaluator")
    parser.add_argument("-i", "--image", required=True, help="Input OMR image")
    parser.add_argument("-o", "--out", default="outputs", help="Output folder")
    args = parser.parse_args()

    result_paths = evaluate_omr(args.image, args.out)
    print("[DONE] Results saved:", result_paths)

if __name__ == "__main__":
    main()
