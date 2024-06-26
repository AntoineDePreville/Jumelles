# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Jumelles
                                 A QGIS plugin
 Recherche des lieux ou des entités géographiques
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-04-26
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Antoine de Préville
        email                : antoine.de_preville@bluewin.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import numpy as np
from PyQt5.QtCore import Qt
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import *
from qgis._core import QgsPoint, QgsRectangle, QgsProject
from qgis.utils import iface

# Import the code for the dialog
from .jumelles_dialog import JumellesDialog
import os.path


class Jumelles:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Jumelles_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Jumelles')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.ui = JumellesDialog()
        self.ui.pushButton_charger.clicked.connect(self.chargement)
        self.ui.pushButton_rechercher.clicked.connect(self.run)
        self.ui.pushButton_arreter.clicked.connect(self.run)

        self.running_flag = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Jumelles', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.dirname(__file__) + '/jumelles.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Jumelles'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Jumelles'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            self.first_start = False
            self.dlg = JumellesDialog()

        # show the dialog
        self.ui.show()
        # Run the dialog event loop
        result = self.ui.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # Call of all methods that perfom all the work + inputs from UI.
            inputOffres = self.ui.lineEdit_offre.text()
            inputDossiers = self.ui.lineEdit_dossier.text()
            inputParcelles = self.ui.lineEdit_parcelle.text()
            inputCommunes = self.ui.lineEdit_commune.text()
            inputAdresses = self.ui.lineEdit_adresse.text()

            if inputOffres != "":
                self.offres(inputOffres)
            elif inputDossiers != "":
                self.dossiers(inputDossiers)
            elif inputParcelles != "" and inputCommunes != "":
                self.parComm(inputParcelles, inputCommunes)
            elif inputParcelles != "":
                self.parcelles(inputParcelles)
            elif inputCommunes != "":
                self.communes(inputCommunes)
            elif inputAdresses != "":
                self.adresses(inputAdresses)

            self.ui.pushButton_annuler.clicked.connect(self.clear_fields)  # clears all fields
            self.ui.pushButton_nouvelleRecherche.clicked.connect(self.clear_results)  # clears results
            self.ui.pushButton_arreter.clicked.connect(self.close)  # call the method close() to close the widget window

    def chargement(self):
        progress = QProgressDialog("Chargement...", "Annuler", 0, 100)
        progress.setWindowTitle("Chargement")
        progress.setWindowModality(Qt.WindowModal)
        progress.setValue(0)
        progress.show()

        # Parcelles et communes
        parcellesLayer = QgsProject.instance().mapLayersByName("Parcelles")[0]

        index1_parcelles = parcellesLayer.fields().indexFromName("NO_PARCELLE")
        list1_parcelles = [i.attributes()[index1_parcelles] for i in parcellesLayer.getFeatures()]
        list1IntParcelles = [int(x) for x in list1_parcelles]

        index2_parcelles = parcellesLayer.fields().indexFromName("COMMUNE")
        list2_parcelles = [i.attributes()[index2_parcelles] for i in parcellesLayer.getFeatures()]
        list2StrParcelles = [str(y) for y in list2_parcelles]

        M_parcelles = np.column_stack((list1IntParcelles, list2StrParcelles))

        # Adresses
        adressesLayer = QgsProject.instance().mapLayersByName("Adresses")[0]
        index1_adresses = adressesLayer.fields().indexFromName("ADRESSE")
        list1_adresses = [i.attributes()[index1_adresses] for i in adressesLayer.getFeatures()]
        list1StrAdresses = [str(x) for x in list1_adresses]

        index2_adresses = adressesLayer.fields().indexFromName("NO_POSTAL")
        list2_adresses = [i.attributes()[index2_adresses] for i in adressesLayer.getFeatures()]
        list2IntAdresses = [int(y) for y in list2_adresses]

        index3_adresses = adressesLayer.fields().indexFromName("COMMUNE")
        list3_adresses = [i.attributes()[index3_adresses] for i in adressesLayer.getFeatures()]
        list3StrAdresses = [str(z) for z in list3_adresses]

        M_adresses = np.column_stack((list1StrAdresses, list2IntAdresses, list3StrAdresses))

        # Dossiers
        dossierLayer = QgsProject.instance().mapLayersByName("Dossiers")[0]
        index_dossiers = dossierLayer.fields().indexFromName("Mandat")
        list_dossiers = [i.attributes()[index_dossiers] for i in dossierLayer.getFeatures()]  # creates list
        lstStrDossiers = [str(x) for x in list_dossiers]
        arr_dossiers = np.array(lstStrDossiers)

        # Offres
        df = QgsProject.instance().mapLayersByName("Offres")[0]
        index_offres = df.fields().indexFromName("num_offre")
        list_offres = [i.attributes()[index_offres] for i in df.getFeatures()]  # creates list
        listStr = [str(x) for x in list_offres]
        arr_offres = np.array(listStr)

        n_parcelles = len(M_parcelles)
        n_adresses = len(M_adresses)
        n_dossiers = len(arr_dossiers)
        n_offres = len(arr_offres)

        def merge_sort_progress(arr, l, r, progress, total_steps):
            def merge(arr, left, mid, right):
                n1 = mid - left + 1
                n2 = right - mid
                L = arr[left:mid + 1]
                R = arr[mid + 1:right + 1]
                i = j = 0
                k = left
                while i < n1 and j < n2:
                    if L[i] <= R[j]:
                        arr[k] = L[i]
                        i += 1
                    else:
                        arr[k] = R[j]
                        j += 1
                    k += 1
                while i < n1:
                    arr[k] = L[i]
                    i += 1
                    k += 1
                while j < n2:
                    arr[k] = R[j]
                    j += 1
                    k += 1
                return arr

            def merge_sort(arr, l, r, progress, total_steps):
                if l < r:
                    mid = (l + r) // 2
                    merge_sort(arr, l, mid, progress, total_steps)
                    merge_sort(arr, mid + 1, r, progress, total_steps)
                    merge(arr, l, mid, r)
                    progress.setValue(progress.value() + 1)
                    if progress.wasCanceled():
                        return False
                return arr

            return merge_sort(arr, l, r, progress, total_steps)

        total_steps = n_parcelles + n_adresses + n_dossiers + n_offres
        progress.setMaximum(total_steps)

        merge_sort_progress(M_parcelles[:, 0].astype(int), 0, n_parcelles - 1, progress, total_steps)
        merge_sort_progress(M_adresses[:, 0].astype(str), 0, n_adresses - 1, progress, total_steps)
        merge_sort_progress(arr_dossiers.astype(str), 0, n_dossiers - 1, progress, total_steps)
        merge_sort_progress(arr_offres.astype(str), 0, n_offres - 1, progress, total_steps)

        progress.close()

        if self.running_flag == 'dossiers':
            return arr_dossiers
        elif self.running_flag == 'offres':
            return arr_offres
        elif self.running_flag == 'parcelles' or self.running_flag == 'communes' or self.running_flag == 'parcomm':
            return M_parcelles
        elif self.running_flag == 'adresses':
            return M_adresses

    def search_dossiers(self, arr, length, target):
        """this method searches the matches between input and attribute table for 'Dossiers'"""
        """left = 0
        right = length - 1

        # makes the research according to binary search algorithm
        while left <= right:
            mid = (right + left) // 2
            if str(arr[mid]) < str(target):
                left = mid + 1
            elif str(arr[mid]) > str(target):
                right = mid - 1
            else:
                return self.ui.listWidget_resultats.addItem(f"Mandat {str(arr[mid])}")
        return self.ui.listWidget_resultats.addItem(f"Erreur: le mandat n'existe pas.")
"""

        n = len(arr) - 1
        found = False
        for i in range(0, n):
            if str(arr[i]) == (str(target)):
                found = True
                self.ui.listWidget_resultats.addItem(f"Mandat {str(arr[i])}")
                break
        if not found:
            return self.ui.listWidget_resultats.addItem("Erreur: le dossier n'existe pas.")

    def dossiers(self, input):
        """'dossier()' finds each 'Mandat' stored in the layer's attribute table"""
        self.running_flag = 'dossiers'
        dossierLayer = QgsProject.instance().mapLayersByName("Dossiers")[
            0]  # selects the good layer. In this case 'Dossiers'
        iface.setActiveLayer(dossierLayer)  # gets it active
        arr = self.chargement()
        length = len(arr)
        result = self.search_dossiers(arr, length, input)
        self.ui.listWidget_resultats.addItem(result)
        self.ui.listWidget_resultats.itemDoubleClicked.connect(
            self.zoom_d)  # Accesses the zoom method that displays the corresponding map by choosing which directory
        # to display

    def search_offres(self, arr, length, target):
        """this method searches the matches between input and attribute table for 'Offres'"""
        """
        left = 0
        right = length - 1
        while left <= right:
            mid = (left + right) // 2
            if str(arr[mid][-5:]).replace('-', '') < str(target):
                left = mid + 1
            elif str(arr[mid][-5:]).replace('-', '') < str(target):
                right = mid - 1
            else:
                return self.ui.listWidget_resultats.addItem(str(arr[mid]))
        return self.ui.listWidget_resultats.addItem("Erreur: l'offre n'existe pas.")
        """
        n = length
        found = False
        for i in range(0, n):
            if str(arr[i]).replace('-', '').lower().__contains__(str(target)) or str(arr[i]).lower().__contains__(
                    str(target)) or str(arr[i]).replace('-', '').upper().__contains__(str(target)) or str(
                    arr[i]).upper().__contains__(str(target)):
                found = True
                self.ui.listWidget_resultats.addItem(str(arr[i]))
                break

        if not found:
            return self.ui.listWidget_resultats.addItem("Erreur: l'offre n'existe pas.")

    def offres(self, input):
        self.running_flag = 'offres'
        df = QgsProject.instance().mapLayersByName("Offres")[0]  # selects the good layer. In this case 'offres'
        iface.setActiveLayer(df)  # gets it active

        arr_offres = sorted(self.chargement())
        length = len(arr_offres)
        self.ui.listWidget_resultats.addItem(self.search_offres(arr_offres, length, input))
        self.ui.listWidget_resultats.itemDoubleClicked.connect(
            self.zoom_o)  # Accesses the zoom method that displays the corresponding map by choosing which directory to display

    def search_parcelles(self, mat, target):
        """this method searches the matches between input and attribute table for 'Parcelles'"""
        n = len(mat) - 1
        found = False

        for i in range(0, n):
            if int(mat[i][0]) == int(target):
                found = True
                self.ui.listWidget_resultats.addItem(f"{str(mat[i][0])} - {str(mat[i][1])}")
        if not found:
            return self.ui.listWidget_resultats.addItem("Erreur: la parcelle n'existe pas.")

    def parcelles(self, input):
        """'parcelles()' finds each 'no_parcelle' stored in the layer's attribute table"""
        self.ui.listWidget_resultats.clear()
        self.running_flag = 'parcelles'
        parcellesLayer = QgsProject.instance().mapLayersByName("Parcelles")[
            0]  # selects the good layer. In this case 'Parcelles'
        iface.setActiveLayer(parcellesLayer)  # sets it active

        M = self.chargement()
        self.ui.listWidget_resultats.addItem(self.search_parcelles(M, input))
        self.ui.listWidget_resultats.itemDoubleClicked.connect(
            self.zoom_p)  # Accesses the zoom method that displays the corresponding map by choosing which parcel to display

    def search_communes(self, mat, target):
        """this method searches the matches between input and attribute table for 'Communes'"""
        n = len(mat) - 1
        found = False
        for i in range(0, n):
            if str(mat[i][1]).__contains__(str(target)) or str(mat[i][1]).lower().__contains__(
                    str(target).lower()) or str(mat[i][1]).upper().__contains__(str(target).upper()):
                found = True
                self.ui.listWidget_resultats.addItem(f"{str(mat[i][0])} - {str(mat[i][1])}")
        if not found:
            return self.ui.listWidget_resultats.addItem("Erreur: la commune n'existe pas.")

    def communes(self, input):
        """'communes()' finds each 'commune' stored in the layer's attribute table"""
        self.ui.listWidget_resultats.clear()
        self.running_flag = 'communes'
        communesLayer = QgsProject.instance().mapLayersByName("Parcelles")[
            0]  # selects the good layer. In this case 'Parcelles'
        iface.setActiveLayer(communesLayer)  # gets it active

        M = self.chargement()
        self.ui.listWidget_resultats.addItem(self.search_communes(M, input))
        self.ui.listWidget_resultats.itemDoubleClicked.connect(
            self.zoom_p)

    def search_adresses(self, mat, target):
        """this method searches the matches between input and attribute table for 'Adresses'"""
        n = len(mat) - 1
        found = False
        for i in range(0, n):
            if (str(mat[i, 0]).__contains__(str(target))) or (
                    str(mat[i, 0]).lower().__contains__(str(target).lower())) or (
                    str(mat[i, 0]).upper().__contains__(str(target).upper())):
                found = True
                self.ui.listWidget_resultats.addItem(f"{str(mat[i][0])} - {str(mat[i][1])} {str(mat[i][2])}")
        if not found:
            return self.ui.listWidget_resultats.addItem("Erreur: l'adresse n'existe pas.")

    def adresses(self, input):
        self.ui.listWidget_resultats.clear()
        self.running_flag = 'adresses'
        """'adresses()' finds each 'NO_ADRESSE' stored in the layer's attribute table"""
        adressesLayer = QgsProject.instance().mapLayersByName("Adresses")[
            0]  # select the good layer. In this case 'Adresses'
        iface.setActiveLayer(adressesLayer)
        M_adresses = self.chargement()
        self.ui.listWidget_resultats.addItem(self.search_adresses(M_adresses, input))

        self.ui.listWidget_resultats.itemDoubleClicked.connect(
            self.zoom_a)  # Accesses the zoom method that displays the corresponding map by choosing which address to display

        self.ui.listWidget_resultats.itemDoubleClicked.connect(
            self.zoom_a)  # Accesses the zoom method that displays the corresponding map by choosing which address to display

    def search_parcomm(self, mat, target1, target2):
        """this method searches the matches between input and attribute table for 'Parcelles' and 'Communes'"""
        n = len(mat) - 1
        found = False
        for i in range(0, n):
            if (str(mat[i][1]).__contains__(str(target2)) or str(mat[i][1]).lower().__contains__(
                    str(target2).lower()) or str(mat[i][1]).upper().__contains__(
                    str(target2).upper())) and (int(mat[i][0]) == int(target1)):
                found = True
                self.ui.listWidget_resultats.addItem(f"{str(mat[i][0])} - {str(mat[i][1])}")
        if not found:
            return self.ui.listWidget_resultats.addItem("Erreur: la parcelle n'existe pas.")

    def parComm(self, inputParc, inputComm):
        """'parComm()' finds each 'no_parcelle' and 'commune' stored in the layer's attribute table"""
        self.ui.listWidget_resultats.clear()
        self.running_flag = 'parcomm'
        parcoLayer = QgsProject.instance().mapLayersByName("Parcelles")[
            0]  # select the good layer. In this case 'Parcelles'
        iface.setActiveLayer(parcoLayer)  # sets it active
        M_parcomm = self.chargement()
        self.ui.listWidget_resultats.addItem(self.search_parcomm(M_parcomm, inputParc, inputComm))
        self.ui.listWidget_resultats.itemDoubleClicked.connect(self.zoom_p)

    def zoom_p(self, item):
        """Diplays the map according to selection in the parcelle() method"""
        selected_item = item.text()
        layer = QgsProject.instance().mapLayersByName("Parcelles")[
            0]  # selects the good layer. In this case 'CAD_PARCELLE_MENSU'
        iface.setActiveLayer(layer)
        for f in layer.getFeatures():
            if selected_item == f"{f['NO_PARCELLE']} - {f['COMMUNE']}":
                layer.removeSelection()
                layer.select(f.id())
                iface.mapCanvas().setExtent(f.geometry().boundingBox())
                iface.mapCanvas().refresh()
                break

    def zoom_c(self, item):
        """Diplays the map according to selection in the parcelle() method"""
        selected_item = item.text()
        layer = QgsProject.instance().mapLayersByName("Parcelles")[
            0]  # select the good layer. In this case 'CAD_PARCELLE_MENSU'
        iface.setActiveLayer(layer)
        for f in layer.getFeatures():
            if selected_item == f"{f['NO_PARCELLE']} - {f['COMMUNE']}":
                layer.removeSelection()
                layer.select(f.id())
                iface.mapCanvas().setExtent(f.geometry().boundingBox())
                iface.mapCanvas().refresh()
                break

    def zoom_d(self, item):
        """Diplays the map according to selection in the dossiers() method"""
        selected_item = item.text()
        layer = QgsProject.instance().mapLayersByName("Dossiers")[0]
        iface.setActiveLayer(layer)
        for f in layer.getFeatures():
            if selected_item == f"Mandat {f['Mandat']}":
                canvas = iface.mapCanvas()
                x = f.geometry().asPoint().x()
                y = f.geometry().asPoint().y()
                zoom_factor = 50.0
                rect = QgsRectangle(x - zoom_factor, y - zoom_factor, x + zoom_factor, y + zoom_factor)
                layer.select(f.id())
                canvas.setExtent(rect)
                canvas.refresh()
                break

    def zoom_o(self, item):
        """Diplays the map according to selection in the offres() method"""
        selected_item = item.text()
        layer = QgsProject.instance().mapLayersByName("Offres")[0]
        iface.setActiveLayer(layer)
        for f in layer.getFeatures():
            if selected_item == f['num_offre']:
                canvas = iface.mapCanvas()
                x = f.geometry().asPoint().x()
                y = f.geometry().asPoint().y()
                zoom_factor = 50.0
                rect = QgsRectangle(x - zoom_factor, y - zoom_factor, x + zoom_factor, y + zoom_factor)
                layer.select(f.id())
                canvas.setExtent(rect)
                QgsPoint(x, y)
                canvas.refresh()
                break

    def zoom_a(self, item):
        """Diplays the map according to selection in the adresse() method"""
        selected_item = item.text()
        layer = QgsProject.instance().mapLayersByName("Adresses")[
            0]  # select the good layer. In this case 'CAD_ADRESSE'
        iface.setActiveLayer(layer)
        for f in layer.getFeatures():
            if selected_item == f'{f["ADRESSE"]} - {f["NO_POSTAL"]} {f["COMMUNE"]}':
                canvas = iface.mapCanvas()
                x = f.geometry().asPoint().x()
                y = f.geometry().asPoint().y()
                zoom_factor = 50.0
                rect = QgsRectangle(x - zoom_factor, y - zoom_factor, x + zoom_factor, y + zoom_factor)
                layer.select(f.id())
                canvas.setExtent(rect)
                QgsPoint(x, y)
                canvas.refresh()
                break

    def clear_fields(self):
        """Clears all fields"""
        self.ui.lineEdit_offre.clear()
        self.ui.lineEdit_dossier.clear()
        self.ui.lineEdit_adresse.clear()
        self.ui.lineEdit_parcelle.clear()
        self.ui.lineEdit_commune.clear()

    def clear_results(self):
        """Clears results"""
        self.ui.listWidget_resultats.clear()

    def close(self):
        """Closes the window"""
        self.ui.close()
