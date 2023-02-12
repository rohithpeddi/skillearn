import hl2ss

ACTIVITY = "activity"
PLACE_ID = "place_id"
PERSON_ID = "person_id"
RECORDING_NUMBER = "recording_number"
STEP_ID = "step_id"
DEVICE_IP = "device_ip"
IS_ERROR = "is_error"

PLACE = "place"
PERSON = "person"

SUBPROCESS_ID = "subprocess_id"

INFO = "info"
ACTIVITIES = "activities"
PLACES = "places"
PERSONS = "persons"
RECORDING_NUMBERS = "recording_numbers"

STANDARD_RECORDINGS = "standard_recordings"
ERROR_RECORDINGS = "error_recordings"
STEPS = "steps"

RECIPE_RECORDING_START_TIME = "recipe_start_time"
RECIPE_RECORDING_END_TIME = "recipe_end_time"

STEP_START_TIME = "step_start_time"
STEP_END_TIME = "step_end_time"

STATUS = "status"

SUCCESS = "success"
FAILED = "failed"
UPLOADED = "uploaded"
PENDING = "pending"
UPLOADING = "uploading"

RECORDING_STATUS = "recording_status"
UPLOAD_STATUS = "upload_status"

UPLOAD_QUEUE = "upload_queue"

# ASYNC OPERATION TYPES
UPLOAD_ASYNC_OPERATION = "async_upload_operation"
ACTIVITY_RECORD_ASYNC_OPERATION = "async_activity_record_operation"

# -----------------------------------------------------------------------------------------------

# Camera parameters
# See etc/hl2_capture_formats.txt for a list of supported formats.
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FRAMERATE = 30

# Video encoding profile
VIDEO_PROFILE = hl2ss.VideoProfile.H265_MAIN
VIDEO_DECODE = 'bgr24'

# Encoded video stream average bits per second
# Must be > 0
VIDEO_BITRATE = 5 * 1024 * 1024
DEPTH_BITRATE = 8 * 1024 * 1024

# Decoded format
DECODED_FORMAT = 'bgr24'

# Audio encoding profile
AUDIO_PROFILE = hl2ss.AudioProfile.AAC_24000

DEPTH_PORT = hl2ss.StreamPort.RM_DEPTH_AHAT
VIDEO_PORT = hl2ss.StreamPort.PHOTO_VIDEO
# Operating mode
# 0: video
# 1: video + rig pose
# 2: query calibration (single transfer)
DEPTH_MODE = hl2ss.StreamMode.MODE_1
VIDEO_MODE = hl2ss.StreamMode.MODE_1

# PNG filter
PNG_FILTER = hl2ss.PngFilterMode.Paeth

# Ports
PORTS = [
    hl2ss.StreamPort.RM_VLC_LEFTFRONT,
    hl2ss.StreamPort.RM_VLC_LEFTLEFT,
    hl2ss.StreamPort.RM_VLC_RIGHTFRONT,
    hl2ss.StreamPort.RM_VLC_RIGHTRIGHT,
    hl2ss.StreamPort.RM_DEPTH_AHAT,
    # hl2ss.StreamPort.RM_DEPTH_LONGTHROW,
    hl2ss.StreamPort.PHOTO_VIDEO,
    hl2ss.StreamPort.MICROPHONE,
    hl2ss.StreamPort.SPATIAL_INPUT,
    hl2ss.StreamPort.RM_IMU_ACCELEROMETER,
    hl2ss.StreamPort.RM_IMU_GYROSCOPE,
    hl2ss.StreamPort.RM_IMU_MAGNETOMETER,
]

# RM VLC parameters
VLC_MODE = hl2ss.StreamMode.MODE_1
VLC_PROFILE = hl2ss.VideoProfile.H264_BASE
VLC_BITRATE = 1 * 1024 * 1024

# RM Depth AHAT parameters
AHAT_MODE = hl2ss.StreamMode.MODE_1
AHAT_PROFILE = hl2ss.VideoProfile.H264_BASE
AHAT_BITRATE = 8 * 1024 * 1024

# RM Depth Long Throw parameters
LT_MODE = hl2ss.StreamMode.MODE_1
LT_FILTER = hl2ss.PngFilterMode.Paeth

# Maximum number of frames in buffer
BUFFER_ELEMENTS = 300

# PV parameters
PV_MODE = hl2ss.StreamMode.MODE_1
PV_WIDTH = FRAME_WIDTH
PV_HEIGHT = FRAME_HEIGHT
PV_FRAMERATE = 30
PV_PROFILE = hl2ss.VideoProfile.H265_MAIN
PV_BITRATE = 5 * 1024 * 1024
PV_FORMAT = 'bgr24'

# VLC Parameters
VLC_FPS = 15
VLC_WIDTH = 640
VLC_HEIGHT = 480

# Audio Parameters
MC_PROFILE = hl2ss.AudioProfile.AAC_24000

# IMU Parameters
IMU_MODE = hl2ss.StreamMode.MODE_1
