from threading import Lock
import time
from OptiTrackPython import NatNetClient


class TestNatNetClient(object):
    def __init__(self,
                 client_ip='192.168.2.101',
                 server_ip="192.168.2.100",
                 multicast_address="239.255.42.99",
                 rigidbody_names2track=["Solo1"]):

        self.rigidbody_names2track = rigidbody_names2track

        self.lock_opti = Lock()

        self.optitrack_reading = {}

        # This will create a new NatNet client
        self.streamingClient = NatNetClient(client_ip,
                                            server_ip,
                                            multicast_address)

        # Configure the streaming client to call our rigid body handler on the emulator to send data out.
        self.streamingClient.rigidBodyListener = self.receiveRigidBodyFrame

        # Start up the streaming client now that the callbacks are set up.
        # This will run perpetually, and operate on a separate thread.
        self.streamingClient.run()

        while True:
            try:
                for key in self.optitrack_reading:
                    print("{} Received frame for rigid body {}:\n position: {}\n rotation: {}".format(self.optitrack_reading[key][0],
                                                                                                      key,
                                                                                                      self.optitrack_reading[key][1],
                                                                                                      self.optitrack_reading[key][2]))
                time.sleep(0.005)
            except KeyboardInterrupt:
                self.streamingClient.is_alive = False
                break

    def receiveRigidBodyFrame(self, timestamp, id, position, rotation, rigidBodyDescriptor):
        if rigidBodyDescriptor:
            for rbname in self.rigidbody_names2track:
                if rbname in rigidBodyDescriptor:
                    if id == rigidBodyDescriptor[rbname][0]:
                        # skips this message if still locked
                        if self.lock_opti.acquire(False):
                            try:
                                # rotation is a quaternion!
                                self.optitrack_reading[rbname] = [timestamp,
                                                                  position,
                                                                  rotation]
                            finally:
                                self.lock_opti.release()


if __name__ == '__main__':
    TestNatNetClient()