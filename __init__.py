# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Jumelles
                                 A QGIS plugin
 Recherche des lieux ou des entités géographiques
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-04-26
        copyright            : (C) 2024 by Antoine de Préville
        email                : antoine.de_preville@bluewin.ch
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Jumelles class from file Jumelles.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .jumelles import Jumelles
    return Jumelles(iface)
