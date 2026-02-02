import hou


def display_warning(message: str):
    """
    Displays a houdini warning.

    Args:
        message (str): Message to display.
    """
    hou.ui.displayMessage(message, severity=hou.severityType.Warning)


def display_error(message: str):
    """
    Displays a houdini error.

    Args:
        message (str): Message to display.
    """
    hou.ui.displayMessage(message, severity=hou.severityType.Error)