from . import radio
import struct

class camera(object):
    def __init__(self):
        self.objects = {}

    def get_object_position(self, object_name):
        rval = None
        if object_name in self.objects:
            x = self.objects[object_name].x
            y = self.objects[object_name].y
            rval = (x, y)
        return rval

    def track_object(self, name, object):
        self.objects[name] = object

class camera_service(camera):
    def __init__(self, address):
        super(camera_service,self).__init__()
        self.transciever = radio.transciever(address)

    def process(self):
        while self.transciever.is_message_available():
            m = self.transciever.receive()
            name = m.data
            address = m.from_address
            m.address = 255
            position = self.get_object_position(name)
            if position != None:
                m.data = struct.pack("Bff", address, position[0], position[1])
                self.transciever.transmit(m)
