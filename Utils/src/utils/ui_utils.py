import os

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *


def populate_combobox(box: QComboBox, folder: str):
    """
    Adds values to combo box based on child directories of given folder.

    Args:
        box (QComboBox): ComboBox to fill values in.
        folder (str): Folder to get children of.

    Raises:
        FileNotFoundError: If directory doesn't exist.
    """
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Path does not exist: {folder}")
    if len(os.listdir(folder)) > 0:
        box.addItems(sorted(os.listdir(folder)))
    else:
        box.addItems(["Empty"])


def popup_warning(message: str, parent=None):
    """
    Creates a Qt popup warning message.

    Args:
        message (str): Message to display.
        parent (QWidget, optional): Parent to inherit from. Defaults to None.
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("Warning")
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
    msg_box.exec()
    

def new_parm(text: str, layout: QWidget, font: QFont, box_width: float, type: str):
    """
    Adds common parameter types to Qt Ui.

    Args:
        text (str): Label to be used.
        layout (QWidget): Qt layout to add parameter to.
        font (QFont): Font of parameter.
        box_width (float): Width of parameter.
        type (str): Type of parameter to create.

    Returns:
        QWidget: Returns new parameter instance.
    """
    if type == "QLineEdit":
        parm = QLineEdit()
        parm.setPlaceholderText(text)
        parm.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout.addWidget(parm, 2)

    if type == "QComboBox":
        label = QLabel(text)
        label.setFixedWidth(box_width)
        label.setFont(font)
        parm = QComboBox()

        layout.addWidget(label, 1)
        layout.addWidget(parm, 1)

    parm.setFont(font)
    parm.setFixedWidth(box_width)
    
    return parm
