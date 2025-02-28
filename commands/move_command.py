"""
Command for moving items in the diagram (for undo/redo).
"""

from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import QPointF


class MoveCommand(QUndoCommand):
    """
    Command for moving items in the diagram.
    
    This command stores the old and new positions of an item to support undo/redo.
    
    Attributes:
        item: The item being moved
        old_pos (QPointF): The original position of the item
        new_pos (QPointF): The new position of the item
    """
    
    def __init__(self, item, old_pos, new_pos, parent=None):
        """
        Initialize a new MoveCommand.
        
        Args:
            item: The item being moved
            old_pos (QPointF): The original position of the item
            new_pos (QPointF): The new position of the item
            parent (QUndoCommand, optional): Parent command. Defaults to None.
        """
        super().__init__("Move Item", parent)
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos
    
    def redo(self):
        """
        Execute the move command.
        """
        self.item.setPos(self.new_pos)
        # Update any associated model data if needed
        if hasattr(self.item, 'update_model_position'):
            self.item.update_model_position()
    
    def undo(self):
        """
        Undo the move command.
        """
        self.item.setPos(self.old_pos)
        # Update any associated model data if needed
        if hasattr(self.item, 'update_model_position'):
            self.item.update_model_position()
