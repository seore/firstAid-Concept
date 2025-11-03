from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, injuries):
        super().__init__()
        self.setWindowTitle("First-Aid App")
        self.resize(600, 500)
        self.injuries = injuries

        # Main widget and layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for injury...")
        self.search_bar.textChanged.connect(self.filter_list)
        self.layout.addWidget(self.search_bar)

        # Injury list
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        # Instruction display
        self.instruction_label = QLabel("Select an injury to see steps.")
        self.instruction_label.setWordWrap(True)
        self.layout.addWidget(self.instruction_label)

        # Emergency button
        self.emergency_button = QPushButton("Emergency")
        self.emergency_button.clicked.connect(self.show_emergency)
        self.layout.addWidget(self.emergency_button)

        self.populate_list()

    def populate_list(self):
        self.list_widget.clear()
        for injury in self.injuries:
            item = QListWidgetItem(injury["name"])
            self.list_widget.addItem(item)
        self.list_widget.currentItemChanged.connect(self.show_steps)

    def show_steps(self, current, previous=None):
        if current is None:
            self.instruction_label.setText("Select an injury to see steps.")
            return
        name = current.text()
        steps = next((i["steps"] for i in self.injuries if i["name"] == name), [])
        text = f"<b>{name}</b><br>" + "<br>".join(f"{idx+1}. {s}" for idx, s in enumerate(steps))
        self.instruction_label.setText(text)

    def filter_list(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def show_emergency(self):
        QMessageBox.information(self, "Emergency", "Call your local emergency number immediately!")
