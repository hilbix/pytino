# Python tools not found elsewhere

def rev(d):
        """reverse a dict: {a:b} becomes {b:a}"""
        return dict((v,k) for (k,v) in d.iteritems())

