# main.py
import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workflows.parasha_workflow import torah_workflow

if __name__ == "__main__":
    result = torah_workflow.run(input="faith and trust in God")
    print(result)