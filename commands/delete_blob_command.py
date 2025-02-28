"""
Command for deleting blobs from the diagram (for undo/redo).
"""

from PyQt5.QtWidgets import QUndoCommand


class DeleteBlobCommand(QUndoCommand):
    """
    Command for deleting blobs from the diagram.
    
    This command removes a blob from the scene, supporting undo/redo.
    
    Attributes:
        scene (DiagramScene): The scene to remove the blob from
        blob (ScopeBlob): The blob to remove
        blob_item (ScopeBlobItem): The visual representation of the blob
        start_outcome_item: The item representing the start outcome
        end_outcome_item: The item representing the end outcome
    """
    
    def __init__(self, scene, blob_item):
        """
        Initialize a new DeleteBlobCommand.
        
        Args:
            scene (DiagramScene): The scene to remove the blob from
            blob_item (ScopeBlobItem): The visual representation of the blob
        """
        super().__init__("Delete Blob")
        self.scene = scene
        self.blob_item = blob_item
        self.blob = blob_item.blob
        
        # Store references for undo
        self.start_outcome_item = None
        self.end_outcome_item = None
        
        # Store outcome references if they exist
        if hasattr(self.blob, 'start_outcome') and self.blob.start_outcome:
            if hasattr(self.blob.start_outcome, 'item'):
                self.start_outcome_item = self.blob.start_outcome.item
        
        if hasattr(self.blob, 'end_outcome') and self.blob.end_outcome:
            if hasattr(self.blob.end_outcome, 'item'):
                self.end_outcome_item = self.blob.end_outcome.item
    
    def redo(self):
        """
        Execute the delete blob command.
        """
        try:
            # Remove from associated outcomes safely
            if self.start_outcome_item:
                if hasattr(self.start_outcome_item, 'associated_blobs'):
                    if self.blob_item in self.start_outcome_item.associated_blobs:
                        self.start_outcome_item.associated_blobs.remove(self.blob_item)
            
            if self.end_outcome_item:
                if hasattr(self.end_outcome_item, 'associated_blobs'):
                    if self.blob_item in self.end_outcome_item.associated_blobs:
                        self.end_outcome_item.associated_blobs.remove(self.blob_item)
            
            # Remove blob from scene
            self.scene.removeItem(self.blob_item)
            self.scene.diagram.remove_blob(self.blob)
        except Exception as e:
            print(f"Error in DeleteBlobCommand.redo: {e}")
    
    def undo(self):
        """
        Undo the delete blob command.
        """
        try:
            # Add blob back to diagram
            self.scene.diagram.blobs.append(self.blob)
            
            # Add blob item back to scene
            self.scene.addItem(self.blob_item)
            
            # Re-associate with outcomes
            if self.start_outcome_item:
                if hasattr(self.start_outcome_item, 'associated_blobs'):
                    self.start_outcome_item.associated_blobs.append(self.blob_item)
            
            if self.end_outcome_item:
                if hasattr(self.end_outcome_item, 'associated_blobs'):
                    self.end_outcome_item.associated_blobs.append(self.blob_item)
        except Exception as e:
            print(f"Error in DeleteBlobCommand.undo: {e}")
