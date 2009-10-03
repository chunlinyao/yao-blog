# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.ext import db
import urllib,string
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
    tag_str = db.StringProperty(required=False) 
    tags = db.ListProperty(db.Category)

    @property
    def tagurls(self):
        def encodeurl(x):
            x.url = urllib.quote(x.encode('utf-8'), safe='') 
            return x	
        return map(encodeurl, self.tags)
        
    def slugurl(self):
        return urllib.quote(self.slug.encode('utf-8'), safe='') 	
    
    def validate_tag_str(self):
        """  """
        tag_str = self.tag_str
        if not type(tag_str) in [unicode, str]:
            raise ValueError('Passed tag_str must be of type string or unicode. not %s'%type(tag_str))

        tag_list = tag_str.split(',')
        tag_list = map(string.strip, tag_list)
        #tag_list = map(string.lowercase, tag_list)  
        tag_list = {}.fromkeys(tag_list).keys()
        # Example: ['ai', 'computer science', 'lisp', '']
        # This removes that empty string
        try: tag_list.remove('')
        except: pass
        tag_list.sort()
        # Return list as an array of db.Category items
        # Example: [db.Category('ai'), db.Category('computer science'), db.Category('lisp')]
        return map(db.Category, tag_list)    
                                 
    def update_tags(self):
        """Update Tag cloud info"""
        oldtags = self.tags or []
        newtags = self.validate_tag_str() or []
        addtags = [x for x in newtags if (x not in oldtags) ]
        removetags = [x for x in oldtags if (x not in newtags) ]
        for tag_ in addtags:
            #tag_ = tag.encode('utf8')
            tags = Tag.all().filter('tag',tag_).fetch(10)
            if tags == []:
                tagnew = Tag(tag=tag_,entrycount=1)
                tagnew.put()
            else:
                tags[0].entrycount+=1
                tags[0].put()    
        for tag_ in removetags:
            #tag_ = tag.encode('utf8')
            tags = Tag.all().filter('tag',tag_).fetch(10)
            if tags != []:
                tags[0].entrycount-=1
                if tags[0].entrycount == 0 :
                    tags[0].delete()
                else:
                    tags[0].put()
        self.tags = newtags;
        
class Tag(db.Model):
    tag = db.StringProperty(multiline=False)
    entrycount = db.IntegerProperty(default=0)
    valid = db.BooleanProperty(default = True)
    def tagurl(self):
        return urllib.quote(self.tag.encode('utf-8'), safe='')

    @staticmethod
    def entries_by_tag(tag):
        return Entry.all().filter('tags =', db.Category(tag)).order('-published')
    
    @staticmethod
    def taglist():
        return Tag.all().filter('valid =', True).order('-entrycount')
        
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
        entry.tag_str = i.tag_str
        entry.update_tags()
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
            markdown=entry.markdown,
            tag_str = entry.tag_str
            )
    entry.update_tags()
    entry.put()
    
    return entry
            

