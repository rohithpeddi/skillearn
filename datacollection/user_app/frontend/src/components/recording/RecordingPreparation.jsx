import React from 'react';
import './RecordingPreparation.css';

const RecordingPreparation = (props) => {
	const { userData, environment, activities, recording, setRecording } = props;
	
	const getActivityName = (activityId) => {
		const activity = activities.find((activity) => activity.id === activityId);
		return activity.name;
	};
	
	if (!recording) {
		return (
			<div>
				<h1>Please go back and select an activity to begin preparing for the recording</h1>
			</div>
		);
	}
	
	return (
		<div className="recPrepContainer">
			<table className="recPrepTable">
				<thead>
				<tr className="recPrepTableHeader">
					<th colSpan="4">Preparing activity {getActivityName(recording.activity_id)}</th>
				</tr>
				</thead>
				<tbody>
				{recording.steps.map((row, index) => (
					<tr key={index} className="recPrepTableRow">
						<td className="recPrepBox">
							<details className="recPrepAccordionDetails" open>
								<summary className="recPrepAccordionSummary">
									<span>{row.modified_description || row.description}</span>
								</summary>
								{row.description.split('\n').map((line, i) => (
									<div key={i} className="recPrepLine">{line}</div>
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

export default RecordingPreparation;
