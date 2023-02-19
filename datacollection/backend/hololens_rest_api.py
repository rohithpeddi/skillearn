import requests
from requests.auth import HTTPBasicAuth

# Reference for the Hololens2 Device portal API reference
# https://learn.microsoft.com/en-us/windows/mixed-reality/develop/advanced-concepts/device-portal-api-reference

HOLOLENS2_USERNAME = f"admin"
HOLOLENS2_PASSWORD = f"123456789"

# Create an HTTPBasicAuth object that will be passed to requests
auth = HTTPBasicAuth(HOLOLENS2_USERNAME, HOLOLENS2_PASSWORD)


def send_rest_post_request(post_url, params=None):
    response = requests.post(post_url, auth=auth)
    if response.ok:
        print(response)
    pass


def send_rest_get_request(post_url, params=None):
    response = requests.post(post_url, auth=auth)
    return response


def get_hostname(ip_address):
    # Define the get URL to get the HostName
    get_url = f"http://{ip_address}/api/os/machinename"
    response = send_rest_get_request(get_url)
    if not response.ok:
        return None
    hostname = response.json()['ComputerName']
    return hostname


# MRC - Mixed Reality Capture
def start_mrc(ip_address):
    #  Need to check the MRC status - /api/holographic/mrc/status
    start_mrc_url = f"http://{ip_address}/api/holographic/mrc/video/control/start" \
                    f"?holo=false&pv=true&mic=true&loopback=false&RenderFromCamera=true&vstab=true&vstabbuffer=30"
    send_rest_post_request(start_mrc_url)


def stop_mrc(ip_address):
    # Need to verify the stop mrc
    stop_mrc_url = f"http://{ip_address}/api/holographic/mrc/video/control/stop"
    send_rest_post_request(stop_mrc_url)
    pass


def main():
    ip_address = '192.168.10.130'
    get_hostname(ip_address)


if __name__ == '__main__':
    main()
