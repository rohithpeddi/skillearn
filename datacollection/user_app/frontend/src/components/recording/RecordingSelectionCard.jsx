import { useState } from 'react';
import axios from "axios";
import "./RecordingSelectionCard.css";

const RecordingSelectionCard = (props) => {
	
	const {userData, label, activityIds, activityIdToActivityName, setRecording} = props;
	
	const [selectedActivityId, setSelectedActivityId] = useState('');
	
	const handleSelectChange = (event) => {
		setSelectedActivityId(event.target.value);
	};
	
	const fetchData = async () => {
		try {
			let url = `http://localhost:5000/users/${userData.id}/activities/${selectedActivityId}/recordings/${label}`;
			const response = await axios.get(url);
			setRecording(response.data);
		} catch (error) {
			console.error(error);
		}
	};
	
	return (
		<div className="rscRoot">
			<div className="rscBox">
				<label htmlFor="select" className="rscLabel">Select {label} Activity:</label>
				<select id="select" value={selectedActivityId} onChange={handleSelectChange} className="rscSelect">
					<option value="">--Please select an activity--</option>
					{activityIds.map((activityId) => (
						<option key={activityId} value={activityId}>
							{activityIdToActivityName[activityId]}
						</option>
					))}
				</select>
			</div>
			<div className="rscBox">
				<button onClick={fetchData} className="rscButton">
					Fetch {label} Recording
				</button>
			</div>
		</div>
	);
};

export default RecordingSelectionCard;
