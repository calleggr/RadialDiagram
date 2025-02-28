"""
Swimlane model class representing a project swimlane.
"""

from PyQt5.QtGui import QColor
from utils.id_generator import generate_unique_id
from styles.colors import COLORS


class Swimlane:
    """
    Represents a project swimlane (radial line) in the diagram.
    
    Attributes:
        id (int): Unique identifier for the swimlane
        angle (float): Angle in degrees from the center
        label (str): Text label for the swimlane
        color (QColor): Color of the swimlane
        item (SwimlaneItem): Reference to the visual representation (set by view)
    """
    
    def __init__(self, label="", angle=0, color=None, id=None):
        """
        Initialize a new Swimlane.
        
        Args:
            label (str, optional): Text label for the swimlane. Defaults to "".
            angle (float, optional): Angle in degrees from the center. Defaults to 0.
            color (QColor, optional): Color of the swimlane. Defaults to segment1 color.
            id (int, optional): Unique identifier. Defaults to None (auto-generated).
        """
        self.id = id or generate_unique_id()
        self.angle = angle
        self.label = label
        self.color = color or QColor(COLORS['segment1'])
        self.item = None  # Reference to the visual representation
    
    def to_dict(self):
        """
        Convert the swimlane to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the swimlane
        """
        return {
            'id': self.id,
            'angle': self.angle,
            'label': self.label,
            'color': self.color.name()
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Swimlane from a dictionary.
        
        Args:
            data (dict): Dictionary containing swimlane data
            
        Returns:
            Swimlane: New swimlane instance
        """
        return cls(
            angle=data['angle'],
            label=data.get('label', ""),
            color=QColor(data.get('color', COLORS['segment1'])),
            id=data.get('id')
        )
