import base64
import os.path
import time
import urllib.parse

import requests
from requests.auth import HTTPBasicAuth


# Reference for the Hololens2 Device portal API reference
# https://learn.microsoft.com/en-us/windows/mixed-reality/develop/advanced-concepts/device-portal-api-reference
class HL2_REST_Utils:
    # Create an HTTPBasicAuth object that will be passed to requests
    HOLOLENS2_USERNAME = f"admin"
    HOLOLENS2_PASSWORD = f"123456789"
    ASCII = "ascii"
    auth = HTTPBasicAuth(HOLOLENS2_USERNAME, HOLOLENS2_PASSWORD)

    @staticmethod
    def base64_encode_string(string_value):
        string_bytes = string_value.encode(HL2_REST_Utils.ASCII)
        base64_bytes = base64.b64encode(string_bytes)
        base64_string = base64_bytes.decode(HL2_REST_Utils.ASCII)
        return base64_string

    @staticmethod
    def base64_decode_string(base64_string):
        base64_bytes = base64_string.encode(HL2_REST_Utils.ASCII)
        string_bytes = base64.b64decode(base64_bytes)
        string_value = string_bytes.decode(HL2_REST_Utils.ASCII)
        return string_value

    @staticmethod
    def send_rest_post_request(post_url):
        ## Logger info of POST url
        response = requests.post(post_url, auth=HL2_REST_Utils.auth)
        if response.ok:
            print(response, f" - Request {post_url} sent successfully")
        pass

    @staticmethod
    def send_rest_get_request(get_url):
        ## Logger info of GET url
        response = requests.get(get_url, auth=HL2_REST_Utils.auth)
        if response.ok:
            print(response, f" - Request {get_url} sent successfully")
        return response

    @staticmethod
    def download_file_using_get(get_url, video_location):
        # NOTE the stream=True parameter below
        with requests.get(get_url, stream=True, auth=HL2_REST_Utils.auth) as r:
            r.raise_for_status()
            with open(video_location, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        pass


class HL2_REST_Controller:

    def __init__(self, ip_address, scheme="http"):
        self.ip_address = ip_address
        self.scheme = scheme
        self.http_hostname = self.scheme + "://" + self.ip_address

    def get_hostname(self):
        # Define the get URL to get the HostName
        rest_api_hostname = "/api/os/machinename"
        get_url = self.http_hostname + rest_api_hostname
        response = HL2_REST_Utils.send_rest_get_request(get_url)
        if not response.ok:
            return None
        hostname = response.json()['ComputerName']
        return hostname

    # MRC - Mixed Reality Capture
    def is_mrc_recording(self):
        rest_api_mrc_status = f"/api/holographic/mrc/status"
        mrc_status_url = self.http_hostname + rest_api_mrc_status
        response = HL2_REST_Utils.send_rest_get_request(mrc_status_url)
        mrc_recording_status = response.json()
        mrc_key = "IsRecording"
        if mrc_key in mrc_recording_status:
            return mrc_recording_status[mrc_key]
        return False

    def start_mrc(self):
        if self.is_mrc_recording():
            print("Recording in progress")
            return
        rest_api_start_mrc = f"/api/holographic/mrc/video/control/start"
        start_mrc_params = {
            'holo': 'false',
            'pv': 'true',
            'mic': 'true',
            'loopback': 'false',
            'RenderFromCamera': 'true',
            'vstab': 'true',
            'vstabbuffer': 30,
        }
        start_mrc_url = self.http_hostname + rest_api_start_mrc + "?" + urllib.parse.urlencode(start_mrc_params)
        HL2_REST_Utils.send_rest_post_request(start_mrc_url)

    def stop_mrc(self):
        if not self.is_mrc_recording():
            print("No recording in progress")
            return
        # Need to verify the Stop MRC
        rest_api_stop_mrc = f"/api/holographic/mrc/video/control/stop"
        stop_mrc_url = self.http_hostname + rest_api_stop_mrc
        HL2_REST_Utils.send_rest_post_request(stop_mrc_url)
        pass

    def get_mrc_files(self):
        rest_api_mrc_files = "/api/holographic/mrc/files"
        get_url = self.http_hostname + rest_api_mrc_files
        response = HL2_REST_Utils.send_rest_get_request(get_url)
        if not response.ok:
            return None
        return response.json()

    def download_most_recent_mrc_file(self, download_location):
        json_response = self.get_mrc_files()

        mrc_files_list = json_response['MrcRecordings']
        most_recent_mrc_file = mrc_files_list[-1]
        filename = most_recent_mrc_file['FileName']
        time_stamp = most_recent_mrc_file['CreationTime']

        video_location = os.path.join(download_location, str(time_stamp) + "_" + filename)

        #  Eg: "/api/holographic/mrc/file?filename=MjAyMzAyMjBfMTYwMzUzX0hvbG9MZW5zLm1wNA==&op=stream"
        filename_hex64 = HL2_REST_Utils.base64_encode_string(filename)
        stream = "stream"
        download_mrc_params = {
            "filename": filename_hex64,
            "op": stream,
        }
        rest_api_download_mrc_file = "/api/holographic/mrc/file"
        get_url = self.http_hostname + rest_api_download_mrc_file + "?" + urllib.parse.urlencode(download_mrc_params)
        print("Downloading   : ", filename)
        HL2_REST_Utils.download_file_using_get(get_url, video_location)
        print("Downloaded to : ", video_location)
        return video_location


def test_rest_api():
    ip_address = '10.176.194.67'
    hl2rc = HL2_REST_Controller(ip_address)
    hostname = hl2rc.get_hostname()
    print(hostname)
    hl2rc.start_mrc()
    print("Started Recording")
    time.sleep(10)
    hl2rc.stop_mrc()
    print("Stopped Recording")
    hl2rc.get_mrc_files()
    hl2rc.download_most_recent_mrc_file(download_location="../../data")


if __name__ == '__main__':
    test_rest_api()
