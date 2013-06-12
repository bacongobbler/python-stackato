

class StackatoApp(object):

    def __init__(self, name, env=None, instances=None, meta=None, created=None, debug=None, version=None,
                 runningInstances=None, services=None, state=None, uris=None, staging=None, resources=None,
                 interface=None):
        self._name = name
        self.environment_variables = env
        self.instances = instances
        self.meta = meta
        self.created = created
        self.debug = debug
        self.version = version
        self.running_instances = runningInstances
        self.services = services
        self.state = state
        self.uris = uris
        self.interface = interface

    def __str__(self):
        return self._name

    def __repr__(self):
        return self.__str__()

    @property
    def name(self):
        return self._name

    @staticmethod
    def from_dict(dict, interface=None):
        return StackatoApp(interface=interface, **dict)

    def delete(self):
        if not self.interface:
            raise Exception("Tried to delete app %s without providing an interface for doing so" % self.name)
        self.interface.delete_app(self.name)