#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, 'lib/lib.zip')

import web, os
import data
from auth import requires_admin
import datetime
from google.appengine.api import users

urls = (
  '/', 'Home',
  '/index.html', 'Home',
  '/index.htm', 'Home',
  '/entry/(.*)', 'Entry',
  '/qr/(.*)', 'QREntry',
  '/archive', 'Archive',
  '/about', 'About',
  '/feed', 'Feed',
  '/atom', 'Feed',
  '/compose', 'Post',
  '/clear-cache', 'ClearCache',
  '/tag/(.*)', 'Tag',
  '/sitemap.xml', 'SiteMap',
)

settings = {
    "blog_title": u"Yao's blog",
    "debug": os.environ.get("SERVER_SOFTWARE", "").startswith("Development/"),
}
if settings['debug']:
    from web.contrib.template import render_jinja
else:
    from gae_render import render_jinja

render = render_jinja('templates')
from datetimeformat import datetimeformat
render._lookup.filters['datetimeformat'] = datetimeformat

import urllib
def urlencode(value):
    return urllib.quote(value, safe='')
render._lookup.filters['urlencode'] = urlencode

def tags_list():
    return data.Tag.taglist()
    
class Home:
    def GET(self):
        entries = data.latest_entries()
        return render.home(entries=entries, **globals())

class Post:
    @requires_admin
    def GET(self):
        i = web.input(key=None)
         
        import logging
        entry = data.entry_by_slug(i.key) if i.key else None
        return render.compose(entry=entry,**globals())

    @requires_admin
    def POST(self):
        i = web.input(key=None,title=None,markdown=None,tag_str=None)
        if i.key:
            if data.exists_entry(i.key):
                entry = data.update_entry(i.key, i)
            else:
                return web.seeother("/")
        else:
            entry = data.insert_entry(i)
        return web.seeother("/entry/" + entry.slugurl())


class Entry:
    def GET(self, slug):
        entry = data.entry_by_slug(slug)
        if entry is None:
            raise web.notfound()
        return render.entry(entry=entry,**globals())

class QREntry:
    def GET(self, id):
        entry = data.entry_by_id(id)
        if entry is None:
            raise web.notfound()
        return render.entry(entry=entry,**globals())


class Archive:
    def GET(self):
        entries = data.all_entries()
        return render.archive(entries=entries,**globals())

class Feed:
    def GET(self):
        web.header('Content-Type', 'application/atom+xml')
        entries = data.latest_entries()
        if(entries):
            last_updated = max(e.updated for e in entries)
        else:
            last_updated = datetime.datetime.utcnow()
        return render.feed(last_updated=last_updated, entries=entries,**globals())

class About:
    def GET(self):
        return render.about(**globals())

class ClearCache:
    def GET(self):
        from google.appengine.api import memcache
        memcache.flush_all()
        return "Memcache flushed." 

class Tag:
    def GET(self, tag):
        entries = data.Tag.entries_by_tag(tag)
        return render.archive(entries=entries, tagname=tag, **globals())

class SiteMap:
    def GET(self):
        web.header('Content-Type', 'text/xml')
        return render.sitemap(**globals())

app = web.application(urls, globals())

def main():
    app.cgirun()

if __name__ == "__main__":
    main()
