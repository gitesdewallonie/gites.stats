# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from affinitic.db.interfaces import IPGDBInitialized
import grokcore.component as grok
from sqlalchemy import MetaData
from gites.db.initializer import GitesModel


@grok.subscribe(MetaData, IPGDBInitialized)
def dbInitialized(metadata, event):
    model = GitesModel()
    model.getModel(metadata)
