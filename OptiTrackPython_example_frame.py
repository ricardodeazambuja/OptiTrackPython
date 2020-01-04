from threading import Lock
import time
from OptiTrackPython import NatNetClient


class TestNatNetClient(object):
    def __init__(self,
                 client_ip='192.168.2.101',
                 server_ip="192.168.2.100",
                 multicast_address="239.255.42.99",
                 rigidbody_names2track=["CogniFly"]):

        self.rigidbody_names2track = rigidbody_names2track

        self.lock_opti = Lock()

        self.optitrack_reading = {}

        # This will create a new NatNet client
        self.streamingClient = NatNetClient(client_ip,
                                            server_ip,
                                            multicast_address)

        # Configure the streaming client to call our rigid body handler on the emulator to send data out.
        self.streamingClient.newFrameListener = self.receiveFrame

        # Start up the streaming client now that the callbacks are set up.
        # This will run perpetually, and operate on a separate thread.
        self.streamingClient.run()

        while True:
            try:
                if self.optitrack_reading:
                    for ms in self.optitrack_reading[1]:
                        for m in ms:
                            print("Time Stamp: {}, Pos: {}".format(self.optitrack_reading[0], m))

                time.sleep(0.005)
            except KeyboardInterrupt:
                self.streamingClient.is_alive = False
                break

    def receiveFrame( frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
                                  labeledMarkerCount, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged,
                                  markerSets ):
        if markerSets:
            if self.lock_opti.acquire(False):
                try:
                    # rotation is a quaternion!
                    self.optitrack_reading = [timestamp, markerSets]
                finally:
                    self.lock_opti.release()


if __name__ == '__main__':
    TestNatNetClient()