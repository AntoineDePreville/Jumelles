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
import json

import requests
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import *
from qgis.utils import iface

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .jumelles_dialog import JumellesDialog
import os.path
import geopandas as gpd


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
        self.dlg.show()
        # Run the dialog event loop
        self.ui.pushButton_rechercher = self.dlg.exec_()
        # See if OK was pressed
        if self.ui.pushButton_rechercher:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            dataOffres = gpd.read_file('/home/antoine/Desktop/offres.gpkg')
            inputOffre = self.ui.lineEdit_offre.text()

            # Donnes à partir des parcelles et communes
            gurl = "https://vector.sitg.ge.ch/arcgis/rest/services/Hosted/CAD_PARCELLE_MENSU/FeatureServer"
            dataParcelles = self.readDataParcelles(gurl)
            inputParcelle = self.ui.lineEdit_parcelle.text()

            communesLayer = iface.activeLayer()
            featComm = communesLayer.getFeatures
            for f in featComm:
                dataComm = f["COMMUNE"]
                inputCommune = self.ui.lineEdit_commune.text()
                if inputCommune != '':
                    if dataComm.__contains__(int(inputCommune)):
                        self.ui.textEdit_resultats.setText(inputCommune)
                    else:
                        self.ui.textEdit_resultats.setText("Erreur: la commune n'existe pas")
                else:
                    self.ui.textEdit_resultats.setText("ENREGISTREZ UNE RECHERCHE SVP")
                    print("ERROR")
                self.ui.lineEdit_commune.clear()

            parcelles_col = dataParcelles['no_parcell']
            parcelles_list = dataParcelles.tolist

            dossierLayer = iface.activeLayer()
            features = dossierLayer.getFeatures
            for f in features:
                dataDossiers = f["Mandat"]
                inputDossier = self.ui.lineEdit_dossier.text()
                if inputDossier != '':
                    if dataDossiers.__contains__(int(inputDossier)):
                        print(int(inputDossier))
                        self.ui.textEdit_resultats.setText(inputDossier)
                    else:
                        self.ui.textEdit_resultats.setText("Erreur: le dossier n'existe pas")
                else:
                    self.ui.textEdit_resultats.setText("ENREGISTREZ UNE RECHERCHE SVP")
                    print("ERROR")
                self.ui.lineEdit_dossier.clear()

            if inputParcelle != '':
                containsValParcelles = parcelles_col.values.__contains__(int(inputParcelle))
                if containsValParcelles:
                    for i in range(0, len(parcelles_list)):
                        indexParc = parcelles_list.index(int(inputParcelle))
                        if parcelles_list[i] == int(inputParcelle):
                            self.ui.textEdit_resultats.setText(
                                f'{communes_list[indexParc]} - {parcelles_list[indexParc]}')
                else:
                    self.ui.textEdit_resultats.setText("ERREUR: LA PARCELLE N'EXISTE PAS")

            if inputOffre != '':
                if dataOffres['Num_offre'].__contains__(int(inputOffre)):
                    self.ui.textEdit_resultats.setText(dataOffres['Num_offre'].get(int(inputOffre) - 1))
                else:
                    self.ui.textEdit_resultats.setText("Erreur: l'offre n'existe pas")

            elif inputCommune != '':
                containsValCommunes = communes_col.values.__contains__(str(inputCommune))
                if containsValCommunes:
                    for i in range(0, len(parcelles_list)):
                        indexComm = communes_list.index(str(inputCommune))
                        if communes_list[i] == str(inputCommune):
                            self.ui.textEdit_resultats.setText(
                                f'{communes_list[indexComm]} - {parcelles_list[indexComm]}')
                else:
                    self.ui.textEdit_resultats.setText("ERREUR: LA COMMUNE N'EXISTE PAS")



            self.ui.lineEdit_offre.clear()
            self.ui.lineEdit_parcelle.clear()

    def readDataParcelles(self, url):
        wurl = [url]
        folder = '/home/antoine/.local/share/QGIS/QGIS3/profiles/default/python/plugins/Jumelles'

        for i in wurl:
            params = {'f': 'json'}
            response = requests.post(i, params)
            result = json.loads(response.text)
            service_name = i.split('FeatureServer')[0].split('/')[-2]

            for j in result['layers']:
                file_name = j['name'].lower().replace(' ', '_').replace('-', '').replace('__', '_')
                id = j['id']
                layer_url = f'{i}/{id}'
                query_url = f'{layer_url}/query'
                params = {"f": 'json'}
                response = requests.post(layer_url, params)
                result = json.loads(response.text)
                id_field = result['objectIdField']
                params = {"f": 'json', "returnCountOnly": 'true', "where": '1=1'}
                response = requests.post(query_url, params)
                result = json.loads(response.text)
                records = result['count']
                # print(f'{j["name"]} ({j["id"]}) - ({records} records)')
                rec_dl = 0
                object_id = -1
                geojson = {"type": "FeatureCollection", "features": []}

                while rec_dl < records:
                    params = {"f": 'geojson', "outFields": '*', "outSR": 2056, "returnGeometry": 'true',
                              "where": f'{id_field} > {object_id}'}
                    response = requests.get(query_url, params)
                    result = json.loads(response.text)

                    if len(result['features']):
                        geojson['features'] += result['features']
                        rec_dl += len(result['features'])
                        object_id = result['features'][len(result['features']) - 1]['properties'][id_field]
                    else:
                        print("NO")
                        break

                    # if rec_dl != records:
                    # print(
                    # f'--- ### Note, the record count for the feature layer ({j["name"]}) is incorrect - this is a bug in the service itself ### ---')
                    # print('-' * 50)

                    output_file = os.path.join(folder, f'{file_name}.geojson')
                    with open(output_file, 'w') as f:
                        f.write(json.dumps(geojson, indent=2))

                    gdf = gpd.read_file(output_file)
                    file = gdf.to_file(f'{file_name}.shp')
                    # data = gpd.read_file(f'{folder}/{file_name}.shp')
                    return file