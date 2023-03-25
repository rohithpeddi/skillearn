import React from 'react';
import './RecordingPreparation.css';
import RecordingStepPreparation from "./RecordingStepPreparation";

const RecordingPreparation = (props) => {
	const { userData, environment, activities, recording, setRecording, mistakeTags} = props;
	
	const getActivityName = (activityId) => {
		const activity = activities.find((activity) => activity.id === activityId);
		return activity.name;
	};
	
	const getDescription = (step) => {
		return step.modified_description || step.description;
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
									<span> {getDescription(row)} </span>
								</summary>
								<RecordingStepPreparation
									recording={recording}
									setRecording={setRecording}
									mistakeTags={mistakeTags}
									step={row}
									stepIndex={index} />
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
