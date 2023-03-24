import React from 'react';
import axios from "axios";
import './RecordingDisplayCard.css';

const RecordingDisplayCard = (props) => {
	
	const {userData, recording, setRecording, handleSuccessPopupOpen, handleErrorPopupOpen} = props;
	
	const selectRecording = async () => {
		try {
			let url = `http://localhost:5000/users/${userData.id}/select/recordings/${recording.id}`;
			const response = await axios.post(url);
			setRecording(response.data)
			handleSuccessPopupOpen("Picked the recording, proceed to prepare the recording");
		} catch (error) {
			console.error(error);
			handleErrorPopupOpen("Error picking the recording, change selection or refresh the page to try again");
		}
	};
	
	return (
		<div className="recordingDisplayGridContainer">
			{recording ? (
				<div>
					<div className="recordingDisplayGridItem">
						<table className="recordingDisplayTable">
							<thead>
							<tr>
								<th>Recording Steps</th>
							</tr>
							</thead>
							<tbody>
							{recording.steps.map((step, index) => (
								<tr key={index}>
									<td>{step.description}</td>
								</tr>
							))}
							</tbody>
						</table>
					</div>
					
					<div className="recordingDisplayGridItem">
						<button
							onClick={selectRecording}
							className="recordingSelectionButton"
						>
							Pick to record
						</button>
					</div>
				</div>
			) : (
				<div className="recordingDisplayGridItem">
					<h6 className="recordingDisplayNoRecording">
						No recording selected
					</h6>
				</div>
			)}
		</div>
	);
}

export default RecordingDisplayCard;
