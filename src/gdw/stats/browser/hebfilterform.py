# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from sets import Set
from dateutil.relativedelta import relativedelta
from z3c.form.form import Form, EditForm
from z3c.form import field, button
from z3c.sqlalchemy import getSAWrapper
from plone.z3cform.layout import FormWrapper
from Products.Five.browser.pagetemplatefile import BoundPageTemplate, ViewPageTemplateFile
from gites.db.content import Hebergement, LogItem
from gdw.stats.browser.interfaces import IHebFilterForm


class StatForm(Form):
    """formulaire"""
    fields = field.Fields(IHebFilterForm)
    ignoreContext = True

    def findHeb(self, hebPk):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        query = session.query(Hebergement)
        query = query.filter(Hebergement.heb_pk == hebPk)
        return query.one()

    def filterHebLogs(self, hebId, minDate, maxDate):
        wrapper = getSAWrapper('gites_wallons')
        session = wrapper.session
        maxDate = maxDate + relativedelta(days=1)
        query = session.query(LogItem)
        query = query.filter(LogItem.log_hebid == hebId)
        query = query.filter(LogItem.log_date >= minDate)
        query = query.filter(LogItem.log_date < maxDate)
        query = query.order_by()
        return query.all()

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
        hebId = heb.heb_id
        self.hebName = heb.heb_nom
        self.dateRange = [minDate, maxDate]
        logs = self.filterHebLogs(hebId, minDate, maxDate)
        stats = []
        if logs:
            log = logs.pop(0)
            for i in range(0, (maxDate - minDate).days + 1):
                day = minDate + relativedelta(days=i)
                stat = {'date': day, 'visit': 0, 'unique': 0}
                hosts = Set()
                while log.log_date.date() == day and logs:
                    stat['visit'] += 1
                    hosts.add(log.log_host)
                    log = logs.pop(0)
                stat['unique'] = len(hosts)
                stats.append(stat)
        self.stats = stats


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
        if self.form_instance.stats is not None:
            pt = ViewPageTemplateFile('templates/hebstat.pt')
            self.index = BoundPageTemplate(pt, self)
