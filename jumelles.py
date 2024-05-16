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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import *
from qgis._core import QgsPoint, QgsRectangle, QgsProject
from qgis.utils import iface

# Initialize Qt resources from file resources.py
# from .resources import *
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
        self.ui.pushButton_rechercher.clicked.connect(self.run)
        self.ui.pushButton_arreter.clicked.connect(self.run)

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

        icon_path = '/home/antoine/.local/share/QGIS/QGIS3/profiles/default/python/plugins/jumelles/jumelles.png'
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

            self.ui.pushButton_annuler.clicked.connect(self.clear_all)  # clears the results widget
            self.ui.pushButton_nouvelleRecherche.clicked.connect(self.clear_all)  # idem
            self.ui.pushButton_arreter.clicked.connect(self.close)  # call the method close() to close the widget window

    def merge(self, arr, p, q, r):
        n1 = q - p + 1
        n2 = r - q
        l = [0]*n1
        k = [0]*n2
        for i in range(0, n1):
            l[i] = arr[p+i]

        for j in range(0, n2):
            k[j] = arr[q+1+j]

        i = 0
        j = 0
        n = p
        while i < n1 and j < n2:
            if l[i] <= k[j]:
                arr[n] = l[i]
                i += 1

            else:
                arr[n] = k[j]
                j += 1
            n += 1

        while i < n1:
            arr[n] = l[i]
            i += 1
            n += 1

        while j < n2:
            arr[n] = k[j]
            j += 1
            n += 1

    def sort(self, arr, p, r):
        if p < r:
            q = p + (r - p)//2
            self.sort(arr, p, q)
            self.sort(arr, q+1, r)
            self.merge(arr, p, q, r)

    def search_dossiers(self, arr, length, target):
        l = 0
        r = length - 1
        while l <= r:
            mid = (r + l) // 2
            if int(arr[mid]) < int(target):
                l = mid + 1
            elif int(arr[mid]) > int(target):
                r = mid - 1
            else:
                return self.ui.listWidget_resultats.addItem(f"Mandat {str(target)}")
        return self.ui.listWidget_resultats.addItem(f"Erreur: le mandat n'existe pas.")

    def dossiers(self, input):
        """'dossier()' finds each 'Mandat' stored in the layer's attribute table"""
        dossierLayer = QgsProject.instance().mapLayersByName("Dossiers — virtual_layer")[
            0]  # selects the good layer. In this case 'Dossiers - virtual layer'
        iface.setActiveLayer(dossierLayer)  # gets it active

        index = dossierLayer.fields().indexFromName("Mandat")
        list = [i.attributes()[index] for i in dossierLayer.getFeatures()]

        arr = np.array(list)
        length = len(arr)
        self.sort(arr, 0, length-1)
        result = self.search_dossiers(arr, length, input)
        self.ui.listWidget_resultats.addItem(result)
        self.ui.listWidget_resultats.itemDoubleClicked.connect(
            self.zoom_d)  # Accesses the zoom method that displays the corresponding map by choosing which directory to display

        self.ui.lineEdit_dossier.clear()

    def search_offres(self, list, length, target):
        left = 0
        right = length - 1

        while left <= right:
            mid = (left + right) // 2
            if int(list[mid][-3:]) < int(target):
                left = mid + 1
            elif int(list[mid][-3:]) > int(target):
                right = mid - 1
            else:
                return self.ui.listWidget_resultats.addItem(str(list[mid]))
        return self.ui.listWidget_resultats.addItem("Can't find the value.")

    def offres(self, input):
        """'offres()' finds each 'Num_offre' stored in the layer's attribute table"""
        df = QgsProject.instance().mapLayersByName("offres")[0]  # selects the good layer. In this case 'offres'
        iface.setActiveLayer(df)  # gets it active
        match_found = False
        if df is not None:
            match_found = True
            index = df.fields().indexFromName("Num_offre")
            list = []
            for f in df.getFeatures():
                val = f.attributes()[index]
                list.append(val)
            length = len(list)
            result = self.search_offres(list, length, input)

            self.ui.listWidget_resultats.addItem(result)
            self.ui.listWidget_resultats.itemDoubleClicked.connect(self.zoom_o)  # Accesses the zoom method that displays the corresponding map by choosing which directory to display
        # Error message in case you mistyped the right offer ;)
        if not match_found:
            self.ui.listWidget_resultats.addItem(f"Erreur: l'offre OF-000-{input} n'existe pas.")

        self.ui.lineEdit_offre.clear()

    def merge_parcelles(self, mat, p, q, r):
        n1 = q - p + 1
        n2 = r - q
        L = []
        K = []
        for i in range(0, n1):
            L[i] = mat[p + i]

        for j in range(0, n2):
            K[j] = mat[q + 1 + j]

        i = 0
        j = 0
        n = p
        while i < n1 and j < n2:
            if L[i] <= K[j]:
                mat[n] = L[i]
                i += 1

            else:
                mat[n] = K[j]
                j += 1
            n += 1

    def sort_parcelles(self, mat, p, r):
        if p < r:
            q = p + (r - p)//2
            self.sort_parcelles(mat, p, q)
            self.sort_parcelles(mat, q+1, r)
            self.merge_parcelles(mat, p, q, r)

    def search_parcelles(self, mat, length, target):
        left = 0
        right = length - 1

        while left <= right:
            mid = (left + right) // 2
            if int(mat[mid]) < int(target):
                left = mid + 1
            elif int(mat[mid]) > int(target):
                right = mid - 1
            else:
                return self.ui.listWidget_resultats.addItem(str(mat[mid]))
        return self.ui.listWidget_resultats.addItem("Can't find the value.")

    def parcelles(self, input):
        """'parcelles()' finds each 'no_parcelle' stored in the layer's attribute table"""
        parcellesLayer = QgsProject.instance().mapLayersByName("CAD_PARCELLE_MENSU")[
            0]  # selects the good layer. In this case 'CAD_PARCELLE_MENSU'
        iface.setActiveLayer(parcellesLayer)  # sets it active

        index1 = parcellesLayer.fields().indexFromName("no_parcelle")
        list1 = [i.attributes()[index1] for i in parcellesLayer.getFeatures()]

        index2 = parcellesLayer.fields().indexFromName("commune")
        list2 = [i.attributes()[index2] for i in parcellesLayer.getFeatures()]

        M = np.column_stack((list1, list2))

        length = len(M)
        self.sort_parcelles(M, 0, length-1)
        result = self.search_parcelles(M, length, input)
        self.ui.listWidget_resultats.addItem(result)
        self.ui.listWidget_resultats.itemDoubleClicked.connect(
                    self.zoom_p)  # Accesses the zoom method that displays the corresponding map by choosing which parcel to display

    def communes(self, input):
        """'communes()' finds each 'commune' stored in the layer's attribute table"""
        communesLayer = QgsProject.instance().mapLayersByName("CAD_PARCELLE_MENSU")[
            0]  # selects the good layer. In this case 'CAD_PARCELLE_MENSU'
        iface.setActiveLayer(communesLayer)  # gets it active
        featCommunes = communesLayer.getFeatures()  # gets the layer's features
        match_found = False
        # Looks for each value in the attribute table
        for f in featCommunes:
            if str(f['commune']).__contains__(input):
                match_found = True
                self.ui.listWidget_resultats.addItem(
                    f'{f["no_parcelle"]} - {f["commune"]}')  # Displays the parcel number along with the commune
                self.ui.listWidget_resultats.itemDoubleClicked.connect(
                    self.zoom_c)  # Accesses the zoom method that displays the corresponding map by choosing which parcel to display
        # error message in case you mistyped the right commune
        if not match_found:
            self.ui.listWidget_resultats.addItem(f"Erreur: la commune {input} n'existe pas.")

        self.ui.lineEdit_commune.clear()

    def adresses(self, input):
        """'adresses()' finds each 'NO_ADRESSE' stored in the layer's attribute table"""
        self.ui.listWidget_resultats.clear()
        adressesLayer = QgsProject.instance().mapLayersByName("CAD_ADRESSE")[
            0]  # select the good layer. In this case 'CAD_ADRESSE'
        iface.setActiveLayer(adressesLayer)
        featAdresses = adressesLayer.getFeatures()
        match_found = False
        # Looks for each value in the attribute table
        for f in featAdresses:
            if str(f['ADRESSE']).__contains__(input) or str(f['ADRESSE']).lower().__contains__(input) or str(
                    f['ADRESSE']).upper().__contains__(input):
                match_found = True
                self.ui.listWidget_resultats.addItem(
                    f'{f["ADRESSE"]} {f["NO_POSTAL"]} {f["COMMUNE"]}')  # Displays the address, zip code and commune
                self.ui.listWidget_resultats.itemDoubleClicked.connect(
                    self.zoom_a)  # Accesses the zoom method that displays the corresponding map by choosing which address to display

        # Error message in case you mistyped the right parcel ;)
        if not match_found:
            self.ui.listWidget_resultats.addItem(f"Erreur: l'adresse n'existe pas.")

    def parComm(self, inputParc, inputComm):
        """'parComm()' finds each 'no_parcelle' and 'commune' stored in the layer's attribute table"""
        self.ui.listWidget_resultats.clear()
        parcoLayer = QgsProject.instance().mapLayersByName("CAD_PARCELLE_MENSU")[
            0]  # select the good layer. In this case 'CAD_ADRESSE:CAD_ADRESSE'
        iface.setActiveLayer(parcoLayer)  # sets it active
        featParCo = parcoLayer.getFeatures()  # gets the layer's features
        match_found = False
        # Looks for each value in the attribute table
        for f in featParCo:
            if str(f['no_parcelle']) == inputParc and str(f['commune']).__contains__(inputComm):
                match_found = True
                self.ui.listWidget_resultats.addItem(
                    f'{f["no_parcelle"]} - {f["commune"]}')  # Displays the parcel along with the commune
                self.ui.listWidget_resultats.itemDoubleClicked.connect(self.zoom_c)
        # error message in case you mistyped the right parcel or commune
        if not match_found:
            self.ui.listWidget_resultats.addItem(f"Erreur: la parcelle {inputParc} - {inputComm} n'existe pas.")

    def zoom_p(self, item):
        """Diplays the map according to selection in the parcelle() method"""
        selected_item = item.text()
        layer = QgsProject.instance().mapLayersByName("CAD_PARCELLE_MENSU")[
            0]  # selects the good layer. In this case 'CAD_PARCELLE_MENSU'
        iface.setActiveLayer(layer)
        for f in layer.getFeatures():
            if selected_item == f"{f['no_parcelle']} - {f['commune']}":
                layer.removeSelection()
                layer.select(f.id())
                iface.mapCanvas().setExtent(f.geometry().boundingBox())
                iface.mapCanvas().refresh()
                break

    def zoom_c(self, item):
        """Diplays the map according to selection in the parcelle() method"""
        selected_item = item.text()
        layer = QgsProject.instance().mapLayersByName("CAD_PARCELLE_MENSU")[
            0]  # select the good layer. In this case 'CAD_PARCELLE_MENSU'
        iface.setActiveLayer(layer)
        for f in layer.getFeatures():
            if selected_item == f"{f['no_parcelle']} - {f['commune']}":
                layer.removeSelection()
                layer.select(f.id())
                iface.mapCanvas().setExtent(f.geometry().boundingBox())
                iface.mapCanvas().refresh()
                break

    def zoom_d(self, item):
        """Diplays the map according to selection in the dossiers() method"""
        selected_item = item.text()
        layer = QgsProject.instance().mapLayersByName("Dossiers — virtual_layer")[0]
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
        layer = QgsProject.instance().mapLayersByName("offres")[0]
        iface.setActiveLayer(layer)
        for f in layer.getFeatures():
            if selected_item == f['Num_offre']:
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
        layer = QgsProject.instance().mapLayersByName("CAD_ADRESSE")[
            0]  # select the good layer. In this case 'CAD_ADRESSE'
        iface.setActiveLayer(layer)
        for f in layer.getFeatures():
            if selected_item == f'{f["ADRESSE"]} {f["NO_POSTAL"]} {f["COMMUNE"]}':
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

    def clear_all(self):
        """Clears the results list"""
        self.ui.listWidget_resultats.clear()

    def close(self):
        """Closes the window"""
        self.ui.close()
