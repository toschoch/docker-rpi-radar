import zmq
import struct
import datetime
import pytz
import pyarrow as pa


class ZmqArrow:
    """Opens a zmq socket and sends images
    Opens a zmq (REQ or PUB) socket on the image sending computer, often a
    Raspberry Pi, that will be sending OpenCV images and
    related text messages to the hub computer. Provides methods to
    send images or send jpg compressed images.
    Two kinds of ZMQ message patterns are possible in imagezmq:
    REQ/REP: an image is sent and the sender waits for a reply ("blocking").
    PUB/SUB: an images is sent and no reply is sent or expected ("non-blocking").
    There are advantabes and disadvantages for each message pattern.
    See the documentation for a full description of REQ/REP and PUB/SUB.
    The default is REQ/REP for the ImageSender class and the ImageHub class.
    Arguments:
      connect_to: the tcp address:port of the hub computer.
      REQ_REP: (optional) if True (the default), a REQ socket will be created
                          if False, a PUB socket will be created
    """

    def __init__(self, address='tcp://127.0.0.1:5555', socket_type=zmq.SUB):
        """Initializes zmq socket for sending images to the hub.
        Expects an appropriate ZMQ socket at the connect_to tcp:port address:
        If REQ_REP is True (the default), then a REQ socket is created. It
        must connect to a matching REP socket on the ImageHub().
        If REQ_REP = False, then a PUB socket is created. It must connect to
        a matching SUB socket on the ImageHub().
        """

        self.zmq_context = SerializingContext()
        self.zmq_socket = self.zmq_context.socket(socket_type)
        if socket_type == zmq.SUB:
            self.zmq_socket.connect(address)
            self.zmq_socket.setsockopt(zmq.SUBSCRIBE, b'')
        elif socket_type == zmq.PUB:
            self.zmq_socket.bind(address)
        else:
            raise NotImplementedError("Only PUB/SUB implemented so far")

    def close(self):
        """Closes the ZMQ socket and the ZMQ context.
        """

        self.zmq_socket.close()
        self.zmq_context.term()

    def __enter__(self):
        """Enables use of ImageSender in with statement.
        Returns:
          self.
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Enables use of ImageSender in with statement.
        """

        self.close()


class SerializingSocket(zmq.Socket):
    """Numpy array serialization methods.
    Modelled on PyZMQ serialization examples.
    Used for sending / receiving OpenCV images, which are Numpy arrays.
    Also used for sending / receiving jpg compressed OpenCV images.
    """

    time_byte_format = '!d'

    def send_time_and_tensor(self, t: datetime.datetime, tensor: pa.Tensor, flags=0, copy=False, track=False):
        """Sends a numpy array with metadata and text message.
        Sends a numpy array with the metadata necessary for reconstructing
        the array (dtype,shape). Also sends a text msg, often the array or
        image name.
        Arguments:
          t:
          tensor:
          flags: (optional) zmq flags.
          copy: (optional) zmq copy.
          track: (optional) zmq track flag.
        """

        sink = pa.BufferOutputStream()
        pa.ipc.write_tensor(tensor, sink)

        self.send(struct.pack(self.time_byte_format, t.timestamp()), copy=False, flags=flags | zmq.SNDMORE)
        return self.send(sink.getvalue(), copy=False, flags=flags, track=track)

    def recv_time_and_tensor(self, copy=False, flags=0, track=False):
        """Receives a jpg buffer and a text msg.
        Receives a apache arrow tensor and a time stamp
        Arguments:
          copy:
          flags: (optional) zmq flags.
          track: (optional) zmq track flag.
        Returns:
          t: (datetime)
          tensor: (pyarrow.tensor), tensor.
        """
        frames = self.recv_multipart(copy=copy)

        t = struct.unpack(self.time_byte_format, frames[0].buffer)[0]
        t = datetime.datetime.fromtimestamp(t, pytz.utc)

        tensor = pa.ipc.read_tensor(pa.BufferReader(frames[1].buffer))

        return t, tensor


class SerializingContext(zmq.Context):
    _socket_class = SerializingSocket
