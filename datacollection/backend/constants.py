from datacollection.backend.hololens import hl2ss

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

# ---------------------------------------------------------------------------------------
# ------------------------ STREAM PRODUCER PROPERTIES -----------------------------------

# Typically transfer of RAW images requires more bitrate.
# PV CAMERA PARAMETERS
PV_FRAME_WIDTH = 1280
PV_FRAME_HEIGHT = 720
PV_FRAMERATE = 30
PV_VIDEO_PROFILE_RAW = hl2ss.VideoProfile.RAW
PV_VIDEO_DECODE = 'bgr24'
PV_VIDEO_BITRATE_RAW = 250 * 1024 * 1024

PV_VIDEO_BITRATE_DECODED = 5 * 1024 * 1024
PV_VIDEO_PROFILE_DECODED = hl2ss.VideoProfile.H265_MAIN

# DEPTH CAMERA PARAMETERS [AHAT]
AHAT_MODE = hl2ss.StreamMode.MODE_1
AHAT_PROFILE_RAW = hl2ss.VideoProfile.RAW
AHAT_BITRATE_RAW = 250 * 1024 * 1024

AHAT_BITRATE_DECODED = 1 * 1024 * 1024
AHAT_PROFILE_DECODED = hl2ss.VideoProfile.H264_BASE

# Audio encoding profile
AUDIO_PROFILE_RAW = hl2ss.AudioProfile.RAW
AUDIO_PROFILE_DECODED = hl2ss.AudioProfile.AAC_24000

# ---------------------------------------------------------------------------------------
# ------------------------ STREAM CONSUMER PROPERTIES -----------------------------------

# Used for writing the RAW data
PV_WRITER = "pv_writer"
DEPTH_AHAT_WRITER = "depth_ahat_writer"
MICROPHONE_WRITER = "microphone_writer"
SPATIAL_WRITER = "spatial_writer"


POSE_WRITER = "pose_writer"
DEPTH_AB_WRITER = "depth_ab_writer"

# ---------------------------------------------------------------------------------------
# ------------------------ REDIS STREAM PROPERTIES -----------------------------------

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_MAX_CONNECTIONS = 20

# Camera parameters
# See etc/hl2_capture_formats.txt for a list of supported formats.
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FRAMERATE = 30

# Video encoding profile
VIDEO_PROFILE_DECODED = hl2ss.VideoProfile.H265_MAIN
VIDEO_PROFILE_RAW = hl2ss.VideoProfile.RAW
VIDEO_DECODE = 'bgr24'

# Encoded video stream average bits per second
# Must be > 0
VIDEO_BITRATE = 5 * 1024 * 1024
DEPTH_BITRATE = 8 * 1024 * 1024

# Decoded format
DECODED_FORMAT = 'bgr24'

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

# RM Depth Long Throw parameters
LT_MODE = hl2ss.StreamMode.MODE_1
LT_FILTER = hl2ss.PngFilterMode.Paeth

# Maximum number of frames in buffer
BUFFER_ELEMENTS = 300

# VLC Parameters
VLC_FPS = 15
VLC_WIDTH = 640
VLC_HEIGHT = 480

# Audio Parameters
MC_PROFILE = hl2ss.AudioProfile.AAC_24000

# IMU Parameters
IMU_MODE = hl2ss.StreamMode.MODE_1

# ---------------------------------------------------------------------------------------------------------
# VERIFICATION PROPERTIES
# ---------------------------------------------------------------------------------------------------------

# Buffer length in seconds
BUFFER_LENGTH = 10

# Integration parameters
VOXEL_LENGTH = 1 / 100
SDF_TRUNC = 0.04
MAX_DEPTH = 3.0

PV_FOCUS = 1000
