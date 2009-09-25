import web
from google.appengine.api import users

def requires_admin(method):
    """Decorate with this method to restrict to site admins."""
    def wrapper(self, *args, **kwargs):
        user = users.get_current_user()
        if not user:
            if web.ctx.method == "GET":
                raise web.seeother(users.create_login_url(web.ctx.path))
            raise web.forbidden()
        elif not (users.is_current_user_admin()):
            raise web.forbidden()
        else:
            return method(self, *args, **kwargs)
    return wrapper
