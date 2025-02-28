"""
Command for changing the color of an item (for undo/redo).
"""

from PyQt5.QtWidgets import QUndoCommand


class ChangeColorCommand(QUndoCommand):
    """
    Command for changing the color of an item.
    
    This command changes the color of an item, supporting undo/redo.
    
    Attributes:
        item: The item whose color is being changed
        old_color: The original color of the item
        new_color: The new color of the item
    """
    
    def __init__(self, item, old_color, new_color, parent=None):
        """
        Initialize a new ChangeColorCommand.
        
        Args:
            item: The item whose color is being changed
            old_color: The original color of the item
            new_color: The new color of the item
            parent (QUndoCommand, optional): Parent command. Defaults to None.
        """
        super().__init__("Change Color", parent)
        self.item = item
        self.old_color = old_color
        self.new_color = new_color
    
    def redo(self):
        """
        Execute the change color command.
        """
        try:
            # Change color in the item
            if hasattr(self.item, 'set_color'):
                self.item.set_color(self.new_color)
            elif hasattr(self.item, 'setColor'):
                self.item.setColor(self.new_color)
            
            # Update model if needed
            if hasattr(self.item, 'update_model'):
                self.item.update_model()
        except Exception as e:
            print(f"Error in ChangeColorCommand.redo: {e}")
    
    def undo(self):
        """
        Undo the change color command.
        """
        try:
            # Restore original color
            if hasattr(self.item, 'set_color'):
                self.item.set_color(self.old_color)
            elif hasattr(self.item, 'setColor'):
                self.item.setColor(self.old_color)
            
            # Update model if needed
            if hasattr(self.item, 'update_model'):
                self.item.update_model()
        except Exception as e:
            print(f"Error in ChangeColorCommand.undo: {e}")
