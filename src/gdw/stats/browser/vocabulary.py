# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.app.schema.vocabulary import IVocabularyFactory
from z3c.sqlalchemy import getSAWrapper
import grokcore.component as grok
from gites.db.content import Province, MaisonTourisme, Commune, TypeHebergement


class ClassementVocabulary(grok.GlobalUtility):
    implements(IVocabularyFactory)
    grok.name('stats.classement')

    def __call__(self, context):
        items = []
        for epis in range(0, 5):
            items.append(SimpleTerm(epis,
                                    epis,
                                    epis))
        return SimpleVocabulary(items)


class ProvinceVocabulary(grok.GlobalUtility):
    implements(IVocabularyFactory)
    grok.name('stats.province')

    def __call__(self, context):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        items = []
        query = session.query(Province).order_by(Province.prov_nom)
        for province in query:
            items.append(SimpleTerm(province.prov_pk,
                                    province.prov_pk,
                                    province.prov_nom))
        session.close()
        return SimpleVocabulary(items)


class CommuneVocabulary(grok.GlobalUtility):
    implements(IVocabularyFactory)
    grok.name('stats.commune')

    def __call__(self, context):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        items = []
        query = session.query(Commune.com_nom).distinct().order_by(Commune.com_nom)
        for commune in query:
            items.append(SimpleTerm(commune.com_nom,
                                    commune.com_nom,
                                    commune.com_nom))
        return SimpleVocabulary(items)


class MaisonTourismeVocabulary(grok.GlobalUtility):
    implements(IVocabularyFactory)
    grok.name('stats.maisontourisme')

    def __call__(self, context):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        items = []
        query = session.query(MaisonTourisme.mais_pk, MaisonTourisme.mais_nom)
        query = query.order_by(MaisonTourisme.mais_nom)
        for maison in query:
            items.append(SimpleTerm(maison.mais_pk,
                                    maison.mais_pk,
                                    maison.mais_nom))
        return SimpleVocabulary(items)


class TypeHebergementVocabulary(grok.GlobalUtility):
    implements(IVocabularyFactory)
    grok.name('stats.hebtype')

    def __call__(self, context):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        items = []
        query = session.query(TypeHebergement.type_heb_pk, TypeHebergement.type_heb_nom)
        query = query.order_by(TypeHebergement.type_heb_nom)
        for typeHeb in query:
            items.append(SimpleTerm(typeHeb.type_heb_pk,
                                    typeHeb.type_heb_pk,
                                    typeHeb.type_heb_nom))
        return SimpleVocabulary(items)
