

class message:
    def __init__(self, data, address):
        self.data = data
        self.address = address

    def __repr__(self):
        return "<message to "+str(self.address)+", data length: "+str(len(self.data))+">"

class transciever:
    def __init__(self, address):
        self.address = address
        self.incoming_messages = [] #fifo
        self.radio = None

    def push_message(self, message):
        self.incoming_messages.append(message)

    def is_message_available(self):
        return (True if len(self.incoming_messages) != 0 else False)

    def transmit(self, message):
        self.radio.push_message(message)

    def receive(self):
        return self.incoming_messages.pop(0)

    def __repr__(self):
        return "<transciever addr: "+str(self.address)+">"

class radio:
    def __init__(self):
        self.transcievers = {}
        self.message_queue = [] #fifo

    def push_message(self, message):
        self.message_queue.append(message)

    def __broadcast(self, message):
        for t in self.transcievers.values():
            t.push_message(message)

    def process(self):
        for m in self.message_queue:
            if m.address == 255:
                __broadcast(m)
                continue
            if m.address in self.transcievers:
                self.transcievers[m.address].push_message(m)

        self.message_queue = []
            
    def add_transciever(self, transciever):
        transciever.radio = self
        self.transcievers[transciever.address] = transciever

if __name__ == "__main__":
    r = radio()

    station1 = transciever(1)
    station2 = transciever(2)

    print "adding", station1, "to network"
    r.add_transciever(station1)
    print "adding", station2, "to network"
    r.add_transciever(station2)

    print "sending message"
    m = message("TEST!", 2)
    print m
    station1.transmit(m)

    print "processing"
    r.process()

    print "checking for message"
    if station2.is_message_available():
        print "message is available"
        incoming = station2.receive()
        print "message data:", incoming.data
    else:
        print "ERROR: no message!"
