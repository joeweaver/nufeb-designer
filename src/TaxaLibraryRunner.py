from poisson import PoissonDisc
from TaxaLibrary import Ui_TaxaLibraryDialog
from DialogAssignTaxa import Ui_Dialog
from PyQt6.QtCore import Qt
from TaxaLibrary import Ui_TaxaLibraryDialog
from PyQt6 import  QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem,  QFileDialog, QHeaderView
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtCore import QPoint
import numpy as np
import json
import random


class TaxaLibraryRunner():
    def __init__(self,taxa_info):
        self.Dialog = QtWidgets.QDialog()
        self.dlg = Ui_TaxaLibraryDialog()
        self.dlg.setupUi(self.Dialog)
        self.taxa_info = taxa_info

        self.dlg.taxaTable.blockSignals(True)
        self.dlg.growthTable.blockSignals(True)
        self._populateTaxaTable()
        self.dlg.taxaTable.blockSignals(False)
        self.dlg.growthTable.blockSignals(False)
        self.dlg.taxaTable.cellClicked.connect(self.taxaTableClicked)
        self.dlg.loadTaxaButton.clicked.connect(self.on_load_taxa_clicked)
        self.dlg.addTaxonButton.clicked.connect(self.on_add_taxon)
        self.dlg.taxaTable.cellChanged.connect(self.on_taxa_table_changed)
        self.dlg.growthTable.cellChanged.connect(self.on_growth_table_changed)
        self.dlg.removeTaxonButton.clicked.connect(self.on_remove_taxon)
        self.dlg.duplicateTaxonButton.clicked.connect(self.on_duplicate_taxon)
        self.dlg.saveTaxaButton.clicked.connect(self.on_save_taxa_clicked)

    def on_save_taxa_clicked(self):
        file_path, _ = QFileDialog.getSaveFileName(self.Dialog, "Save File", "", "Taxa Library (*.json);;All Files (*)")
        if file_path:
            with open(file_path, "w") as f:
                json.dump(self.taxa_info, f, indent=4)  # indent for better readability
        else:
            print("No file selected.")
    def on_growth_table_changed(self, row, column):
        indices = self.dlg.taxaTable.selectedIndexes()
        if indices:
            taxaRow=indices[0].row()
        growth_strat = self.dlg.taxaTable.item(taxaRow,6).text()
        taxon = self.dlg.taxaTable.item(taxaRow, 0).text()
        if growth_strat== 'growth_het':
            growth_colmap = ['name', 'strat', 'mu_max', 'sub-Ks', 'o2-Ks', 'no2-Ks', 'no3-Ks',
                           'yield', 'decay', 'anoxic', 'maintain', 'epsyield', 'epsdens']
            newtext = str(self.dlg.growthTable.item(row, column).text())
            self.taxa_info[taxon]['growth_strategy'][growth_colmap[column]] = newtext


    def on_duplicate_taxon(self):
        selected_indices = self.dlg.taxaTable.selectedIndexes()
        if selected_indices:
            row = selected_indices[0].row()
            name = self.dlg.taxaTable.item(row,0).text()
            newNum = self.dlg.taxaTable.rowCount()+1
            dupName= f'{name}_duplicate_{newNum}'
            self.taxa_info[dupName]=self.taxa_info[name]
            self.dlg.taxaTable.blockSignals(True)
            self.dlg.growthTable.blockSignals(True)
            self.dlg.taxaTable.clear()
            self.dlg.growthTable.clear()
            self._populateTaxaTable()
            self.dlg.taxaTable.selectRow(newNum)
            self.dlg.taxaTable.blockSignals(False)
            self.dlg.growthTable.blockSignals(False)
    def on_remove_taxon(self):
        selected_indices = self.dlg.taxaTable.selectedIndexes()

        if selected_indices:
            row = selected_indices[0].row()
            name = self.dlg.taxaTable.item(row,0).text()
            self.taxa_info.pop(name)
            self.dlg.taxaTable.blockSignals(True)
            self.dlg.growthTable.blockSignals(True)
            self.dlg.taxaTable.clear()
            self.dlg.growthTable.clear()
            self._populateTaxaTable()
            self.dlg.taxaTable.blockSignals(False)
            self.dlg.growthTable.blockSignals(False)

    def on_taxa_table_changed(self, row, column):
        taxa_colmap =['name','diameter','outer_diameter','division_strategy','density','morphology','growth_strategy','description']
        name = self.dlg.taxaTable.item(row,0).text()
        newtext = str(self.dlg.taxaTable.item(row,column).text())
        # if name hasn't changed
        if column != 0:
            # special cases where it's nested
            if column == 3:
                self.taxa_info[name][taxa_colmap[column]]['diameter'] = newtext
            elif column == 6:
                self.taxa_info[name][taxa_colmap[column]]['name'] = newtext
            else:
                self.taxa_info[name][taxa_colmap[column]] =newtext
        else:
            old_names = set(self.taxa_info.keys())
            names = []
            for i in range(self.dlg.taxaTable.rowCount()):
                names.append(str(self.dlg.taxaTable.item(i,0).text()))
            new_names = set(names)
            old_name = list(old_names.difference(new_names))[0]
            self.taxa_info[name] = self.taxa_info[old_name]
            self.taxa_info.pop(old_name)



    def on_add_taxon(self):
        name = f'new_taxon_{len(self.taxa_info.keys())}'
        self.taxa_info[name] = {'growth_strategy':{
                                     "name": "growth_het",
                                      "sub-ID":"sub",
                                      "sub-Ks" : 3.5e-5,
                                      "o2-ID": "o2",
                                      "o2-Ks": 0,
                                      "no2-ID":"no2",
                                      "no2-Ks" : 0,
                                      "no3-ID": "no3",
                                      "no3-Ks": 0,
                                      "mu_max-ID": "growth",
                                      "mu_max": 0.00028,
                                      "yield-ID": "yield",
                                      "yield": 0.61,
                                      "decay-ID": "decay",
                                      "decay": 0,
                                      "anoxic-ID": "anoxic",
                                      "anoxic": 0,
                                      "maintain-ID": "maintain",
                                      "maintain": 0,
                                      "epsyield-ID": "epsyield",
                                      "epsyield": 0,
                                      "epsdens-ID": "epsdens",
                                      "epsdens": 0},
                                "division_strategy": {
                                    "name": "divide_coccus",
                                    "diameter": 1.36
                                },
                            "diameter": 1,
                            "density": 150,
                            "outer_diameter": 1,
                            "morphology": "coccus",
                            "description": "Slow growing, but has a T6SS"
                            }
        self.dlg.taxaTable.clear()
        self._populateTaxaTable()
    def on_load_taxa_clicked(self):
        # Open a file dialog and get the selected file path
        file_path, _ = QFileDialog.getOpenFileName(self.Dialog, "Select a File", "", "Taxa Library (*.json);;All Files (*)")

        # If a file was selected, update the label
        if file_path:
            with open(file_path) as f:
                self.taxa_info = json.load(f)
            self.dlg.taxaTable.clear()
            self.dlg.growthTable.clear()
            self._populateTaxaTable()

    def taxaTableClicked(self, row, column):
        #if column == 6:
        name = self.dlg.taxaTable.item(row,0).text()
        growth_strat = self.taxa_info[name]['growth_strategy']
        self._populateGrowthTable(name,growth_strat)



    def _populateGrowthTable(self,bugname,growth_strat):
        self.dlg.growthTable.clear()
        if growth_strat['name'] == 'growth_het':
            self._populateGrowthTable_growth_het(bugname,growth_strat)
        else:
            pass

    # {'name': 'growth_het', 'sub-ID': 'sub', 'sub-Ks': 3.5e-05, 'o2-ID': 'o2', 'o2-Ks': 0, 'no2-ID': 'no2', 'no2-Ks': 0,
    # 'no3-ID': 'no3', 'no3-Ks': 0, 'mu_max-ID': 'growth', 'mu_max': 0.00028, 'yield-ID': 'yield', 'yield': 0.61,
    # 'decay-ID': 'decay', 'decay': 0, 'anoxic-ID': 'anoxic', 'anoxic': 0, 'maintain-ID': 'maintain', 'maintain': 0,
    # 'epsyield-ID': 'epsyield', 'epsyield': 0, 'epsdens-ID': 'epsdens', 'epsdens': 0}
    def _populateGrowthTable_growth_het(self,bugname,growth_strat):
        self.dlg.growthTable.blockSignals(True)
        cols = ["Name", "Strat", "\u03BC max", "KS", "KO2", "KNO2", "KNO3", "Yield","Decay","Anoxic"]

        self.dlg.growthTable.setColumnCount(len(cols))
        self.dlg.growthTable.setHorizontalHeaderLabels(cols)

        self.dlg.growthTable.setRowCount(1)


        item = QTableWidgetItem(bugname)
        flags = item.flags()
        item.setFlags(flags & ~Qt.ItemFlag.ItemIsEditable)
        self.dlg.growthTable.setItem(0, 0, item)

        item = QTableWidgetItem(growth_strat["name"])
        flags = item.flags()
        item.setFlags(flags & ~Qt.ItemFlag.ItemIsEditable)
        self.dlg.growthTable.setItem(0,1,item)
        self.dlg.growthTable.setItem(0,2,QTableWidgetItem(str(growth_strat["mu_max"])))
        self.dlg.growthTable.setItem(0, 3, QTableWidgetItem(str(growth_strat["sub-Ks"])))
        self.dlg.growthTable.setItem(0, 4, QTableWidgetItem(str(growth_strat["o2-Ks"])))
        self.dlg.growthTable.setItem(0, 5, QTableWidgetItem(str(growth_strat["no2-Ks"])))
        self.dlg.growthTable.setItem(0, 6, QTableWidgetItem(str(growth_strat["no3-Ks"])))
        self.dlg.growthTable.setItem(0, 7, QTableWidgetItem(str(growth_strat["yield"])))
        self.dlg.growthTable.setItem(0, 8, QTableWidgetItem(str(growth_strat["decay"])))
        self.dlg.growthTable.setItem(0, 9, QTableWidgetItem(str(growth_strat["anoxic"])))


        self.dlg.growthTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.dlg.growthTable.blockSignals(False)

    def _populateTaxaTable(self):
        self.dlg.taxaTable.blockSignals(True)
        self.dlg.growthTable.blockSignals(True)
        cols = ["Name", "Diameter (microns)", "Outer Diameter", "Division Diameter", "Density", "Morphology",
                "Growth Model", "Description", ]
        self.dlg.taxaTable.setColumnCount(len(cols))
        self.dlg.taxaTable.setHorizontalHeaderLabels(cols)
        self.dlg.taxaTable.setRowCount(len(self.taxa_info))

        for i, taxon in enumerate(self.taxa_info.keys()):
            name = taxon
            row = i
            self.dlg.taxaTable.setItem(row, 0, QTableWidgetItem(name))
            self.dlg.taxaTable.setItem(row, 1, QTableWidgetItem(str(self.taxa_info[taxon]['diameter'])))
            self.dlg.taxaTable.setItem(row, 2, QTableWidgetItem(str(self.taxa_info[taxon]['outer_diameter'])))
            self.dlg.taxaTable.setItem(row, 3,
                                       QTableWidgetItem(str(self.taxa_info[taxon]['division_strategy']["diameter"])))
            self.dlg.taxaTable.setItem(row, 4, QTableWidgetItem(str(self.taxa_info[taxon]['density'])))

            item = QTableWidgetItem(self.taxa_info[taxon]['morphology'])
            flags = item.flags()
            item.setFlags(flags & ~Qt.ItemFlag.ItemIsEditable)
            self.dlg.taxaTable.setItem(row, 5, item )

            item = QTableWidgetItem(self.taxa_info[taxon]['growth_strategy']['name'])
            flags = item.flags()
            item.setFlags(flags & ~Qt.ItemFlag.ItemIsEditable)
            self.dlg.taxaTable.setItem(row, 6, item )
            if 'description' in self.taxa_info[taxon]:
                self.dlg.taxaTable.setItem(row, 7, QTableWidgetItem(self.taxa_info[taxon]['description']))
            else:
                self.dlg.taxaTable.setItem(row, 7, QTableWidgetItem(""))
        # self.dlg.taxaTablesetSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.dlg.taxaTable.resizeColumnToContents(0)
        self.dlg.taxaTable.resizeColumnToContents(1)
        self.dlg.taxaTable.resizeColumnToContents(2)
        self.dlg.taxaTable.resizeColumnToContents(3)
        self.dlg.taxaTable.resizeColumnToContents(4)
        self.dlg.taxaTable.resizeColumnToContents(5)
        self.dlg.taxaTable.resizeColumnToContents(6)

        # Make the last column stretch
        header = self.dlg.taxaTable.horizontalHeader()
        header.setSectionResizeMode(7, header.ResizeMode.Stretch)
        self.dlg.taxaTable.setStyleSheet("""
                            QTableWidget::item:selected {
                                background: #00ff0000; /* Keep the cell's background color visible */
                                border: 1px solid blue;  /* Add a blue border around the selected item */
                            }
                            QTableWidget::item {
                                selection-color: black;  /* Text color for selected cells */
                                selection-background-color: transparent;
                            }
                        """)
        self.dlg.taxaTable.blockSignals(False)
        self.dlg.growthTable.blockSignals(False)
    def exec(self):
        return self.Dialog.exec()