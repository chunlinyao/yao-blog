# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.ext import db
import urllib
from utils import slugify, versionate, markdown

class Entry(db.Model):
    """A single blog entry."""
    author = db.UserProperty()
    title = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    markdown = db.TextProperty(required=True)
    published = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    
    def slugurl(self):
        return urllib.quote(self.slug.encode('utf-8'), safe='') 	

def all_entries():
    return Entry.all()

def last_updated():
    import datetime
    last = db.Query(Entry).order('-published').get()
    return last.updated if last else datetime.datetime.now()
    

def latest_entries(limit=10):
    return db.Query(Entry).order('-published').fetch(limit=limit)


def entry_by_slug(slug):
    '''We're assuming all entries contain a unique slug.'''
    return db.Query(Entry).filter(u'slug =', slug).get()

def exists_entry(slug):
    q = db.Query(Entry).filter(u'slug =', slug).get()
    return q is not None

def update_entry(slug, i):
    entry = entry_by_slug(slug)
    if entry:
        entry.title = i.title
        entry.markdown = i.markdown
        entry.body = markdown(i.markdown)
        entry.put()
    return entry


def insert_entry(entry):
    slug = slugify(entry.title)
    while exists_entry(slug):
        slug = versionate(slug)        

    entry = Entry(
            author=users.get_current_user(),
            title=entry.title,
            body=markdown(entry.markdown),
            slug=slug,
            markdown=entry.markdown
            )
    entry.put()
    return entry
            

