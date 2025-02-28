"""
ScopeBlob model class representing a connection between outcomes.
"""

from PyQt5.QtGui import QColor
from utils.id_generator import generate_unique_id


class ScopeBlob:
    """
    Represents a scope blob connecting outcomes in the diagram.
    
    Attributes:
        id (int): Unique identifier for the blob
        points (list): List of points defining the blob's shape
        color (QColor): Color of the blob
        label (str): Text label for the blob
        polygon_item (ScopeBlobItem): Reference to the visual representation (set by view)
        start_swimlane (Swimlane): Starting swimlane
        end_swimlane (Swimlane): Ending swimlane
        start_outcome (Outcome): Starting outcome
        end_outcome (Outcome): Ending outcome
    """
    
    def __init__(self, points, color=None, id=None, label=""):
        """
        Initialize a new ScopeBlob.
        
        Args:
            points (list): List of points defining the blob's shape
            color (QColor, optional): Color of the blob. Defaults to semi-transparent red.
            id (int, optional): Unique identifier. Defaults to None (auto-generated).
            label (str, optional): Text label for the blob. Defaults to "".
        """
        self.id = id or generate_unique_id()
        self.points = points
        self.color = color or QColor(255, 0, 0, 50)
        self.polygon_item = None  # Reference to the visual representation
        self.label = label
        self.label_item = None
        self.start_swimlane = None
        self.end_swimlane = None
        self.start_outcome = None
        self.end_outcome = None
        self.associated_blobs = []  # For compatibility with outcome references
    
    def to_dict(self):
        """
        Convert the blob to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the blob
        """
        return {
            'id': self.id,
            'points': self.points,
            'color': self.color.name(QColor.HexArgb),
            'label': self.label,
            'start_swimlane_id': self.start_swimlane.id if self.start_swimlane else None,
            'end_swimlane_id': self.end_swimlane.id if self.end_swimlane else None,
            'start_outcome_id': self.start_outcome.id if self.start_outcome else None,
            'end_outcome_id': self.end_outcome.id if self.end_outcome else None
        }
    
    @classmethod
    def from_dict(cls, data, swimlanes=None, outcomes=None):
        """
        Create a ScopeBlob from a dictionary.
        
        Args:
            data (dict): Dictionary containing blob data
            swimlanes (dict, optional): Dictionary of swimlanes by ID. Defaults to None.
            outcomes (dict, optional): Dictionary of outcomes by ID. Defaults to None.
            
        Returns:
            ScopeBlob: New blob instance
        """
        blob = cls(
            points=data['points'],
            color=QColor(data.get('color', QColor(255, 0, 0, 50).name(QColor.HexArgb))),
            id=data.get('id'),
            label=data.get('label', "")
        )
        
        # Link to swimlanes and outcomes if provided
        if swimlanes:
            start_id = data.get('start_swimlane_id')
            end_id = data.get('end_swimlane_id')
            if start_id and start_id in swimlanes:
                blob.start_swimlane = swimlanes[start_id]
            if end_id and end_id in swimlanes:
                blob.end_swimlane = swimlanes[end_id]
        
        if outcomes:
            start_id = data.get('start_outcome_id')
            end_id = data.get('end_outcome_id')
            if start_id and start_id in outcomes:
                blob.start_outcome = outcomes[start_id]
            if end_id and end_id in outcomes:
                blob.end_outcome = outcomes[end_id]
        
        return blob
