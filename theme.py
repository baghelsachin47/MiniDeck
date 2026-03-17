# theme.py

MODERN_THEME = """
QWidget {
    background-color: #1E1E1E;
    color: #E0E0E0;
    font-family: "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #333333;
    border-radius: 8px;
    margin-top: 1.5ex;
    font-weight: bold;
    color: #00D2FF; 
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 0 5px;
}

QPushButton {
    background-color: #2D2D30;
    border: 1px solid #3E3E42;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #3E3E42;
    border: 1px solid #00D2FF;
    color: #00D2FF;
}
QPushButton:pressed {
    background-color: #00D2FF;
    color: #121212;
}

/* Tree and List Widgets */
QTreeWidget, QListWidget {
    background-color: #121212;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 5px;
    outline: none;
}
QTreeWidget::item, QListWidget::item {
    padding: 8px;
    border-radius: 4px;
}
QTreeWidget::item:hover, QListWidget::item:hover {
    background-color: #2A2A2D;
}
QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #00D2FF;
    color: #121212;
}

/* Custom Tree Header */
QHeaderView::section {
    background-color: #1E1E1E;
    color: #888888;
    padding: 4px;
    border: none;
    border-bottom: 1px solid #333333;
    font-weight: bold;
}

/* Custom Sliders */
QSlider::groove:horizontal {
    border-radius: 4px;
    height: 6px;
    background: #3E3E42;
}
QSlider::handle:horizontal {
    background: #00D2FF;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #55E0FF;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QSlider::sub-page:horizontal {
    background: #007A99;
    border-radius: 4px;
}

/* Search Bar */
QLineEdit {
    background-color: #121212;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 8px;
    color: #FFFFFF;
}
QLineEdit:focus {
    border: 1px solid #00D2FF;
}

/* Checkbox */
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #555;
    background-color: #2D2D30;
}
QCheckBox::indicator:checked {
    background-color: #00D2FF;
    border: 1px solid #00D2FF;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #1E1E1E;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #444;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #666;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""