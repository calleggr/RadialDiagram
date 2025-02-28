"""
Outcome model class representing a project outcome on a swimlane.
"""

from utils.id_generator import generate_unique_id


class Outcome:
    """
    Represents a project outcome on a swimlane.
    
    Attributes:
        id (int): Unique identifier for the outcome
        swimlane_id (int): ID of the swimlane this outcome belongs to
        distance (float): Distance from center along the swimlane
        label (str): Text label for the outcome
        item (OutcomeItem): Reference to the visual representation (set by view)
        associated_blobs (list): Blobs connected to this outcome
    """
    
    def __init__(self, swimlane_id, distance, label="", id=None):
        """
        Initialize a new Outcome.
        
        Args:
            swimlane_id (int): ID of the swimlane this outcome belongs to
            distance (float): Distance from center along the swimlane
            label (str, optional): Text label for the outcome. Defaults to "".
            id (int, optional): Unique identifier. Defaults to None (auto-generated).
        """
        self.id = id or generate_unique_id()
        self.swimlane_id = swimlane_id
        self.distance = distance
        self.label = label
        self.item = None  # Reference to the visual representation
        self.associated_blobs = []
    
    def to_dict(self):
        """
        Convert the outcome to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the outcome
        """
        return {
            'id': self.id,
            'swimlane_id': self.swimlane_id,
            'distance': self.distance,
            'label': self.label
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create an Outcome from a dictionary.
        
        Args:
            data (dict): Dictionary containing outcome data
            
        Returns:
            Outcome: New outcome instance
        """
        return cls(
            swimlane_id=data['swimlane_id'],
            distance=data['distance'],
            label=data.get('label', ""),
            id=data.get('id')
        )
