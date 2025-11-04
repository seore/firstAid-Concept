from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QLineEdit, QMessageBox, QHBoxLayout,
    QSpacerItem, QSizePolicy, QFrame, QToolButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QEvent, QSize
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor
import os
import pyttsx3
import json
import webbrowser
import platform

APP_BG = "#eaf4f4"
CARD_BG = "#c8d9e6"
PRIMARY = "#4a90e2"
EMERGENCY_COLOR = "#e53935"
FAV = "#f1c40f"
UI_ACCENT = "#4caf50"
TEXT_COLOR = "#1e1b2e"
INPUT_BG = "#ffffff"
INPUT_TEXT = "#000000"
MUTED = "#7d7396"
IMG_PLACEHOLDER = ""

class MainWindow(QMainWindow):
    def __init__(self, injuries):
        super().__init__()
        self.tss_engine = pyttsx3.init()
        self.setWindowTitle("First-Aid App")
        self.resize(1000, 650)
        self.injuries = injuries
        self.current_index = 0
        self.favourites = []

        # Main Container
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)
        self.container_layout.setContentsMargins(18,12,18,12)
        self.container_layout.setSpacing(12)
        self.setCentralWidget(self.container)
        self.setMinimumSize(900,600)

        # Header
        header = QHBoxLayout()
        title_label = QLabel("First Aid")
        title_label.setFont(QFont("Noto Sans", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {TEXT_COLOR};")
        header.addWidget(title_label)
        header.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        about_button = QToolButton()
        about_button.setText("About")
        about_button.clicked.connect(self.display_about) 
        about_button.setAutoRaise(True)
        header.addWidget(about_button)
        self.container_layout.addLayout(header)

        # Search bar + main
        top_display = QHBoxLayout()
        top_display.setSpacing(18)
        self.container_layout.addLayout(top_display, stretch=1)

        # Left Display - Injuries
        left_display = QFrame()
        left_display.setObjectName("display_left")
        left_display_layout = QVBoxLayout(left_display)
        left_display_layout.setContentsMargins(14,14,14,14)
        left_display_layout.setSpacing(18)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for injury type...")
        self.search_bar.textChanged.connect(self.filter_list)
        self.search_bar.setFixedHeight(42)
        left_display_layout.addWidget(self.search_bar)

        self.list_widget = QListWidget()
        self.list_widget.setSpacing(10)
        self.list_widget.setUniformItemSizes(False)
        # self.list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_widget.currentItemChanged.connect(self.show_steps)
        left_display_layout.addWidget(self.list_widget)

        top_display.addWidget(left_display, stretch=34)
    
        # Right Display - Injuries Details
        right_display = QFrame()
        right_display.setObjectName("display_right")
        right_display_layout = QVBoxLayout(right_display)
        right_display_layout.setContentsMargins(18,18,18,18)
        right_display_layout.setSpacing(14)

        # Favourites Display Card
        title_r = QHBoxLayout()
        self.injury_title = QLabel("Choose an injury")
        self.injury_title.setFont(QFont("Noto Sans", 16, QFont.Weight.DemiBold))
        title_r.addWidget(self.injury_title)
        title_r.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.like_button = QPushButton("Favourite")
        self.like_button.setCheckable(True)
        self.like_button.clicked.connect(self.click_like)
        title_r.addWidget(self.like_button)
        right_display_layout.addLayout(title_r)

        # Placeholder Display
        self.img_label = QLabel()
        self.img_label.setFixedHeight(260)
        self.img_label.setStyleSheet("border-radius: 12px; background: #f6f8fb;")
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setObjectName("image_label")
        right_display_layout.addWidget(self.img_label)

        # Instruction Display
        self.instruction = QLabel("Select an injury to see steps.")
        self.instruction.setWordWrap(True)
        self.instruction.setFont(QFont("Noto Sans", 12))
        self.instruction.setStyleSheet("color: %s;" % TEXT_COLOR)
        self.instruction.setObjectName("intstruction")
        right_display_layout.addWidget(self.instruction, stretch=1)

        # App buttons
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.clicked.connect(self.prev_step)
        self.prev_button.setObjectName("primary")
        self.next_button = QPushButton("Next  ▶")
        self.next_button.clicked.connect(self.next_step)
        self.next_button.setObjectName("primary")
        #self.voice_button = QPushButton("Play Voice")
        #self.voice_button.clicked.connect(self.read_current_step)
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)
        #nav_layout.addWidget(self.voice_button)
        nav_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        right_display_layout.addLayout(nav_layout)

        # Other App Buttons
        footer_layout = QHBoxLayout()
        self.emergency_button = QPushButton("🚨 Emergency")
        self.emergency_button.clicked.connect(self.show_emergency)
        self.emergency_button.setStyleSheet(f"background-color: {EMERGENCY_COLOR}; color: white; font-weight: bold;")
        self.display_favs = QPushButton("★ Favourites")
        self.display_favs.clicked.connect(self.show_favs)
        self.emergency_button.setObjectName("emergency")
        self.display_favs.setObjectName("fav")
        footer_layout.addWidget(self.emergency_button)
        footer_layout.addWidget(self.display_favs)
        footer_layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        right_display_layout.addLayout(footer_layout)
    
        top_display.addWidget(right_display, stretch=66)

        self.populate_list()
        self.apply_styles()

    # ---------------------  Lists -----------------------
    def populate_list(self):
        self.list_widget.clear()
        for injury in self.injuries:
            name = injury.get("name", "unknown")
            item = QListWidgetItem(name)
            img_title = injury.get("icons", "")
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
        self.like_button.setChecked(False)
        self.like_button.setText("☆ Favorite")

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
        img_path = os.path.join("data/icons", img_name) if img_name else ""
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
        emergency_number = "999"
        try:
            webbrowser.open(f"tel: {emergency_number}")
            if platform.system() in ["Windows", "Darwin"]:
                webbrowser.open(f"facetime://{emergency_number}")
                webbrowser.open(f"skype:{emergency_number}?call")
        except Exception as e:
            print(f"Call launch failed: {e}")
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Emergency Help")
        msg.setStyleSheet("""
           QMessageBox {{ 
                background-color: #fefefe; 
                border-radius: 12px; 
                font-family: 'SF Pro Display'; 
                color: #1e1b2e; 
            }}
            QMessageBox QLabel {{ 
                font-size: 13pt; 
                color: #1e1b2e; 
            }}
            QPushButton {{ 
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ff6b60, stop:1 #e53935; 
                border-radius: 8px; 
                padding: 8px 14px;
                font-weight: bold; 
                color: white; 
            }}
            QPushButton:hover {{ background: #ff7a6a; }}            
        """)

        msg.setText("<b>🚨 Emergency Assistance</b>")
        msg.setInformativeText(
            f"If calling fails automatically, please dial one of the following numbers:\n\n"
            f"911 (USA)\n"
            f"112 (EU / Worldwide GSM)\n"
            f"999 (UK)\n"
            f"000 (Australia)\n\n"
            f"You can also try calling directly using Facetime or Skype."
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        # In Case
        skype_button = QPushButton("Call via Skype")
        skype_button.clicked.connect(lambda: webbrowser.open(f"skype:{emergency_number}?call"))
        msg.addButton(skype_button, QMessageBox.ButtonRole.ActionRole)
        msg.exec()

    def display_about(self):
        QMessageBox.information(self, "About FirstAid", "First Aid - Quick Help\nSimple offline first-aid guidance.")
    

    def apply_styles(self):
        self.setStyleSheet(f"""
        QMainWindow {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #f3f6ff, stop:1 {APP_BG}); }}
        QFrame#display_left, QFrame#display_right {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffffff, stop:1 #eef6ff);
            border-radius: 12px;
            border-top: 1px solid rgba(255,255,255,0.9); 
            border-bottom: 1px solid rgba(0,0,0,0.06);  
        }}
        QListWidget {{
            background: transparent;
            border: none;
            padding: 6px;
        }}
        QListWidget::item {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #f6fbff, stop:1 #e6f0fb);
            border-radius: 10px;
            padding: 12px 16px;
            margin: 8px 4px;
            color: {TEXT_COLOR};
            font-size: 13pt;
            border-top: 1px solid rgba(255,255,255,0.95); 
            border-bottom: 2px solid rgba(0,0,0,0.04);  
        }}
        QListWidget::item:selected {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ffffff, stop:1 #eaf3ff);
            color: {TEXT_COLOR};
            border: 2px solid {PRIMARY};
        }}

        /* Search input (black text only here) */
        QLineEdit {{
            background: {INPUT_BG if 'INPUT_BG' in globals() else '#ffffff'};
            color: #000000;
            border-radius: 10px;
            padding: 10px;
            font-size: 12pt;
            border: 1px solid rgba(0,0,0,0.08);
        }}

        /* Image box (flat card) */
        QLabel {{
            color: {TEXT_COLOR};
        }}
        QLabel#image_label {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffffff, stop:1 #f7fbff);
            border-radius: 10px;
            border-top: 1px solid rgba(255,255,255,0.9);
            border-bottom: 1px solid rgba(0,0,0,0.03);
        }}

        /* Buttons: 3D look using gradients + light top edge */
        QPushButton {{
            border-radius: 10px;
            padding: 10px 14px;
            color: white;
            font-weight: 600;
            min-height: 40px;
        }}

        QPushButton#primary, QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {PRIMARY},
                stop:1 #5f3fe0);
            border-top: 1px solid rgba(255,255,255,0.9); 
            border-bottom: 2px solid rgba(0,0,0,0.12);  
        }}
        QPushButton#primary:hover {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #7a5df0, stop:1 #5b3ff0);
        }}
        QPushButton#primary:pressed {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #5b3ff0, stop:1 #7a5df0);
            border-top: 2px solid rgba(0,0,0,0.08);
            border-bottom: 1px solid rgba(255,255,255,0.7);
            padding-top: 12px;
        }}

        QPushButton#emergency {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ff6b60, stop:1 {EMERGENCY_COLOR});
            border-top: 1px solid rgba(255,255,255,0.9);
            border-bottom: 2px solid rgba(0,0,0,0.12);
        }}
        QPushButton#emergency:pressed {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {EMERGENCY_COLOR}, stop:1 #ff6b60);
            border-top: 2px solid rgba(0,0,0,0.08);
            border-bottom: 1px solid rgba(255,255,255,0.7);
            padding-top: 12px;
        }}

        QPushButton#fav {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffe27a, stop:1 #f1c40f);
            color: #1e1b2e;
            border-top: 1px solid rgba(255,255,255,0.9);
            border-bottom: 2px solid rgba(0,0,0,0.06);
        }}
        QPushButton#fav:pressed {{
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #f1c40f, stop:1 #ffd65a);
            padding-top: 12px;
        }}
        QLabel#injury_title {{
            font-size: 16pt;
            font-weight: 700;
            color: {TEXT_COLOR};
        }}
        QLabel#instruction {{
            font-size: 13pt;
            color: {TEXT_COLOR};
        }}
    """)
  

