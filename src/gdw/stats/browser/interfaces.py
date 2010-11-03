# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from zope.interface import Interface, invariant, Invalid
from zope.schema import Choice, Date, Int, Tuple


class ISearchFilterForm(Interface):

    @invariant
    def isLoginPartOfEmail(search):
        if search.date_min > search.date_max:
            raise Invalid("Date de début supérieure à la date de fin")

    date_min = Date(
        title=u"Date de début",
        description=u"",
        required=True)

    date_max = Date(
        title=u"Date de fin",
        description=u"",
        required=True)

    nombre_jour = Int(
        title=u"Nombre de jour inactif maximum",
        description=u"",
        default=1,
        required=False)

    classement = Choice(
        title=u"Classement",
        description=u"",
        required=False,
        vocabulary="stats.classement")

    province = Choice(
        title=u"Province",
        description=u"",
        required=False,
        vocabulary="stats.province")

    commune = Choice(
        title=u"Commune",
        description=u"",
        required=False,
        vocabulary="stats.commune")

    maisonTourisme = Choice(
        title=u"Maison du Tourisme",
        description=u"",
        required=False,
        vocabulary="stats.maisontourisme")

    hebType = Tuple(
        title=u"Type d'hébergement",
        description=u"",
        required=True,
        value_type=Choice(vocabulary="stats.hebtype"))

    capaciteMin = Int(
        title=u"Capacité minimum",
        description=u"",
        required=False)

    capaciteMax = Int(
        title=u"Capacité maximum",
        description=u"",
        required=False)

#    thematique = Tuple(title=u"Thématique",
#                        description=u"Selectionnez les animaux",
#                        required=True,
#                        value_type=Choice(title=u"animal",
#                                          vocabulary="cerise.user.Animal"))
