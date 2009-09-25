#coding: utf-8

import logging
from jinja2 import FileSystemLoader
from google.appengine.api import memcache

class render_jinja:
    """Rendering interface to Jinja2 Templates
    
    Example:

        render= render_jinja('templates')
        render.hello(name='jinja2')
    """
    def __init__(self, *a, **kwargs):
        extensions = kwargs.pop('extensions', [])
        globals = kwargs.pop('globals', {})

        from jinja2 import Environment,FileSystemLoader
        self._lookup = Environment(loader=PythonLoader(*a, **kwargs), extensions=extensions)
        self._lookup.globals.update(globals)
        
    def __getattr__(self, name):
        # Assuming all templates end with .html
        path = name + '.html'
        t = self._lookup.get_template(path)
        return t.render
try:
    mydata
except NameError:
    logging.error("damn")
    mydata = {}
import base64
def get_data_by_name(name):
    if base64.b64encode(name) in mydata:
        return mydata[base64.b64encode(name)]
    return None
class PythonLoader(FileSystemLoader):
    """A Jinja2 loader that loads pre-compiled templates."""
    def load(self, environment, name, globals=None):
        """Loads a Python code template."""
        if globals is None:
            globals = {}
        #try for a variable cache
        code = get_data_by_name(name)
        if code is not None:
            logging.info("ultrafast memcache")
        else:
            logging.info("slow memcache")
            code = memcache.get(name)
            if code is None:
                logging.info("oops no memcache!!")
                source, filename, uptodate = self.get_source(environment, name)
                template = file(filename).read().decode('ascii').decode('utf-8')
                code = environment.compile(template, raw=True)
                memcache.set(name,code)
                logging.info(name)
            else:
                logging.info("yeh memcache")
            code = compile(code, name, 'exec')
            mydata[base64.b64encode(name)] = code
        return environment.template_class.from_code(environment, code,globals)

