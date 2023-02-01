import time
from threading import Thread

from datacollection.error.backend.client_all_sensor_streams import hl2_record_sensor_streams
from datacollection.error.backend.client_all_sensor_streams import update_recording_status


class HololensService:
    def __init__(self):
        self._recording = False
        self.record_thread = None

    def start_recording(self, recording_path, hololens2_ip):
        if self._recording:
            print("Already recording")
            return
        self._recording = True
        record_thread = Thread(target=hl2_record_sensor_streams,
                               args=(recording_path, hololens2_ip, False))
        record_thread.start()

    def stop_recording(self):
        if not self._recording:
            print("Not recording")
            return
        self._recording = False
        update_recording_status(self._recording)
        if self.record_thread is not None:
            self.record_thread.join()


def test_hololens_service():
    recording_path = "../frames"
    hololens2_ip = '192.168.10.133'
    hololens_service = HololensService()
    record_time = 10
    hololens_service.start_recording(recording_path, hololens2_ip)
    time.sleep(record_time + 1)
    hololens_service.stop_recording()


if __name__ == '__main__':
    test_hololens_service()
