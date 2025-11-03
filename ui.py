from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QLineEdit, QMessageBox, QHBoxLayout,
    QSpacerItem, QSizePolicy, QFrame, QToolButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont, QIcon
import os
import pyttsx3
import json

APP_BG = "#eef3f6"
CARD_BG = "#ffffff"
PRIMARY = "#2b7cff"
EMERGENCY_COLOR = "#e53935"
UI_ACCENT = "#4caf50"
TEXT_COLOR = "#222831"
MUTED = "#6b7280"
IMG_PLACEHOLDER = "icons/place.png"

class MainWindow(QMainWindow):
    def __init__(self, injuries):
        super().__init__()
        self.tss_engine = pyttsx3.init()
        self.setWindowTitle("First-Aid App")
        self.resize(1000, 650)
        self.injuries = injuries
        self.current_index = 0
        self.favourites = []

        # Widgets and layouts
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        header = QHBoxLayout()
        title_label = QLabel("First Aid")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {TEXT_COLOR};")
        header.addWidget(title_label)
        header.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        about_button = QToolButton()
        about_button.setText("About")
        about_button.clicked.connect(self.display_about) 
        header.addWidget(about_button)

        self.layout.addLayout(header)

        # Search bar and Main Display
        top_display = QHBoxLayout()
        self.layout.addLayout(top_display, stretch=1)

        # Left Display - Injuries
        left_display = QVBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for injury type...")
        self.search_bar.textChanged.connect(self.filter_list)
        self.search_bar.setFixedHeight(40)
        self.layout.addWidget(self.search_bar)
        
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(8)
        self.list_widget.setUniformItemSizes(False)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.currentItemChanged.connect(self.show_steps)
        left_display.addWidget(self.list_widget)
        top_display.addLayout(left_display, stretch=33)
    
        # Right Display - Injuries Details
        right_display = QVBoxLayout()
        displayCard = QFrame()
        displayCard.setObjectName("Display card")
        display_layout = QVBoxLayout()
        displayCard.setLayout(display_layout)
        display_layout.setContentsMargins(10,10,10,10)
        right_display.addWidget(displayCard, stretch=1)

        # Favourites Display Card
        title_r = QHBoxLayout()
        self.injury_title = QLabel("Choose an injury")
        self.injury_title.setFont(QFont("Segoe UI", 16, QFont.Weight.DemiBold))
        title_r.addWidget(self.injury_title)
        title_r.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.like_button = QPushButton("Favourite")
        self.like_button.setCheckable(True)
        self.like_button.clicked.connect(self.click_like)
        title_r.addWidget(self.like_button)
        display_layout.addLayout(title_r)

        # Placeholder Display
        self.img_label = QLabel()
        self.img_label.setFixedHeight(250)
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_layout.addWidget(self.img_label)

        # Instruction Display
        self.instruction = QLabel("Select an injury to see steps.")
        self.instruction.setWordWrap(True)
        self.instruction.setFont(QFont("Segoe UI", 12))
        display_layout.layout.addWidget(self.instruction)

        # App buttons
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.clicked.connect(self.prev_step)
        self.next_button = QPushButton("Next  ▶")
        self.next_button.clicked.connect(self.next_step)
        self.voice_button = QPushButton("Play Voice")
        self.voice_button.clicked.connect(self.read_current_step)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.voice_button)
        nav_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        display_layout.addLayout(nav_layout)

        # Other App Buttons
        footer_layout = QHBoxLayout()
        self.emergency_button = QPushButton("🚨 Emergency")
        self.emergency_button.clicked.connect(self.show_emergency)
        self.emergency_button.setStyleSheet(f"background-color: {EMERGENCY_COLOR}; color: white; font-weight: bold;")
        self.display_favs = QPushButton("★ Favourites")
        self.display_favs.clicked.connect(self.show_favs)
        footer_layout.addWidget(self.emergency_button)
        footer_layout.addWidget(self.display_favs)
        footer_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        display_layout.addLayout(footer_layout)
    
        top_display.addLayout(right_display, stretch=60)

        self.populate_list()
        self.apply_styles()

    # ---------------------  Lists -----------------------
    def populate_list(self):
        self.list_widget.clear()
        for injury in self.injuries:
            name = injury.get("name", "unknown")
            item = QListWidgetItem(name)
            img_title = injury.get("icon", "")
            img_path = os.path.join("icons", img_title) if img_title else ""
            if img_path and os.path.exists(img_path):
                icon = QIcon(img_path)
                item.setIcon(icon)
            else:
                if os.path.exists(IMG_PLACEHOLDER):
                    item.setIcon(QIcon(IMG_PLACEHOLDER))
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.list_widget.addItem(item)
    
    def locate_injury(self, name):
        for i in self.injuries:
            if i.get("name", "").lower() == name.lower():
                    return i
            return None

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
            self.clear_instructions()
            return
        name = current.text()
        i = self.locate_injury(name)
        if not i:
            self.clear_instructions()
            return
        self.current_injury = i
        self.current_index = 0
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
