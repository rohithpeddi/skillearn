from ..models.recording_data_container import RecordingDataContainer
from ..models.recording import Recording
from ..utils.constants import Recording_Constants as const


class RecordingSummary:
	
	def __init__(
			self,
			recording_id: str,
			recording: Recording,
			is_hololens_enabled: bool,
			is_spatial_enabled: bool,
	):
		self.recording = recording
		self.recording_id = recording_id
		self.is_hololens_enabled = is_hololens_enabled
		self.is_spatial_enabled = is_spatial_enabled
		
		self.metadata = RecordingDataContainer(
			is_holo_lens_enabled=self.is_hololens_enabled,
			is_spatial_enabled=self.is_spatial_enabled
		)
		self.download_links = RecordingDataContainer(
			is_holo_lens_enabled=self.is_hololens_enabled,
			is_spatial_enabled=self.is_spatial_enabled
		)
		self.file_sizes = RecordingDataContainer(
			is_holo_lens_enabled=self.is_hololens_enabled,
			is_spatial_enabled=self.is_spatial_enabled
		)
		
	def to_dict(self):
		return {
			const.RECORDING_ID: self.recording_id,
			const.RECORDING: self.recording.to_dict(),
			const.IS_HOLO_LENS_ENABLED: self.is_hololens_enabled,
			const.IS_SPATIAL_ENABLED: self.is_spatial_enabled,
			const.METADATA: self.metadata.to_dict(),
			const.DOWNLOAD_LINKS: self.download_links.to_dict(),
			const.FILE_SIZES: self.file_sizes.to_dict()
		}
	
	@classmethod
	def from_dict(cls, recording_summary_dict) -> "RecordingSummary":
		recording_id = recording_summary_dict[const.RECORDING_ID]
		recording = Recording.from_dict(recording_summary_dict[const.RECORDING])
		is_holo_lens_enabled = recording_summary_dict[const.IS_HOLO_LENS_ENABLED]
		is_spatial_enabled = recording_summary_dict[const.IS_SPATIAL_ENABLED]
		
		recording_summary = cls(
			recording_id=recording_id,
			recording=recording,
			is_hololens_enabled=is_holo_lens_enabled,
			is_spatial_enabled=is_spatial_enabled
		)
		
		recording_summary.metadata = RecordingDataContainer.from_dict(
			recording_summary_dict[const.METADATA]
		)
		recording_summary.download_links = RecordingDataContainer.from_dict(
			recording_summary_dict[const.DOWNLOAD_LINKS]
		)
		recording_summary.file_sizes = RecordingDataContainer.from_dict(
			recording_summary_dict[const.FILE_SIZES]
		)
		
		return recording_summary
		
