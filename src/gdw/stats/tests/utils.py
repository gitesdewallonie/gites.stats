# -*- coding: utf-8 -*-
"""
gdw.stats

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl
"""
from lxml import etree


def to_string(node):
    if isinstance(node, basestring):
        return node
    else:
        return etree.tostring(node, pretty_print=True)


def queryHTML(xpath, response):
    """Helper function to perform an xpath query on an html response"""
    doc = etree.HTML(response)
    result = [to_string(node) for node in doc.xpath(xpath)]
    return result
