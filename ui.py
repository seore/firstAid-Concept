from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QLineEdit, QMessageBox, QHBoxLayout,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import os
import pyttsx3
import json

class MainWindow(QMainWindow):
    def __init__(self, injuries):
        super().__init__()
        self.tss_engine = pyttsx3.init()
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

        self.content_layout = QHBoxLayout()
        self.layout.addLayout(self.content_layout)

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
        self.voice_button = QPushButton("Play Voice")
        self.voice_button.clicked.connect(self.read_current_step)
        app_layout.addWidget(self.prev_button)
        app_layout.addWidget(self.next_button)
        app_layout.addWidget(self.voice_button)
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

    def apply_styles(self):
        self.setStyleSheet(""" 
            QMainWindow { background-color: #f0f4f7; }
            QLabel { font-size: 14pt; color: #333; }
            QListWidget { font-size: 12pt; padding: 5px; }
            QPushButton { background-color: #1976d2; color: white; font-weight: bold; border-radius: 8px; padding: 10px; }
            QPushButton#emergency { background-color: #d32f2f; }
            QLineEdit { padding: 8px; font-size: 12pt; }
        """)
        self.emergency_button.setObjectName("emergency")
    
    def show_steps(self, current, previous=None):
        if current is None:
            self.instruction_label.setText("Select an injury to see steps.")
            self.image_graph.clear()
            return
        name = current.text()
        self.current_index = 0
        self.current_injury = next((i for i in self.injuries if i["name"] == name), None)
        self.update_instructions()
    
    def update_instructions(self):
        if not self.current_injury:
            return
        steps = self.current_injury["steps"]
        if self.current_index >= len(steps):
            self.current_index = len(steps) - 1
        text = f"<b>{self.current_injury['name']} (Step {self.current_index+1}/{len(steps)})</b><br>{steps[self.current_index]}"
        self.instruction_label.setText(text)

        # image display
        img_path = os.path.join("icons", self.current_injury.get("icons", ""))
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path).scaled(300,200, Qt.AspectRatioMode.KeepAspectRatio)
            self.image_graph.setPixmap(pixmap)
        else:
            self.image_graph.clear()

    def read_current_step(self):
        if hasattr(self, "current_injury") and self.current_injury:
            step_text = self.current_injury["steps"][self.current_index]
            self.tss_engine.say(f"{self.current_injury['name']}. Step {self.current_index + 1}. {step_text}")
            self.tss_engine.runAndWait()
            
    def next_step(self):
        if hasattr(self, "current_injury") and self.current_injury:
            if self.current_index < len(self.current_injury["steps"]) - 1:
                self.current_index += 1
                self.update_instructions()
    
    def prev_step(self):
        if hasattr(self, "current_injury") and self.current_injury:
            if self.current_index > 0:
                self.current_index -= 1
                self.update_instructions()

    def filter_list(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def toggle_like(self):
        if not hasattr(self, "current_injury") or not self.current_injury:
            return
        name = self.current_injury["name"]
        if name in self.favourites:
            self.favourites.remove(name)
            self.like_button.setText("Add to Favourites")
        else:
            self.favourites.append(name)
            self.like_button.setText("Remove from Favourites")

    def show_emergency(self):
        QMessageBox.information(self, "Emergency", "Call your local emergency number immediately!")
