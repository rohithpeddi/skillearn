import os
import paramiko
from ..constants import Post_Processing_Constants as const
from ..logger_config import logger


class NASTransferService:
	
	def __init__(self, recording, data_parent_directory: str):
		self.recording = recording
		self.data_parent_directory = data_parent_directory
		
		self.remote_parent_directory = const.NAS_PARENT_DIRECTORY
		
		self.ssh_client = paramiko.SSHClient()
		self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	def _transfer_directory(self, sftp_client, src_directory, dst_directory, is_file=False):
		if not is_file:
			sftp_client.mkdir(dst_directory)
		for item in os.listdir(src_directory):
			src_path = os.path.join(src_directory, item)
			dst_path = os.path.join(dst_directory, item)
			if os.path.isfile(src_path) or is_file:
				sftp_client.put(src_path, dst_path)
				logger.info(f'Transferred {item} to NAS')
			elif os.path.isdir(src_path):
				self._transfer_directory(sftp_client, src_path, dst_path)
	
	def transfer(self):
		self.ssh_client.connect(const.NAS_HOSTNAME, port=const.NAS_PORT, username=const.NAS_USERNAME,
		                        password=const.NAS_PASSWORD)
		sftp_client = self.ssh_client.open_sftp()
		
		data_directory = os.path.join(self.data_parent_directory, self.recording.id)
		remote_data_directory = os.path.join(self.remote_parent_directory, self.recording.id)
		remote_raw_data_directory = os.path.join(remote_data_directory, const.RAW)
		remote_sync_directory = os.path.join(remote_data_directory, const.SYNC)
		remote_gopro_directory = os.path.join(remote_data_directory, const.GOPRO)
		
		# 1. Transfer RAW data to NAS
		for node in os.listdir(data_directory):
			node_path = os.path.join(data_directory, node)
			if os.path.isdir(node_path) and node not in (const.SYNC, const.GOPRO):
				remote_node_path = os.path.join(remote_raw_data_directory, node)
				self._transfer_directory(sftp_client, node_path, remote_node_path)
		
		# 2. Transfer Synchronized data to NAS
		sync_directory = os.path.join(data_directory, const.SYNC)
		self._transfer_directory(sftp_client, sync_directory, remote_sync_directory)
		
		# 3. Transfer GOPRO data to NAS
		gopro_directory = os.path.join(data_directory, const.GOPRO)
		self._transfer_directory(sftp_client, gopro_directory, remote_gopro_directory, is_file=True)
