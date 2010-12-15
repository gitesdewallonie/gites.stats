# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
#from sets import Set
#from dateutil.relativedelta import relativedelta
from five import grok
from zope.interface import Interface
from z3c.form.form import Form, EditForm
from z3c.form import field, button
from z3c.sqlalchemy import getSAWrapper
from plone.z3cform.layout import FormWrapper
from Products.Five.browser.pagetemplatefile import BoundPageTemplate, ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from gites.db.content import Hebergement
from gdw.stats.browser.interfaces import IHebFilterForm
from gdw.stats.visits import StatContainer


grok.templatedir('templates')
grok.context(Interface)


class StatViewlet(grok.Viewlet):
    grok.baseclass()
    grok.template('statviewlet')
    groupType = None

    title = None

    def stats(self):
        minDate = self.view.form_instance.dateRange[0]
        maxDate = self.view.form_instance.dateRange[1]
        hebPk = self.view.form_instance.hebPk
        return StatContainer(hebPk, minDate, maxDate, self.groupType)


class DailyStatViewlet(StatViewlet):
    grok.order(1)
    title = u'Statistique par jour'
    groupType = 'day'


class MonthlyStatViewlet(StatViewlet):
    grok.order(2)
    title = u'Statistique par mois'
    groupType = 'month'


class YearlyStatViewlet(StatViewlet):
    grok.order(3)
    title = u'Statistique par an'
    groupType = 'year'


class StatsContentViewletManager(grok.ViewletManager):
    grok.name('stats.content')

grok.viewletmanager(StatsContentViewletManager)


class StatForm(Form):
    """formulaire"""
    fields = field.Fields(IHebFilterForm)
    ignoreContext = True
    hebPk = None

    def findHeb(self, hebPk):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        query = session.query(Hebergement)
        query = query.filter(Hebergement.heb_pk == hebPk)
        return query.first()

    def update(self):
        self.stats = None
        super(StatForm, self).update()

    @button.buttonAndHandler(u'Analyser')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = EditForm.formErrorsMessage
            return
        hebPk = data.get('hebPk')
        minDate = data.get('date_min')
        maxDate = data.get('date_max')
        heb = self.findHeb(hebPk)
        if heb is None:
            msg = u'Hebergement %s introuvable' % hebPk
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return
        self.hebName = heb.heb_nom
        self.hebPk = hebPk
        self.dateRange = [minDate, maxDate]


class StatFormView(FormWrapper):
    """la view"""
    form = StatForm

    @property
    def stats(self):
        return self.form_instance.stats

    @property
    def hebName(self):
        return self.form_instance.hebName

    @property
    def period(self):
        dateRange = self.form_instance.dateRange
        return "du %s au %s" % (dateRange[0].strftime('%d-%m-%Y'),
                                dateRange[1].strftime('%d-%m-%Y'))

    def update(self):
        super(StatFormView, self).update()
        if self.form_instance.hebPk is not None:
            pt = ViewPageTemplateFile('templates/hebstat.pt')
            self.index = BoundPageTemplate(pt, self)
