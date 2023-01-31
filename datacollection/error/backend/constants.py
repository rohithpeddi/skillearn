import hl2ss

RECIPE = "recipe"
KITCHEN_ID = "kitchen_id"
PERSON_ID = "person_id"
RECORDING_NUMBER = "recording_number"
STEP_ID = "step_id"

SUBPROCESS_ID = "subprocess_id"


INFO = "info"
RECORDINGS = "recordings"
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

RECORDING_STATUS = "recording_status"
UPLOAD_STATUS = "upload_status"

# -----------------------------------------------------------------------------------------------

# HoloLens address
HOLOLENS_IP = "192.168.1.149"

# Camera parameters
# See etc/hl2_capture_formats.txt for a list of supported formats.
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
FRAMERATE = 30

# Video encoding profile
VIDEO_PROFILE = hl2ss.VideoProfile.H265_MAIN

# Encoded video stream average bits per second
# Must be > 0
VIDEO_BITRATE = 5 * 1024 * 1024
DEPTH_BITRATE = 8 * 1024 * 1024

# Decoded format
DECODED_FORMAT = 'bgr24'

# Audio encoding profile
AUDIO_PROFILE = hl2ss.AudioProfile.AAC_24000

DEPTH_PORT = hl2ss.StreamPort.RM_DEPTH_AHAT
VIDEO_PORT = hl2ss.StreamPort.PERSONAL_VIDEO
# Operating mode
# 0: video
# 1: video + rig pose
# 2: query calibration (single transfer)
DEPTH_MODE = hl2ss.StreamMode.MODE_1
VIDEO_MODE = hl2ss.StreamMode.MODE_1

# PNG filter
PNG_FILTER = hl2ss.PngFilterMode.Paeth



