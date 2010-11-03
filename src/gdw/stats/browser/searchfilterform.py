# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from z3c.form.form import Form, EditForm
from z3c.form import field, button
from z3c.sqlalchemy import getSAWrapper
from plone.z3cform.layout import FormWrapper
from gites.db.content import Hebergement, Province, Commune, TypeHebergement, MaisonTourisme
from gdw.stats.browser.interfaces import ISearchFilterForm
from gdw.stats.occupation import HebergementsOccupation
from Products.Five.browser.pagetemplatefile import BoundPageTemplate, ViewPageTemplateFile


class StatForm(Form):
    """formulaire"""
    fields = field.Fields(ISearchFilterForm)
    ignoreContext = True

    def filterHebs(self, data):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        query = session.query(Hebergement)
        if data.get('province') is not None:
            query = query.join('province')
            query = query.filter(Province.prov_pk == data.get('province'))
        if data.get('commune') is not None:
            query = query.join('commune')
            query = query.filter(Commune.com_nom == data.get('commune'))
        if data.get('hebType'):
            query = query.join('type')
            query = query.filter(TypeHebergement.type_heb_pk.in_(data.get('hebType')))
        if data.get('maisonTourisme'):
            query = query.join('maisonTourisme')
            query = query.filter(MaisonTourisme.mais_pk == data.get('maisonTourisme'))
        return query

    def update(self):
        self.occupation = None
        super(StatForm, self).update()

    @button.buttonAndHandler(u'Calculer')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = EditForm.formErrorsMessage
            return
        minDate = data.get('date_min')
        maxDate = data.get('date_max')
        hebergements = self.filterHebs(data)
        nombre_jour = data.get('nombre_jour')
        self.occupation = HebergementsOccupation(hebergements, minDate, maxDate, nombre_jour)


class StatFormView(FormWrapper):
    """la view"""
    form = StatForm

    @property
    def occupation(self):
        return self.form_instance.occupation

    def tauxOccupation(self):
        return "%.2f %%" % (self.occupation.taux * 100.0)

    def nombreJoursOccupes(self):
        return self.occupation.nombreJoursOccupes

    def hebergementConcernes(self):
        return self.occupation.hebergementCount

    def hebergementsActifCount(self):
        return self.occupation.hebergementsActifCount

    def hebergementsInactifCount(self):
        return self.occupation.hebergementsInactifCount

    def update(self):
        super(StatFormView, self).update()
        if self.form_instance.occupation is not None:
            pt = ViewPageTemplateFile('templates/occupation.pt')
            self.index = BoundPageTemplate(pt, self)
