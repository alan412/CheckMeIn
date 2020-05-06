
class WebBase(object):
    def __init__(self, lookup, engine):
        self.lookup = lookup
        self.engine = engine

    def template(self, name, **kwargs):
        return self.lookup.get_template(name).render(**kwargs)
    def dbConnect(self):
        return self.engine.dbConnect()