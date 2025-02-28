"""
Command for adding blobs to the diagram (for undo/redo).
"""

from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtGui import QColor

from styles.colors import COLORS
from views.scope_blob_item import ScopeBlobItem


class AddBlobCommand(QUndoCommand):
    """
    Command for adding blobs to the diagram.
    
    This command creates a new blob and adds it to the scene, supporting undo/redo.
    
    Attributes:
        scene (DiagramScene): The scene to add the blob to
        points (list): List of points defining the blob's shape
        label (str): Text label for the blob
        blob (ScopeBlob): The created blob
        blob_item (ScopeBlobItem): The visual representation of the blob
    """
    
    def __init__(self, scene, points, label):
        """
        Initialize a new AddBlobCommand.
        
        Args:
            scene (DiagramScene): The scene to add the blob to
            points (list): List of points defining the blob's shape
            label (str): Text label for the blob
        """
        super().__init__("Add Blob")
        self.scene = scene
        self.points = points
        self.label = label
        self.blob = None
        self.blob_item = None
    
    def redo(self):
        """
        Execute the add blob command.
        """
        try:
            # Get next segment color
            segment_num = len(self.scene.diagram.blobs) % 4 + 1
            color_key = f'segment{segment_num}'
            
            # Create blob with segment color
            color = QColor(COLORS[color_key])
            color.setAlpha(80)
            self.blob = self.scene.diagram.add_blob(self.points, color=color, label=self.label)
            
            # Store swimlanes and outcomes
            self.blob.start_swimlane = self.scene.start_swimlane
            self.blob.end_swimlane = self.scene.end_swimlane
            self.blob.start_outcome = self.scene.start_outcome
            self.blob.end_outcome = self.scene.end_outcome
            
            # Create and add blob item
            self.blob_item = ScopeBlobItem(self.blob, self.scene)
            self.scene.addItem(self.blob_item)
            self.blob.polygon_item = self.blob_item
            
            # Associate blob with outcomes safely
            if self.blob.start_outcome and hasattr(self.blob.start_outcome, 'item'):
                if hasattr(self.blob.start_outcome.item, 'associated_blobs'):
                    self.blob.start_outcome.item.associated_blobs.append(self.blob_item)
            
            if self.blob.end_outcome and hasattr(self.blob.end_outcome, 'item'):
                if hasattr(self.blob.end_outcome.item, 'associated_blobs'):
                    self.blob.end_outcome.item.associated_blobs.append(self.blob_item)
        except Exception as e:
            print(f"Error in AddBlobCommand.redo: {e}")
    
    def undo(self):
        """
        Undo the add blob command.
        """
        try:
            # Remove from associated outcomes safely
            if hasattr(self.blob, 'start_outcome') and self.blob.start_outcome:
                if hasattr(self.blob.start_outcome, 'item') and self.blob.start_outcome.item:
                    if hasattr(self.blob.start_outcome.item, 'associated_blobs'):
                        if self.blob_item in self.blob.start_outcome.item.associated_blobs:
                            self.blob.start_outcome.item.associated_blobs.remove(self.blob_item)
            
            if hasattr(self.blob, 'end_outcome') and self.blob.end_outcome:
                if hasattr(self.blob.end_outcome, 'item') and self.blob.end_outcome.item:
                    if hasattr(self.blob.end_outcome.item, 'associated_blobs'):
                        if self.blob_item in self.blob.end_outcome.item.associated_blobs:
                            self.blob.end_outcome.item.associated_blobs.remove(self.blob_item)
            
            # Remove blob from scene
            if self.blob_item:
                self.scene.removeItem(self.blob_item)
            if self.blob:
                self.scene.diagram.remove_blob(self.blob)
        except Exception as e:
            print(f"Error in AddBlobCommand.undo: {e}")
