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

APP_BG = "#e0d1f8"
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
        display_layout.addWidget(self.instruction)

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
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {APP_BG}; }}
            QWidget#card {{ background: {CARD_BG}; border-radius: 12px; }}
            QListWidget {{ background: transparent; border: none; padding: 8px; }}
            QListWidget::item {{ background: {CARD_BG}; border-radius:10px; padding: 12px; margin: 6px; color: {TEXT_COLOR}; }}
            QListWidget::item:selected {{ border: 2px solid {PRIMARY}; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffffff, stop:1 #f4f9ff); }}
            QPushButton {{ background-color: {PRIMARY}; color: white; padding: 8px 14px; border-radius: 8px; font-weight: 600; }}
            QPushButton:disabled {{ background-color: #bfc9d9; color: #ffffff; }}
            QLineEdit {{ background: white; border: 1px solid #d7dde3; border-radius: 8px; padding: 8px; }}
        """)
        #self.emergency_button.setObjectName("emergency")
    
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

    def clear_instructions(self):
        self.injury_title.setText("Select an injury")
        self.instruction.setText("Choose an injury on the left to view step-to-step guidance.")
        self.img_label.clear()
        self.toggle_like.setChecked(False)
        self.toggle_like.setText("☆ Favorite")

    def update_instructions(self):
        i = getattr(self, "current_injury", None)
        if not i:
            self.clear_instructions(); return
        name = i.get("name", "injury")
        steps = i.get("steps", [])
        if self.current_index >= len(steps):
            self.current_index = max(0, len(steps)-1)
        self.injury_title.setText(name)
        if steps:
            content = f"<b>Step {self.current_index+1}/{len(steps)}</b><br><p style='margin-top: 6px'>{steps[self.current_index]}</p>"
        else:
            content = "<i>No steps available.</i>"
        self.instruction.setText(content)
    
        # image display
        img_name = i.get("image", "")
        img_path = os.path.join("icons", img_name) if img_name else ""
        if img_path and os.path.exists(img_path):
            pix = QPixmap(img_path).scaledToHeight(260, Qt.TransformationMode.SmoothTransformation)
            self.img_label.setPixmap(pix)
        else:
            if os.path.exists(IMG_PLACEHOLDER):
                pix = QPixmap(IMG_PLACEHOLDER).scaledToHeight(180, Qt.TransformationMode.SmoothTransformation)
                self.img_label.setPixmap(pix)
            else:
                self.img_label.clear()

        if name in self.favourites:
            self.like_button.setChecked(True)
            self.like_button.setText("★ Favorited")
        else:
            self.like_button.setChecked(False)
            self.like_button.setText("☆ Favorite")

    def read_current_step(self):
        i = getattr(self, "current_injury", None)
        if not i: return
        steps = i.get("steps", [])
        t = f"{i.get('name')}. Step {self.current_index+1}. {steps[self.current_index]}"
        try:
            self.tss_engine.say(t)
            self.tss_engine.runAndWait()
        except Exception as e:
            QMessageBox.warning(self, "TTS Error", f"Could not play voice:{e}")
            
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
        text = (text or "").strip().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text not in item.text().lower())

    def click_like(self):
        i = getattr(self, "current_injury", None)
        if not i:
            return
        name = i.get("name")
        if name in self.favourites:
            self.favourites.remove(name)
            self.like_button.setText("☆ Favorite")
        else:
            self.favourites.append(name)
            self.like_button.setText("★ Favorited")
    
    def show_favs(self):
        if not self.favourites:
            QMessageBox.information(self, "Favourites", "You have no favourites yet. Mark an injury then come back.")
            return
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(item.text() not in self.favourites)

    def show_emergency(self):
        QMessageBox.information(self, "Emergency", "Call your local emergency number immediately!",
            buttons= QMessageBox.StandardButton.Ok)
        
    def display_about(self):
        QMessageBox.information(self, "About FirstAid", "First Aid - Quick Help\nSimple offline first-aid guidance.")
