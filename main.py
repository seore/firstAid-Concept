import sys
import json
from PyQt6.QtWidgets import QApplication
from ui import MainWindow

def load_injuries(path="data/injuries.json"):
    with open(path, "r") as f:
        return json.load(f)
    
def main():
    app = QApplication(sys.argv)
    injuries = load_injuries()
    window = MainWindow(injuries)
    window.show()

if __name__ == "__main__":
    main()
