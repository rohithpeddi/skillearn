import os

from datacollection.user_app.backend.hololens import hl2ss

BASE_DIRECTORY = os.getcwd()


# # ---------------------------------------------------------------------------------------
# # ------------------------ USER APP PROPERTIES -----------------------------------

class User_Constants:
	ID = "id"
	USERNAME = "username"
	
	TOTAL_ENVIRONMENTS = 10
	ACTIVITIES_PER_PERSON_PER_ENV = 10
	
	ACTIVITY_PREFERENCES = "activity_preferences"
	RECORDING_SCHEDULES = "recording_schedules"
	ENVIRONMENT = "environment"
	NORMAL_RECORDINGS = "normal_activities"
	ERROR_RECORDINGS = "error_activities"
	RECORDED_LIST = "recorded_list"
	IS_DONE_RECORDING = "recording_status"


# # ---------------------------------------------------------------------------------------
# # ------------------------ RECORDING PROPERTIES -----------------------------------

class Recording_Constants:
	ID = "id"
	ACTIVITY_ID = "activity_id"
	IS_ERROR = "is_error"
	IS_PREPARED = "is_prepared"
	RECORDED_BY = "recorded_by"
	SELECTED_BY = "selected_by"
	ERRORS = "errors"
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
	ERROR_HINTS = "error_hints"
	REQUIRED_ITEMS = "required_items"
	
	DUMMY_USER_ID = -1
	
	START_TIME = "start_time"
	END_TIME = "end_time"
	
	DEFAULT_HOLOLENS_IP = "192.168.1.149"
	DEVICE_IP = "device_ip"
	
	PHOTOVIDEO = "pv"
	MICROPHONE = "mc"
	SPATIAL = "spatial"
	DEPTH_AHAT = "depth_ahat"
	DEPTH_LT = "depth_lt"
	IMU_ACCELEROMETER = "imu_accelerometer"
	IMU_GYROSCOPE = "imu_gyroscope"
	IMU_MAGNETOMETER = "imu_magnetometer"
	VLC_LEFTLEFT = "vlc_leftleft"
	VLC_LEFTFRONT = "vlc_leftfront"
	VLC_RIGHTFRONT = "vlc_rightleft"
	VLC_RIGHTRIGHT = "vlc_rightright"
	
	HOLOLENS_INFO = "hololens_info"
	GOPRO = "gopro"


# # ---------------------------------------------------------------------------------------
# # ------------------------ ASYNC SERVICE PROPERTIES -----------------------------------

class Async_Constants:
	ACTIVITY_RECORDING = "activity_recording"


# # ---------------------------------------------------------------------------------------
# # ------------------------ POST PROCESSING PROPERTIES -----------------------------------

class Post_Processing_Constants:
	PHOTOVIDEO = "pv"
	MICROPHONE = "mc"
	SPATIAL = "spatial"
	DEPTH_AHAT = "depth_ahat"
	DEPTH_LT = "depth_lt"
	IMU_ACCELEROMETER = "imu_accelerometer"
	IMU_GYROSCOPE = "imu_gyroscope"
	IMU_MAGNETOMETER = "imu_magnetometer"
	VLC_LEFTLEFT = "vlc_leftleft"
	VLC_LEFTFRONT = "vlc_leftfront"
	VLC_RIGHTFRONT = "vlc_rightleft"
	VLC_RIGHTRIGHT = "vlc_rightright"
	
	AB = "ab"
	DEPTH = "depth"
	VLC_LIST = [VLC_LEFTLEFT, VLC_LEFTFRONT, VLC_RIGHTFRONT, VLC_RIGHTRIGHT]


# # ---------------------------------------------------------------------------------------
# # ------------------------ HOLOLENS SERVICE PROPERTIES -----------------------------------

class Hololens_Constants:
	DEFAULT_HOLOLENS_IP = "192.168.1.149"
	DEVICE_IP = "device_ip"
	
	REDIS_HOST = "localhost"
	REDIS_PORT = 6379
	REDIS_MAX_CONNECTIONS = 20
	
	PHOTOVIDEO = "pv"
	MICROPHONE = "mc"
	SPATIAL = "spatial"
	DEPTH_AHAT = "depth_ahat"
	DEPTH_LT = "depth_lt"
	IMU_ACCELEROMETER = "imu_accelerometer"
	IMU_GYROSCOPE = "imu_gyroscope"
	IMU_MAGNETOMETER = "imu_magnetometer"
	VLC_LEFTLEFT = "vlc_leftleft"
	VLC_LEFTFRONT = "vlc_leftfront"
	VLC_RIGHTFRONT = "vlc_rightleft"
	VLC_RIGHTRIGHT = "vlc_rightright"
	
	AB = "ab"
	DEPTH = "depth"
	FRAMES = "frames"
	
	PV_FRAME_WIDTH = 640
	PV_FRAME_HEIGHT = 360
	PV_FRAMERATE = 30
	PV_VIDEO_PROFILE_RAW = hl2ss.VideoProfile.RAW
	PV_VIDEO_BITRATE_RAW = 250 * 1024 * 1024
	
	AHAT_MODE = hl2ss.StreamMode.MODE_1
	AHAT_PROFILE_RAW = hl2ss.VideoProfile.RAW
	AHAT_BITRATE_RAW = 250 * 1024 * 1024
	
	AUDIO_PROFILE_RAW = hl2ss.AudioProfile.RAW
	AUDIO_PROFILE_DECODED = hl2ss.AudioProfile.AAC_24000
	AUDIO_FRAME_RATE = hl2ss.Parameters_MICROPHONE.SAMPLE_RATE
	
	PV_POSE_FILE_NAME = "pv_pose"
	PV_DATA_DIRECTORY = "pv_data"
	
	DEPTH_AHAT_POSE_FILE_NAME = "depth_pose"
	DEPTH_AHAT_AB_DATA_DIRECTORY = "depth_ahat_ab_data"
	DEPTH_AHAT_DEPTH_DATA_DIRECTORY = "depth_ahat_depth_data"
	
	SPATIAL_DATA_WRITER = "spatial_data_writer"
	
	MICROPHONE_DATA_WRITER = "mc_data_writer"
	DEPTH_AHAT_POSE_WRITER = "depth_ahat_pose_writer"
	PV_POSE_WRITER = "pv_pose_writer"
	
	PV_STRIDE = hl2ss.compute_nv12_stride(PV_FRAME_WIDTH)


# # ---------------------------------------------------------------------------------------
# # ------------------------ GO PRO SERVICE PROPERTIES -----------------------------------

class GoPro_Constants:
	pass


# # ---------------------------------------------------------------------------------------
# # ------------------------ DATABASE PROPERTIES -----------------------------------

class Firebase_Constants:
	USERS = "users"
	ACTIVITIES = "activities"
	CURRENT_ENVIRONMENT = "current_environment"
	
	RECORDINGS = "recordings"
	
	RECORDED_BY = "recorded_by"
	ACTIVITY_ID = "activity_id"


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
	ERRORS = "errors"
	
	NUM_VALID_PROGRAMS = 25
	NUM_INVALID_PROGRAMS = 100
	
	NUM_MISSING_STEP_PROGRAMS = 10
	NUM_INVALID_ORDER_PROGRAMS = 90
	
	THRESHOLD_NUM_MISSING_STEPS = 20
	THRESHOLD_NUM_MISSING_STEPS_ORDER_ERRORS = 40
	
	NUM_TO_SHUFFLE = 20


# # ---------------------------------------------------------------------------------------
# # ------------------------ FLASK SERVER PROPERTIES -----------------------------------

class FlaskServer_constants:
	ID = "id"
	USERNAME = "username"
	
	ACTIVITY_RECORDINGS = "activity_recordings"
	RECORDED_BY = "recorded_by"
	
	SELECTED_ACTIVITIES = "selectedActivities"
	
	ERROR = "Error"
	SELECTED_BY = "selected_by"
	
	PREPARED = "Retrieved a PREPARED activity"
	SELECTED_PREVIOUSLY = "Retrieved a PREVIOUSLY SELECTED activity"
	NEWLY_SELECTED = "Retrieved a NEW activity"
	
	SELECTION_TYPE = "selection_type"
	RECORDING_CONTENT = "recording_content"
	
	NUMBER_OF_RECORDINGS = "number_of_recordings"
	NUMBER_OF_ERROR_RECORDINGS = "number_of_error_recordings"
	NUMBER_OF_CORRECT_RECORDINGS = "number_of_correct_recordings"
	
	RECORDING_STATS = "recording_stats"
	ERROR_STATS = "error_stats"
	USER_RECORDING_STATS = "user_recording_stats"
	
	DUMMY_USER_ID = -1
	
	ACTIVITY_RECORDING = "activity_recording"
	STATUS = "status"
	SUCCESS = "success"
	SUBPROCESS_ID = "subprocess_id"


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
	ERRORS = "errors"
	NAME = "name"
	ID = "id"
