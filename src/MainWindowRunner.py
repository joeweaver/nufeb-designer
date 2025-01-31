from poisson import PoissonDisc
from MainWindow import Ui_MainWindow
from DialogAssignTaxa import Ui_Dialog
from TaxaLibraryRunner import TaxaLibraryRunner
from T6SSPairRunner import T6SSPairRunner
from DialogHelp import Ui_AboutDialog
from nufebmgr import NufebProject
from PyQt6 import  QtWidgets
from PyQt6.QtWidgets import QTableWidgetItem,  QFileDialog
from PyQt6.QtGui import QColor, QIntValidator, QPen
from PyQt6.QtCore import QPoint
import numpy as np
import json
import random


class MainWindowRunner():
    def __init__(self, MainWindow):
        with open('./config/default/sample_taxa.json') as f:
            self.taxa_info = json.load(f)
        self.all_valid = True
        self.t6ss_pairs = []
        self.bugColours = [QColor(27, 158, 119),
                           QColor(217, 95, 2),
                           QColor(117, 112, 179),
                           QColor(231, 41, 138),
                           QColor(102, 166, 30),
                           QColor(230, 171, 2),
                           QColor(166, 118, 29),
                           QColor(253, 191, 111),
                           QColor(106, 61, 154),
                           ]
        self.penColour = QColor()
        self.MainWindow = MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        self.load_taxa(self.taxa_info)
        self.setupTaxaTable()
        self.ui.tableWidget.cellClicked.connect(self.on_cell_clicked)
        self.ui.tableWidget.verticalHeader().sectionClicked.connect(self.on_row_clicked)
        self.ui.distributeRandomButton.clicked.connect(self.on_distribute_random_clicked)
        self.ui.distributeGridButton.clicked.connect(self.on_distribute_grid_clicked)
        self.ui.distributePoissonButton.clicked.connect(self.on_distribute_poisson_clicked)
        self.ui.clearDrawingButton.clicked.connect(self.on_clear_drawing)
        self.ui.assignTaxaProportionButton.clicked.connect(self.on_assign_clicked)
        self.ui.assignTaxaEvenlyButton.clicked.connect(self.on_assign_evenly)
        self.ui.clearTaxaAssignmentsButton.clicked.connect(self.on_clear_taxa_assignments)
        self.ui.applyDimensions.clicked.connect(self.on_apply_dimensions)
        #self.ui.widthText.editingFinished.connect(self.on_finished_width)
        self.ui.widthText.textChanged.connect(self.on_changed_dimensions)
        self.ui.lengthText.textChanged.connect(self.on_changed_dimensions)
        self.ui.viewScaleText.setDisabled(True)
        self.ui.applyDimensions.setDisabled(True)
        self.ui.actionView_Available.triggered.connect(self.on_taxa_library)
        self.ui.editTaxaButton.clicked.connect(self.on_edit_taxa)
        self.ui.actionAbout.triggered.connect(self.on_about)
        self.ui.actionType_VI_Secretion.triggered.connect(self.on_t6ss_pairing)
        self.ui.genProjectButton.clicked.connect(self.on_generate)
        self.ui.actionLoad_Edit_Taxa.triggered.connect(self.on_taxa_library)
        self.ui.actionExit.triggered.connect(self.MainWindow.close)
        self.ui.graphicsView.set_callback(self.graphics_clicked)
        pos_int_validator = QIntValidator(1, 500)



        # validation/robustness
        self.field_button_map = {
            self.ui.randomNumBactText: self.ui.distributeRandomButton,
            self.ui.poissonRadiusText: self.ui.distributePoissonButton,
            self.ui.gridRowsText: self.ui.distributeGridButton,
            self.ui.gridColsText: self.ui.distributeGridButton,
            self.ui.widthText: self.ui.applyDimensions,
            self.ui.lengthText: self.ui.applyDimensions
        }
        for field, button in self.field_button_map.items():
            field.setValidator(pos_int_validator)
            field.textChanged.connect(lambda text, f=field, b=button: self.validate_and_toggle_button(f, b))

        self.ui.runTimeText.setValidator(QIntValidator(1,7*24*60*60*10))
        self.ui.seedText.setValidator(QIntValidator(1,7*24*60*60*10))
        self.ui.runTimeText.textChanged.connect(lambda text, f=self.ui.runTimeText, b=None: self.validate_and_toggle_button(f, b))
        self.ui.seedText.textChanged.connect(
            lambda text, f=self.ui.seedText, b=None: self.validate_and_toggle_button(f, b))

        self.ui.genProjectButton.setEnabled(False)

    def graphics_clicked(self):
        self.set_gen_enabled()

    def validate_and_toggle_button(self, field, button):
        text = field.text()
        if button:
            button.setEnabled(field.hasAcceptableInput())
        if not field.hasAcceptableInput():
            # Invalid: red border and set all_valid to False
            field.setStyleSheet("border: 2px solid red;")
            self.all_valid = False
        else:
            # Valid: clear border and update all_valid
            field.setStyleSheet("")
            self.all_valid = self.all_valid or True
        self.set_gen_enabled()

    def set_gen_enabled(self):
        enabled = self.all_valid
        white, black, others = self.ui.graphicsView.point_info()

        self.ui.genProjectButton.setEnabled(self.all_valid & (others > 0) & (black < 1))

    def on_generate(self):
        with NufebProject() as prj:
            directory = QFileDialog.getExistingDirectory(self.MainWindow, "Select Directory")

            self.ui.graphicsView.save(f'{directory}/layout.png')

            prj.use_seed(int(self.ui.seedText.text()))
            prj.set_box(x=int(self.ui.widthText.text()),
                        y=int(self.ui.lengthText.text()),
                        z=int(self.ui.ceilText.text()))
            prj.set_taxa(self.taxa_info)
            mappings = self.taxa_colors()
            prj.simple_image_layout(f'{directory}/layout.png',mappings)
            prj.set_track_abs()
            prj.enable_thermo_output(timestep=1)

            # use self.t6ss_pairs which is a list of (attacker,vuln)' tuples
            # for every unique vuln, we need to define an intoxicated group
            # for every attacker, we create it along with an effector
            # for every paring, we create a new vuln entry associated with the attacker's effector

            vulns =[]
            attackers = []
            for pairing in self.t6ss_pairs:
                attacker, vuln = pairing
                vulns.append(vuln)
                attackers.append(attacker)
            for vuln in set(vulns):
                prj.add_lysis_group_by_json(f'intoxicated_{vuln}',{'name':f'intoxicated_{vuln}','releases':'sub','rate':'2e-3','percent':'0.2'})
            for attacker in set(attackers):
                prj.arm_t6ss(taxon=attacker, effector=f'toxin_{attacker}', harpoon_len=1.3e-6, cooldown=100)
            for pairing in self.t6ss_pairs:
                attacker, vuln = pairing
                prj.vuln_t6ss(taxon=vuln, effector=f'toxin_{attacker}', prob=1, to_group=f'intoxicated_{vuln}')

            runtime = int(self.ui.runTimeText.text())
            runtime_units = self.ui.simTimeUnits.currentText()
            conversions={'Seconds': 1,
                         'Minutes': 60,
                         'Hours': 60*60,
                         'Days': 60*60*24}
            runtime_s = runtime*conversions[runtime_units]
            prj.set_runtime(runtime_s)
            # write the actual inputs to NUFEB
            atom_in, inputscript = prj.generate_case()



            with open(f'{directory}/atom.in', "w") as outf:
                outf.write(atom_in)
            with open(f'{directory}/inputscript.nufeb', "w") as outf:
                outf.write(inputscript)

    def taxa_colors(self):
        mapping = {}
        for rowNum in range(self.ui.tableWidget.rowCount()):
            item = self.ui.tableWidget.item(rowNum, 2)
            taxa_name = self.ui.tableWidget.item(rowNum, 0).text()
            taxa_rgb = f'{item.background().color().rgb():06X}'
            mapping[taxa_rgb] = taxa_name
        return mapping

    def on_about(self):
        Dialog = QtWidgets.QDialog()
        dlg = Ui_AboutDialog()
        dlg.setupUi(Dialog)
        Dialog.exec()

    def on_t6ss_pairing(self):
        t6ssPairDlg = T6SSPairRunner(self.taxa_info,self.t6ss_pairs)
        result = t6ssPairDlg.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.t6ss_pairs = t6ssPairDlg.get_pairings()



    def do_taxa_library_dlg(self):
        taxaLibraryDlg = TaxaLibraryRunner(self.taxa_info)

        result = taxaLibraryDlg.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:

            self.taxa_info = taxaLibraryDlg.taxa_info
            self.ui.tableWidget.clear()
            self.load_taxa(self.taxa_info)
            self.setupTaxaTable()
            self.ui.graphicsView.clear()

    def on_edit_taxa(self):
        self.do_taxa_library_dlg()
    def on_taxa_library(self):
        self.do_taxa_library_dlg()

    def on_apply_dimensions(self):
        if int(self.ui.widthText.text()) > 500:
            self.ui.widthText.setText("500")
        if int(self.ui.lengthText.text()) > 500:
            self.ui.lengthText.setText("500")
        self.ui.graphicsView.set_x(int(self.ui.widthText.text()))
        self.ui.graphicsView.set_y(int(self.ui.lengthText.text()))
        self.ui.graphicsView.clear_and_resize()
        self.ui.applyDimensions.setDisabled(True)
        self.ui.viewScaleText.setText(str(self.ui.graphicsView.scale))
    def on_changed_dimensions(self):
        #self.ui.graphicsView.set_x(int(self.ui.widthText.text()))
        self.ui.applyDimensions.setDisabled(False)

    def on_clear_taxa_assignments(self):
        for i, j in np.ndindex(self.ui.graphicsView.unscaled_points.shape):
            if self.ui.graphicsView.unscaled_points[i, j] != 0xFFFFFFFF:
                color = 0xFF000000
                pen = QPen(color)
                self.ui.graphicsView.unscaled_points[i,j] = color
                self.ui.graphicsView.paint_point(QPoint(i*self.ui.graphicsView.scale,j*self.ui.graphicsView.scale),pen)
    def on_assign_evenly(self):
        for i, j in np.ndindex(self.ui.graphicsView.unscaled_points.shape):
            if self.ui.graphicsView.unscaled_points[i, j] == 0xFF000000:
                color = random.choices(self.bugColours[0:self.ui.tableWidget.rowCount()-1], k=1)[0]
                pen = QPen(color)
                self.ui.graphicsView.unscaled_points[i,j] = color.rgba()
                self.ui.graphicsView.paint_point(QPoint(i*self.ui.graphicsView.scale,j*self.ui.graphicsView.scale),pen)

    def on_assign_clicked(self):
        Dialog = QtWidgets.QDialog()
        dlg = Ui_Dialog()
        dlg.setupUi(Dialog)
        cols = ["Name", "Abundance"]
        dlg.tableWidget.setColumnCount(len(cols))
        dlg.tableWidget.setHorizontalHeaderLabels(cols)
        dlg.tableWidget.setRowCount(len(self.taxa_info))
        for i, taxon in enumerate(self.taxa_info.keys()):
            name = taxon
            row = i
            dlg.tableWidget.setItem(row, 0, QTableWidgetItem(name))
            dlg.tableWidget.setItem(row, 1, QTableWidgetItem("0"))
        # self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        dlg.tableWidget.resizeColumnToContents(0)
        # Make the last column stretch
        header = dlg.tableWidget.horizontalHeader()
        header.setSectionResizeMode(1, header.ResizeMode.Stretch)
        result = Dialog.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            total = 0
            for row in range(dlg.tableWidget.rowCount()):
                item = dlg.tableWidget.item(row, 1)
                if item is not None and item.text().isdigit():
                    total += int(item.text())  # Or float(item.text()) for decimals
            proportions = []
            for row in range(dlg.tableWidget.rowCount()):
                item = dlg.tableWidget.item(row, 1)
                if item is not None and item.text().isdigit():
                    if total== 0:
                        proportions.append(0)
                    else:
                        proportions.append(int(item.text())/total)
            for i, j in np.ndindex(self.ui.graphicsView.unscaled_points.shape):
                if self.ui.graphicsView.unscaled_points[i, j] == 0xFF000000:
                    color = random.choices(self.bugColours[0:len(proportions)], weights=proportions, k=1)[0]
                    pen = QPen(color)
                    self.ui.graphicsView.unscaled_points[i, j] = color.rgba()
                    self.ui.graphicsView.paint_point(QPoint(i * self.ui.graphicsView.scale, j * self.ui.graphicsView.scale), pen)


    def on_row_clicked(self, index):
        self.ui.graphicsView.setColour(self.ui.tableWidget.item(index,2).background().color())

    def on_cell_clicked(self, row, column):
        self.ui.graphicsView.setColour(self.ui.tableWidget.item(row,2).background().color())

    def load_taxa(self,taxa_info):
        self.taxa_info = taxa_info

    def setupTaxaTable(self):
        cols = ["Name", "Description", "Colour"]
        self.ui.tableWidget.setColumnCount(len(cols))
        self.ui.tableWidget.setHorizontalHeaderLabels(cols)
        self.ui.tableWidget.setRowCount(len(self.taxa_info)+1)
        self.ui.tableWidget.setItem(0, 0, QTableWidgetItem("unassigned"))
        self.ui.tableWidget.setItem(0, 1, QTableWidgetItem("To be assigned later, using 'assign taxa' button"))
        self.ui.tableWidget.setItem(0, 2, QTableWidgetItem(''))
        self.ui.tableWidget.item(0, 2).setBackground(QColor("black"))
        for i,taxon in enumerate(self.taxa_info.keys()):
            name = taxon
            row = i+1
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(name))
            if 'description' in self.taxa_info[taxon]:
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(self.taxa_info[taxon]['description']))
            else:
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(""))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(''))
            self.ui.tableWidget.item(row,2).setBackground(self.bugColours[i])
        #self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.tableWidget.resizeColumnToContents(0)
        self.ui.tableWidget.resizeColumnToContents(1)
        # Make the last column stretch
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(2, header.ResizeMode.Stretch)
        self.ui.tableWidget.setStyleSheet("""
            QTableWidget::item:selected {
                background: #00ff0000; /* Keep the cell's background color visible */
                border: 1px solid blue;  /* Add a blue border around the selected item */
            }
            QTableWidget::item {
                selection-color: black;  /* Text color for selected cells */
                selection-background-color: transparent;
            }
        """)

    def add_taxa_to_list(self):
        self.ui.tableWidget.setRowCount(self.ui.tableWidget.rowCount()+1)
        self.ui.tableWidget.setItem(0,0,QTableWidgetItem('Slow heterotroph'))

    def on_clear_drawing(self):
        self.ui.graphicsView.clear()

    def on_distribute_random_clicked(self):
        drawscale=self.ui.graphicsView.scale
        base = np.random.rand(int(self.ui.randomNumBactText.text()), 2)
        bugs_xy = np.round(base * np.array([(self.ui.graphicsView.x_microns-1)*drawscale,(self.ui.graphicsView.y_microns-1)*drawscale])).astype(int)
        for x,y in bugs_xy:
            self.ui.graphicsView.draw_point(QPoint(x,y))

    def on_distribute_poisson_clicked(self):
        drawscale=self.ui.graphicsView.scale
        width = self.ui.graphicsView.x_microns
        length = self.ui.graphicsView.y_microns
        r = int(self.ui.poissonRadiusText.text())
        poisson_disc = PoissonDisc(width, length, r)
        s = poisson_disc.sample()
        bugs_xy = np.floor(np.array(s) * drawscale).astype(int)
        for x,y in bugs_xy:
            self.ui.graphicsView.draw_point(QPoint(x,y))

    def on_distribute_grid_clicked(self):
        drawscale=self.ui.graphicsView.scale
        rows = int(self.ui.gridRowsText.text())
        cols = int(self.ui.gridColsText.text())
        width = self.ui.graphicsView.x_microns
        length = self.ui.graphicsView.y_microns
        x_spacing = width/(cols)
        y_spacing = length/(rows)

        x_coords = np.linspace(x_spacing / 2, width - x_spacing / 2, cols)
        y_coords = np.linspace(y_spacing / 2, length - y_spacing / 2, rows)
        x, y = np.meshgrid(x_coords, y_coords)
        points = np.column_stack((x.ravel(), y.ravel()))
        bugs_xy = np.round(points*drawscale).astype(int)
        for x,y in bugs_xy:
            self.ui.graphicsView.draw_point(QPoint(x,y))