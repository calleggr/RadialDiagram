"""
Stylesheet definitions for the application.
"""

from .colors import COLORS

# Modern stylesheet
STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {COLORS['background']};
}}

QWidget {{
    color: {COLORS['text']};
    font-family: 'Segoe UI', 'Helvetica', 'Arial', sans-serif;
}}

QToolBar {{
    background-color: {COLORS['surface']};
    border-bottom: 1px solid {COLORS['divider']};
    padding: 4px;
}}

QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 4px;
}}

QToolButton:hover {{
    background-color: rgba(0, 0, 0, 0.05);
}}

QToolButton:pressed {{
    background-color: rgba(0, 0, 0, 0.1);
}}

QPushButton {{
    background-color: {COLORS['segment2']};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLORS['segment2_light']};
}}

QPushButton:pressed {{
    background-color: #1976D2;
}}

QPushButton:disabled {{
    background-color: {COLORS['divider']};
    color: {COLORS['text_secondary']};
}}

QLineEdit, QSpinBox {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['divider']};
    border-radius: 4px;
    padding: 6px;
}}

QLineEdit:focus, QSpinBox:focus {{
    border: 2px solid {COLORS['segment2']};
}}

QLabel {{
    color: {COLORS['text']};
}}

QMenu {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['divider']};
    border-radius: 4px;
}}

QMenu::item {{
    padding: 6px 24px;
}}

QMenu::item:selected {{
    background-color: rgba(33, 150, 243, 0.1);
}}

QStatusBar {{
    background-color: {COLORS['surface']};
    color: {COLORS['text_secondary']};
}}

QSlider::groove:horizontal {{
    border: 1px solid {COLORS['divider']};
    height: 4px;
    background: {COLORS['background']};
    margin: 0px;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {COLORS['segment2']};
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}
"""


def get_stylesheet():
    """
    Get the application stylesheet.
    
    Returns:
        str: The stylesheet
    """
    return STYLESHEET
