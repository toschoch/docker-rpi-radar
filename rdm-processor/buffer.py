import pyarrow as pa
from pyarrow import fs
from datetime import timedelta
import numpy as np
from storageapi.client import Client
import logging


class Buffer:

    def __init__(self, storage_client: Client):

        self.period_per_file = timedelta(minutes=1)

        self.times = []
        self.amps = []
        self.phases = []

        self.client = storage_client
        self.local = fs.LocalFileSystem()
        self.log = logging.getLogger('Buffer')

    def clear(self):
        self.log.debug("clear buffer...")
        self.times.clear()
        self.amps.clear()
        # self.phases.clear()

    def append(self, t, amp):#, phases):

        if len(self.times) > 0 and (t - self.times[0]) > self.period_per_file:
            self.store()

        self.times.append(t)
        self.amps.append(amp)
        # self.phases.append(phases)
        self.log.debug("added to buffer (current length {})".format(len(self.times)))

    def store(self):

        times = np.array(self.times)
        amps = np.array(self.amps)
        # phs = np.array(self.phases)

        self.log.info("create data object of {}...".format(amps.shape))
        rec = self.client.create(bucket='rdms', date=times[-1], meta={
            'samples': amps.shape[0],
            'start_time': times[0],
            'end_time': times[-1]
        })

        times = pa.Tensor.from_numpy(times.astype(np.datetime64).astype(np.int))
        amps = pa.Tensor.from_numpy(amps)
        # phs = pa.Tensor.from_numpy(phs)

        with self.local.open_output_stream(rec.location) as file:
            pa.ipc.write_tensor(times, file)
            pa.ipc.write_tensor(amps, file)
            # pa.ipc.write_tensor(phs, file)

        rec = self.client.finalize(rec)
        self.log.info("data object created ({})!.".format(rec.location))
        self.clear()




