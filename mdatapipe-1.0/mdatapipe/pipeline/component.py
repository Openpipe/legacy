class Component(object):

    def __init__self(self, item):
        self.output_link = None

    def _on_input(self, item):
        if item is None:
            on_complete_func = getattr(self, 'on_complete', None)
            if on_complete_func:
                self.on_complete_func()
            self.put(item)
        else:
            self.on_input_func(item)

    def put(self, item):
        if self.output_link:
            self.output_link._on_input(item)
