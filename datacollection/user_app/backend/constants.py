# # ---------------------------------------------------------------------------------------
# # ------------------------ USER APP PROPERTIES -----------------------------------
import os


class User_Constants:
	ID = "id"
	USERNAME = "username"
	
	TOTAL_ENVIRONMENTS = 10
	ACTIVITIES_PER_PERSON_PER_ENV = 10
	
	ACTIVITY_PREFERENCES = "activity_preferences"
	RECORDING_SCHEDULES = "recording_schedules"
	ENVIRONMENT = "environment"
	NORMAL_RECORDINGS = "normal_activities"
	MISTAKE_RECORDINGS = "mistake_activities"
	RECORDED_LIST = "recorded_list"
	IS_DONE_RECORDING = "recording_status"


BASE_DIRECTORY = os.getcwd()

ID = "id"
USERNAME = "username"
ACTIVITY_ID = "activity_id"
IS_MISTAKE = "is_mistake"
RECORDED_BY = "recorded_by"


# # ---------------------------------------------------------------------------------------
# # ------------------------ RECORDING PROPERTIES -----------------------------------

class Recording_Constants:
	ID = "id"
	ACTIVITY_ID = "activity_id"
	IS_MISTAKE = "is_mistake"
	RECORDED_BY = "recorded_by"
	SELECTED_BY = "selected_by"
	MISTAKES = "mistakes"
	ENVIRONMENT = "environment"
	STEPS = "steps"
	
	RECORDING_INFO = "recording_info"
	RGB = "rgb"
	AUDIO = "audio"
	INFO_3D = "info_3d"
	
	IS_RGB_AUDIO_SYNCHRONIZED = 'is_rgb_audio_synchronized'
	IS_RGB_INFO_3D_SYNCHRONIZED = 'is_rgb_info_3d_synchronized'
	ARE_ALL_SYNCHRONIZED = 'are_all_synchronized'
	
	DESCRIPTION = "description"
	MODIFIED_DESCRIPTION = "modified_description"
	
	TAG = "tag"
	
	ACTIVITIES = "activities"
	NAME = "name"
	CATEGORY = "category"
	ACTIVITY_TYPE = "activity_type"
	MISTAKE_HINTS = "mistake_hints"
	REQUIRED_ITEMS = "required_items"


# # ---------------------------------------------------------------------------------------
# # ------------------------ DATABASE PROPERTIES -----------------------------------

class Firebase_Constants:
	USERS = "users"
	ACTIVITIES = "activities"
	CURRENT_ENVIRONMENT = "current_environment"
	
	RECORDINGS = "recordings"


ENVIRONMENT = "environment"
NORMAL_RECORDINGS = "normal_activities"
MISTAKE_RECORDINGS = "mistake_activities"
RECORDED_LIST = "recorded_list"
IS_DONE_RECORDING = "recording_status"
ACTIVITY_PREFERENCES = "activity_preferences"
RECORDING_SCHEDULES = "recording_schedules"

TAG = "tag"
DESCRIPTION = "description"
MODIFIED_DESCRIPTION = "modified_description"
MISTAKES = "mistakes"

NAME = "name"
CATEGORY = "category"
ACTIVITY_TYPE = "activity_type"
MISTAKE_HINTS = "mistake_hints"
REQUIRED_ITEMS = "required_items"
STEPS = "steps"


# # ---------------------------------------------------------------------------------------
# # ------------------------ LIGHT TAG PROPERTIES -----------------------------------

class LightTag_Constants:
	SCHEMA = "schema"
	TAGS = "tags"
	EXAMPLES = "examples"
	ANNOTATIONS = "annotations"
	NAME = "name"
	ID = "id"
	TAGGED_TOKEN_ID = "tagged_token_id"
	TAG_ID = "tag_id"
	VALUE = "value"
	RELATIONS = "relations"
	CHILDREN = "children"
	STEP = "step"
	ACTION = "action"
	LABEL = "label"
	
	RECORDING_ID = "recording_id"
	DESCRIPTION = "description"
	STEPS = "steps"
	MISTAKES = "mistakes"
	
	NUM_VALID_PROGRAMS = 25
	NUM_INVALID_PROGRAMS = 100
	
	NUM_MISSING_STEP_PROGRAMS = 10
	NUM_INVALID_ORDER_PROGRAMS = 90
	
	THRESHOLD_NUM_MISSING_STEPS = 20
	THRESHOLD_NUM_MISSING_STEPS_ORDER_MISTAKES = 40
	
	NUM_TO_SHUFFLE = 20


# # ---------------------------------------------------------------------------------------
# # ------------------------ FLASK SERVER PROPERTIES -----------------------------------

class FlaskServer_constants:
	ID = "id"
	USERNAME = "username"
	
	ACTIVITY_RECORDINGS = "activity_recordings"
	RECORDED_BY = "recorded_by"
	
	SELECTED_ACTIVITIES = "selectedActivities"
	


# # ---------------------------------------------------------------------------------------
# # ------------------------ DB INGESTION PROPERTIES -----------------------------------

class DatabaseIngestion_Constants:
	INFO_FILES = "info_files"
	RECORDINGS = "recordings"
	GRAPHS = "graphs"
	
	USERS_YAML_FILE_NAME = "users.yaml"
	ACTIVITIES_YAML_FILE_NAME = "activities.yaml"
	
	RECORDING_ID = "recording_id"
	STEPS = "steps"
	MISTAKES = "mistakes"
	NAME = "name"
	ID = "id"


# # ---------------------------------------------------------------------------------------
# # ------------------------ STREAM PRODUCER PROPERTIES -----------------------------------

ACTIVITY = "activity"
PLACE_ID = "place_id"
PERSON_ID = "person_id"
RECORDING_NUMBER = "recording_number"
STEP_ID = "step_id"
DEVICE_IP = "device_ip"

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

IS_DONE_RECORDING = "is_done_recording"
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

AB = "ab"
DEPTH = "depth"

PV_POSE_FILE_NAME = "pv_pose"
PV_DATA_DIRECTORY = "pv_data"

DEPTH_AHAT_POSE_FILE_NAME = "depth_pose"
DEPTH_AHAT_AB_DATA_DIRECTORY = "depth_ahat_ab_data"
DEPTH_AHAT_DEPTH_DATA_DIRECTORY = "depth_ahat_depth_data"

SPATIAL_DATA_WRITER = "spatial_data_writer"

MICROPHONE_DATA_WRITER = "mc_data_writer"
DEPTH_AHAT_POSE_WRITER = "depth_ahat_pose_writer"
PV_POSE_WRITER = "pv_pose_writer"

# # ---------------------------------------------------------------------------------------
# # ------------------------ STREAM PRODUCER PROPERTIES -----------------------------------
#
# # Typically transfer of RAW images requires more bitrate.
# # PV CAMERA PARAMETERS
# PV_FRAME_WIDTH = 640
# PV_FRAME_HEIGHT = 360
# PV_FRAMERATE = 30
# PV_STRIDE = hl2ss.compute_nv12_stride(PV_FRAME_WIDTH)
#
# PV_VIDEO_PROFILE_RAW = hl2ss.VideoProfile.RAW
# PV_VIDEO_BITRATE_RAW = 250 * 1024 * 1024
#
# PV_VIDEO_DECODE = 'bgr24'
# PV_VIDEO_BITRATE_DECODED = 5 * 1024 * 1024
# PV_VIDEO_PROFILE_DECODED = hl2ss.VideoProfile.H265_MAIN
#
# # DEPTH CAMERA PARAMETERS [AHAT]
# AHAT_MODE = hl2ss.StreamMode.MODE_1
# AHAT_PROFILE_RAW = hl2ss.VideoProfile.RAW
# AHAT_BITRATE_RAW = 250 * 1024 * 1024
#
# AHAT_BITRATE_DECODED = 1 * 1024 * 1024
# AHAT_PROFILE_DECODED = hl2ss.VideoProfile.H264_BASE
#
# # Audio encoding profile
# AUDIO_PROFILE_RAW = hl2ss.AudioProfile.RAW
# AUDIO_PROFILE_DECODED = hl2ss.AudioProfile.AAC_24000
# AUDIO_FRAME_RATE = hl2ss.Parameters_MICROPHONE.SAMPLE_RATE
#
# # RM VLC parameters
# VLC_MODE = hl2ss.StreamMode.MODE_1
# VLC_PROFILE = hl2ss.VideoProfile.H264_BASE
# VLC_BITRATE = 1 * 1024 * 1024
# VLC_FPS = 15
# VLC_WIDTH = 640
# VLC_HEIGHT = 480
# BUFFER_ELEMENTS = 300
#
# # RM Depth Long Throw parameters
# LT_MODE = hl2ss.StreamMode.MODE_1
# LT_FILTER = hl2ss.PngFilterMode.Paeth
#
# # ---------------------------------------------------------------------------------------
# # ------------------------ STREAM CONSUMER PROPERTIES -----------------------------------
#
#
# # ---------------------------------------------------------------------------------------
# # ------------------------ REDIS STREAM PROPERTIES -----------------------------------
#
# REDIS_HOST = "localhost"
# REDIS_PORT = 6379
# REDIS_MAX_CONNECTIONS = 20
#
# # ---------------------------------------------------------------------------------------------------------
# # POST PROCESSING PROPERTIES
# # ---------------------------------------------------------------------------------------------------------
#
# # ---------------------------------------------------------------------------------------
# # ------------------------ AUDIO PROPERTIES -----------------------------------
#
#
#
# # Buffer length in seconds
# BUFFER_LENGTH = 10
#
# # Integration parameters
# VOXEL_LENGTH = 1 / 100
# SDF_TRUNC = 0.04
# MAX_DEPTH = 3.0
#
# PV_FOCUS = 1000
