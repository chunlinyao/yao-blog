#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re,unicodedata

def markdown(text):
    from markdown import markdown
    return markdown(text)

def timestamp(d=None):
    '''returns a string representing a given datetime up to the microsecond.
    Couldnt find a way to use strftime up to that precision'''
    import datetime
    date = d or datetime.datetime.now()
    microseconds = date.isoformat().split('.')[-1]
    return ''.join([datetime.datetime.strftime(date, '%Y%m%d%H%M%S'), microseconds])

def slugify(s):
    """Convert some string to a url-friendly name."""
    #islug = unicodedata.normalize("NFKD", s).encode(
    #    "ascii", "ignore")
    #slug = re.sub(u"[^\w]+", u" ", s)
    slug = u"-".join(s.lower().strip().split())
    if not slug: slug = "entry"
    return slug

def versionate(s):
    """
    Assumes s is a slug-type string.
    Returns another slug-type string with a number at the the end.
    Useful when you want unique slugs that may have been hashed to the same string.
    """
    words = s.split("-")
    if len(words) > 1:
        try:
            # Check if the last element is a number. If no exception, it is.
            # We'll substitute the number on the slug
            num = int(words[-1])
            words[-1] = str(num+1)
        except ValueError:
            #Not a number. We'll append the number 1 to create a new version.
            words.append('1')
        
    return '-'.join(words)


def save_uploaded_file(f, **kw):
    import datetime
    
    name = kw.pop('name', None)      
    folder = kw.pop('folder', './')

    uploaded_filename = str(f)
    extension = ('.' in uploaded_filename and uploaded_filename.split('.')[-1]) or ''
    
    filename = str(name) if name is not None else '.'.join([timestamp(), extension])
    
    destination = open(os.path.join(folder, filename), 'w')
    for chunk in f.chunks():
        destination.write(chunk)
        destination.close()
   
    return filename
    
    
