from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QLineEdit, QMessageBox, QHBoxLayout,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os
import json

class MainWindow(QMainWindow):
    def __init__(self, injuries):
        super().__init__()
        self.setWindowTitle("First-Aid App")
        self.resize(800, 600)
        self.injuries = injuries
        self.current_index = 0
        self.favourites = []

        # Main widget and layout
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for injury type...")
        self.search_bar.textChanged.connect(self.filter_list)
        self.layout.addWidget(self.search_bar)

        # Injury list
        self.list_widget = QListWidget()
        self.list_widget.setMaximumWidth(250)
        self.list_widget.currentItemChanged.connect(self.show_steps)
        self.content_layout.addWidget(self.list_widget)

        # Instruction display
        self.instruction = QVBoxLayout()
        self.content_layout.addLayout(self.instruction)
        self.instruction_label = QLabel("Select an injury to see steps.")
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.instruction_label)

        # Injury Graphics
        self.image_graph = QLabel()
        self.image_graph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction.addWidget(self.image_graph)

        # App buttons
        app_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_step)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_step)
        app_layout.addWidget(self.prev_button)
        app_layout.addWidget(self.next_button)
        self.instruction.addLayout(app_layout)

        # Other buttons
        footer_layout = QHBoxLayout()
        self.emergency_button = QPushButton("Emergency")
        self.emergency_button.clicked.connect(self.show_emergency)
        self.like_button = QPushButton("Add To Favourites")
        self.like_button.clicked.connect(self.toggle_like)
        footer_layout.addWidget(self.emergency_button)
        footer_layout.addWidget(self.like_button)
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        footer_layout.addSpacerItem(spacer)
        self.layout.addLayout(footer_layout)
    
        self.populate_list()
        self.apply_styles()

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
