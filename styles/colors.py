"""
Color definitions for the application.
"""

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

# Modern color scheme
COLORS = {
    'segment1': '#00BCD4',  # Turquoise
    'segment2': '#2196F3',  # Blue 
    'segment3': '#E91E63',  # Pink
    'segment4': '#F44336',  # Red
    'segment1_light': '#4DD0E1',
    'segment2_light': '#64B5F6',
    'segment3_light': '#F06292',
    'segment4_light': '#EF5350',
    'background': '#FAFAFA',
    'surface': '#FFFFFF',
    'text': '#212121',
    'text_secondary': '#757575',
    'divider': '#BDBDBD',
    'error': '#F44336'
}

# Default colors for swimlanes, outcomes, and blobs
DEFAULT_COLORS = [
    QColor('#00BCD4'),  # Turquoise
    QColor('#2196F3'),  # Blue
    QColor('#E91E63'),  # Pink
    QColor('#F44336'),  # Red
    QColor('#8BC34A'),  # Light Green
    QColor('#FFC107'),  # Amber
    QColor('#9C27B0'),  # Purple
    QColor('#FF5722'),  # Deep Orange
]


def get_color_palette():
    """Create a QPalette with modern colors."""
    palette = QPalette()
    
    # Set colors for various palette roles
    palette.setColor(QPalette.Window, QColor(COLORS['background']))
    palette.setColor(QPalette.WindowText, QColor(COLORS['text']))
    palette.setColor(QPalette.Base, QColor(COLORS['surface']))
    palette.setColor(QPalette.AlternateBase, QColor(COLORS['background']))
    palette.setColor(QPalette.ToolTipBase, QColor(COLORS['surface']))
    palette.setColor(QPalette.ToolTipText, QColor(COLORS['text']))
    palette.setColor(QPalette.Text, QColor(COLORS['text']))
    palette.setColor(QPalette.Button, QColor(COLORS['surface']))
    palette.setColor(QPalette.ButtonText, QColor(COLORS['text']))
    palette.setColor(QPalette.Link, QColor(COLORS['segment2']))
    palette.setColor(QPalette.Highlight, QColor(COLORS['segment2']))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    
    return palette
