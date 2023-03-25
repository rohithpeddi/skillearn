import React from 'react';
import './RecordingRecording.css';
import RecordingRequiredItems from "./RecordingRequiredItems";

const RecordingRecording = (props) => {
	const { userData, environment, activities, recording, setRecording } = props;
	
	const getActivityName = (activityId) => {
		const activity = activities.find((activity) => activity.id === activityId);
		return activity.name;
	};
	
	const getRequiredItems = (activityId) => {
		const activity = activities.find((activity) => activity.id === activityId);
		return activity.required_items;
	};
	
	if (!recording) {
		return (
			<div>
				<h1>Please go back and select an activity to begin preparing for the recording</h1>
			</div>
		);
	}
	
	return (
		<div className="recRecordContainer">
			
			<div className="recRecordHeader">
				<h2>Required Items</h2>
				<RecordingRequiredItems requiredItems={getRequiredItems(recording.activity_id)}/>
			</div>
			
			<table className="recRecordTable">
				<thead>
				<tr className="recRecordTableHeader">
					<th colSpan="4">Preparing activity {getActivityName(recording.activity_id)}</th>
				</tr>
				</thead>
				<tbody>
				{recording.steps.map((row, index) => (
					<tr key={index} className="recRecordTableRow">
						<td className="recRecordBox">
							<details className="recRecordAccordionDetails">
								<summary className="recRecordAccordionSummary">
									<span>{row.modified_description || row.description}</span>
								</summary>
								{row.description.split('\n').map((line, i) => (
									<div key={i} className="recRecordLine">{line}</div>
								))}
							</details>
						</td>
					</tr>
				))}
				</tbody>
			</table>
		</div>
	);
};

export default RecordingRecording;
