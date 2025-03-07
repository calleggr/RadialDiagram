"""
Diagram model class representing the entire project diagram.
"""

import json
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor

from .swimlane import Swimlane
from .outcome import Outcome
from .scope_blob import ScopeBlob


class Diagram:
    """
    Represents the entire project diagram with swimlanes, outcomes, and blobs.
    
    Attributes:
        center (QPointF): Center point of the diagram
        swimlanes (dict): Dictionary of swimlanes by ID
        outcomes (dict): Dictionary of outcomes by ID
        blobs (list): List of scope blobs
    """
    
    def __init__(self, center=None):
        """
        Initialize a new Diagram.
        
        Args:
            center (QPointF, optional): Center point of the diagram. Defaults to (0, 0).
        """
        self.center = center or QPointF(0, 0)
        self.swimlanes = {}
        self.outcomes = {}
        self.blobs = []
    
    def add_swimlane(self, swimlane_or_angle, label="", color=None, length=250):
        """
        Add a new swimlane to the diagram.
        
        Args:
            swimlane_or_angle: Either a Swimlane object or an angle in degrees from the center
            label (str, optional): Text label for the swimlane. Defaults to "".
            color (QColor, optional): Color of the swimlane. Defaults to None.
            length (float, optional): Length of the swimlane from center. Defaults to 250.
            
        Returns:
            Swimlane: The newly created swimlane
        """
        if isinstance(swimlane_or_angle, Swimlane):
            swimlane = swimlane_or_angle
        else:
            swimlane = Swimlane(label, swimlane_or_angle, color, length=length)
        
        self.swimlanes[swimlane.id] = swimlane
        return swimlane
    
    def add_outcome(self, outcome_or_swimlane_id, distance=None, label=""):
        """
        Add a new outcome to the diagram.
        
        Args:
            outcome_or_swimlane_id: Either an Outcome object or the ID of the swimlane this outcome belongs to
            distance (float, optional): Distance from center along the swimlane. Required if outcome_or_swimlane_id is not an Outcome.
            label (str, optional): Text label for the outcome. Defaults to "".
            
        Returns:
            Outcome: The newly created outcome
        """
        from .outcome import Outcome
        
        if isinstance(outcome_or_swimlane_id, Outcome):
            outcome = outcome_or_swimlane_id
        else:
            if distance is None:
                raise ValueError("Distance must be provided when adding an outcome by swimlane_id")
            outcome = Outcome(outcome_or_swimlane_id, distance, label)
        
        self.outcomes[outcome.id] = outcome
        return outcome
    
    def add_blob(self, points, color=None, label=""):
        """
        Add a new scope blob to the diagram.
        
        Args:
            points (list): List of points defining the blob's shape
            color (QColor, optional): Color of the blob. Defaults to None.
            label (str, optional): Text label for the blob. Defaults to "".
            
        Returns:
            ScopeBlob: The newly created blob
        """
        blob = ScopeBlob(points, color, label=label)
        self.blobs.append(blob)
        return blob
    
    def remove_blob(self, blob):
        """
        Remove a blob from the diagram.
        
        Args:
            blob (ScopeBlob): The blob to remove
        """
        if blob in self.blobs:
            # Safe removal from outcomes
            try:
                if hasattr(blob, 'start_outcome') and blob.start_outcome:
                    if hasattr(blob.start_outcome, 'associated_blobs'):
                        if blob in blob.start_outcome.associated_blobs:
                            blob.start_outcome.associated_blobs.remove(blob)
            except Exception as e:
                print(f"Error removing from start outcome: {e}")
                
            try:
                if hasattr(blob, 'end_outcome') and blob.end_outcome:
                    if hasattr(blob.end_outcome, 'associated_blobs'):
                        if blob in blob.end_outcome.associated_blobs:
                            blob.end_outcome.associated_blobs.remove(blob)
            except Exception as e:
                print(f"Error removing from end outcome: {e}")
                
            self.blobs.remove(blob)
    
    def remove_outcome(self, outcome_id):
        """
        Remove an outcome from the diagram.
        
        Args:
            outcome_id (int): ID of the outcome to remove
        """
        if outcome_id in self.outcomes:
            outcome = self.outcomes[outcome_id]
            # Remove any blobs connected to this outcome
            blobs_to_remove = []
            for blob in self.blobs:
                if blob.start_outcome == outcome or blob.end_outcome == outcome:
                    blobs_to_remove.append(blob)
            
            for blob in blobs_to_remove:
                self.remove_blob(blob)
            
            # Remove the outcome
            del self.outcomes[outcome_id]
    
    def remove_swimlane(self, swimlane_id):
        """
        Remove a swimlane from the diagram.
        
        Args:
            swimlane_id (int): ID of the swimlane to remove
        """
        if swimlane_id in self.swimlanes:
            # Remove all outcomes on this swimlane
            outcomes_to_remove = []
            for outcome_id, outcome in self.outcomes.items():
                if outcome.swimlane_id == swimlane_id:
                    outcomes_to_remove.append(outcome_id)
            
            for outcome_id in outcomes_to_remove:
                self.remove_outcome(outcome_id)
            
            # Remove the swimlane
            del self.swimlanes[swimlane_id]
    
    def get_swimlane_by_id(self, swimlane_id):
        """
        Get a swimlane by its ID.
        
        Args:
            swimlane_id: ID of the swimlane to get
            
        Returns:
            Swimlane: The swimlane with the given ID, or None if not found
        """
        return self.swimlanes.get(swimlane_id)
    
    def get_outcome_by_id(self, outcome_id):
        """
        Get an outcome by its ID.
        
        Args:
            outcome_id: ID of the outcome to get
            
        Returns:
            Outcome: The outcome with the given ID, or None if not found
        """
        return self.outcomes.get(outcome_id)
    
    def to_dict(self):
        """
        Convert the diagram to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation of the diagram
        """
        return {
            'center': {'x': self.center.x(), 'y': self.center.y()},
            'swimlanes': [s.to_dict() for s in self.swimlanes.values()],
            'outcomes': [o.to_dict() for o in self.outcomes.values()],
            'blobs': [b.to_dict() for b in self.blobs]
        }
    
    def save_to_file(self, filename):
        """
        Save the diagram to a JSON file.
        
        Args:
            filename (str): Path to the file to save to
        """
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_dict(cls, data):
        """
        Create a Diagram from a dictionary.
        
        Args:
            data (dict): Dictionary containing diagram data
            
        Returns:
            Diagram: New diagram instance
        """
        center = QPointF(data['center']['x'], data['center']['y'])
        diagram = cls(center)
        
        # Create swimlanes
        for swimlane_data in data.get('swimlanes', []):
            swimlane = Swimlane.from_dict(swimlane_data)
            diagram.swimlanes[swimlane.id] = swimlane
        
        # Create outcomes
        for outcome_data in data.get('outcomes', []):
            outcome = Outcome.from_dict(outcome_data)
            diagram.outcomes[outcome.id] = outcome
        
        # Create blobs
        for blob_data in data.get('blobs', []):
            color = QColor(blob_data.get('color', QColor(255, 0, 0, 50).name()))
            blob = ScopeBlob.from_dict(blob_data, diagram.swimlanes, diagram.outcomes)
            diagram.blobs.append(blob)
        
        return diagram
    
    @classmethod
    def load_from_file(cls, filename):
        """
        Load a diagram from a JSON file.
        
        Args:
            filename (str): Path to the file to load from
            
        Returns:
            Diagram: Loaded diagram instance
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
