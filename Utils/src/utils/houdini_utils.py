import hou


def display_warning(message):
    hou.ui.displayMessage(message, severity=hou.severityType.Warning)


def display_error(message):
    hou.ui.displayMessage(message, severity=hou.severityType.Error)