
import cherrypy


class Cookie(object):
    def __init__(self, name):
        self.name = name

    def get(self, default=''):
        result = default
        try:
            result = cherrypy.session.get(self.name)
            if not result:
                self.set(default)
                result = default
        except:
            self.set(default)
        return result

    def set(self, value):
        cherrypy.session[self.name] = value
        return value

    def delete(self):
        cherrypy.session.pop(self.name, None)


class WebBase(object):
    def __init__(self, lookup, engine):
        self.lookup = lookup
        self.engine = engine

    def template(self, name, **kwargs):
        return self.lookup.get_template(name).render(**kwargs)

    def dbConnect(self):
        return self.engine.dbConnect()
