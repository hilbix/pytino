# Python tools not found elsewhere

from __future__ import absolute_import

def rev(d):
        """reverse a dict: {a:b} becomes {b:a}"""
        return dict((v,k) for (k,v) in d.iteritems())

