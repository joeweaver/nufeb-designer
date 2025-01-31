from DialogT6SS import Ui_DialogT6SS
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QHeaderView, QComboBox



class T6SSPairRunner():
    def __init__(self,taxa_info,t6ss_pairs):
        self.t6ss_pairs = t6ss_pairs
        self.Dialog = QtWidgets.QDialog()
        self.dlg = Ui_DialogT6SS()
        self.dlg.setupUi(self.Dialog)

        self.taxa_names = taxa_info.keys()
        cols=["Attacker","Susceptible"]
        self.dlg.pairsTable.setColumnCount(len(cols))
        self.dlg.pairsTable.setHorizontalHeaderLabels(cols)
        self.dlg.pairsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.dlg.addButton.clicked.connect(self.on_add_pair)
        self.dlg.removeButton.clicked.connect(self.on_remove_pair)

        if self.t6ss_pairs:
            self.dlg.pairsTable.setRowCount(len(self.t6ss_pairs))

            for row, row_data in enumerate(self.t6ss_pairs):
                for col, value in enumerate(row_data):
                    # Create a combo box for the cell
                    combo = QComboBox()
                    combo.addItems(self.taxa_names)

                    # Set the combo box to the correct value
                    index = combo.findText(value)
                    if index != -1:  # Valid value, set the index
                        combo.setCurrentIndex(index)

                    # Add the combo box to the table
                    self.dlg.pairsTable.setCellWidget(row, col, combo)

    def exec(self):
        return self.Dialog.exec()

    def on_add_pair(self):
        rowNo = self.dlg.pairsTable.rowCount()
        self.dlg.pairsTable.insertRow(rowNo)
        combo_box_1 = QComboBox()
        combo_box_1.addItems(self.taxa_names)
        combo_box_2 = QComboBox()
        combo_box_2.addItems(self.taxa_names)
        self.dlg.pairsTable.setCellWidget(rowNo, 0, combo_box_1)
        self.dlg.pairsTable.setCellWidget(rowNo, 1, combo_box_2)


    def on_remove_pair(self):
        current_row = self.dlg.pairsTable.currentRow()
        if current_row >= 0:
            self.dlg.pairsTable.removeRow(current_row)

    def get_pairings(self):
        pairings = []
        for row in range(self.dlg.pairsTable.rowCount()):
            row_data = tuple(
                self.dlg.pairsTable.cellWidget(row, col).currentText()  # Get text of the QComboBox
                for col in range(self.dlg.pairsTable.columnCount())
            )
            pairings.append(row_data)
        return pairings