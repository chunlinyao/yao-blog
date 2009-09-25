#!/usr/bin/env python
#coding:utf-8

import sys
sys.path.insert(0, 'lib/webpy.zip')
sys.path.insert(0, 'lib/markdown.zip')
sys.path.insert(0, 'lib/jinja2.zip')

import web, os
import data
from auth import requires_admin
import datetime,locale
from google.appengine.api import users

urls = (
  '/', 'Home',
  '/entry/(.*)', 'Entry',
  '/archive', 'Archive',
  '/about', 'About',
  '/feed', 'Feed',
  '/compose', 'Post'
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

class Home:
    def GET(self):
        entries = data.latest_entries()
        return render.home(entries=entries, **globals())

class Post:
    @requires_admin
    def GET(self):
        key = web.input(key=None)
        entry = Entry.get(key) if key else None
        return render.compose(entry=entry,**globals())

    @requires_admin
    def POST(self):
        key = web.input(key=None)
        if key:
            entry = Entry.get(key)
            entry.title = self.get_argument("title")
            entry.body = self.get_argument("markdown")
            entry.markdown = markdown.markdown(self.get_argument("markdown"))
        else:
            title = self.get_argument("title")
            slug = unicodedata.normalize("NFKD", title).encode(
                "ascii", "ignore")
            slug = re.sub(r"[^\w]+", " ", slug)
            slug = "-".join(slug.lower().strip().split())
            if not slug: slug = "entry"
            while True:
                existing = db.Query(Entry).filter("slug =", slug).get()
                if not existing or str(existing.key()) == key:
                    break
                slug += "-2"
            entry = Entry(
                author=self.current_user,
                title=title,
                slug=slug,
                body=self.get_argument("markdown"),
                markdown=markdown.markdown(self.get_argument("markdown")),
            )
        entry.put()
        return web.seeother("/entry/" + entry.slug)


class Entry:
    def GET(self, slug):
        entry = data.entry_by_slug(slug)
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
 

app = web.application(urls, globals())

def main():
    app.cgirun()

if __name__ == "__main__":
    main()
