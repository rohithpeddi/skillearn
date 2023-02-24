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
# ---------------------------- STREAM TYPES & PROPERTIES --------------------------------

PHOTOVIDEO = "pv"
MICROPHONE = "mc"
SPATIAL = "spatial"

DEPTH_AHAT = "depth_ahat"
DEPTH_AHAT_AB = "depth_ahat_ab"
DEPTH_AHAT_DEPTH = "depth_ahat_depth"

DEPTH_LT = "depth_lt"
DEPTH_LT_AB = "depth_lt_ab"
DEPTH_LT_DEPTH = "depth_lt_depth"

IMU_ACCELEROMETER = "imu_acc"
IMU_GYROSCOPE = "imu_gyro"
IMU_MAGNETOMETER = "imu_magnetometer"

VLC_LEFTLEFT = "vlc_ll"
VLC_LEFTFRONT = "vlc_lf"
VLC_RIGHTRIGHT = "vlc_rr"
VLC_RIGHTFRONT = "vlc_rf"

# Operating mode
# 0: video
# 1: video + rig pose
# 2: query calibration (single transfer)


PV_POSE_FILE_NAME = "pv_pose"
PV_DATA_DIRECTORY = "pv_data"

DEPTH_AHAT_POSE_FILE_NAME = "depth_pose"
DEPTH_AHAT_AB_DATA_DIRECTORY = "depth_ahat_ab_data"
DEPTH_AHAT_DEPTH_DATA_DIRECTORY = "depth_ahat_depth_data"

SPATIAL_DATA_WRITER = "spatial_data_writer"

MICROPHONE_DATA_WRITER = "mc_data_writer"

# ---------------------------------------------------------------------------------------
# ------------------------ STREAM PRODUCER PROPERTIES -----------------------------------

# Typically transfer of RAW images requires more bitrate.
# PV CAMERA PARAMETERS
PV_FRAME_WIDTH = 640
PV_FRAME_HEIGHT = 360
PV_FRAMERATE = 30
PV_STRIDE = hl2ss.compute_nv12_stride(PV_FRAME_WIDTH)

PV_VIDEO_PROFILE_RAW = hl2ss.VideoProfile.RAW
PV_VIDEO_BITRATE_RAW = 250 * 1024 * 1024

PV_VIDEO_DECODE = 'bgr24'
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

# RM VLC parameters
VLC_MODE = hl2ss.StreamMode.MODE_1
VLC_PROFILE = hl2ss.VideoProfile.H264_BASE
VLC_BITRATE = 1 * 1024 * 1024
VLC_FPS = 15
VLC_WIDTH = 640
VLC_HEIGHT = 480
BUFFER_ELEMENTS = 300

# RM Depth Long Throw parameters
LT_MODE = hl2ss.StreamMode.MODE_1
LT_FILTER = hl2ss.PngFilterMode.Paeth

# ---------------------------------------------------------------------------------------
# ------------------------ STREAM CONSUMER PROPERTIES -----------------------------------


# ---------------------------------------------------------------------------------------
# ------------------------ REDIS STREAM PROPERTIES -----------------------------------

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_MAX_CONNECTIONS = 20

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
