import React, { useState, useEffect } from 'react';
import {
	Button,
	TableContainer,
	Table,
	TableHead,
	TableRow,
	TableCell,
	TableBody,
	Paper,
	Typography
} from '@mui/material';
import axios from 'axios';
import "./RecordingSelection.css";
import RecordingSelectionCard from "./RecordingSelectionCard";

const RecordingSelection = (props) => {
	
	const {userData, environment, activities, recording, setRecording} = props;
	
	const [environmentNormalActivityIds, setEnvironmentNormalActivityIds] = useState([]);
	const [environmentMistakeActivityIds, setEnvironmentMistakeActivityIds] = useState([]);
	
	const [activityIdToActivityName, setActivityIdToActivityName] = useState({});
	
	const selectRecording = async () => {
		try {
			let url = `http://localhost:5000/users/${userData.id}/select/recordings/${recording.id}`;
			const response = await axios.post(url);
			setRecording(response.data);
		} catch (error) {
			console.error(error);
		}
	};
	
	useEffect(() => {
		if (
			userData &&
			environment &&
			activities &&
			userData.recording_schedules &&
			userData.recording_schedules[environment]
		) {
			
			setEnvironmentNormalActivityIds(
				userData.recording_schedules[environment].normal_activities
			);
			
			setEnvironmentMistakeActivityIds(
				userData.recording_schedules[environment].mistake_activities
			);
			
		}
		
		let activityIdToActivityNameTemp = {};
		activities.forEach((activity) => {
			activityIdToActivityNameTemp[activity.id] = activity.name;
		});
		
		setActivityIdToActivityName(activityIdToActivityNameTemp);
	}, [userData, environment, activities]);
	
	return (
		
		<div className="recordingSelectionContainer">
			<div className="recordingSelectionContent">
				<div className="recordingSelectionGridContainer">
					<div className="recordingSelectionGridItem">
						<RecordingSelectionCard
							userData={userData}
							environment={environment}
							setRecording={setRecording}
							activityIdToActivityName={activityIdToActivityName}
							activityIds={environmentNormalActivityIds}
							label={"Normal"}
						/>
					</div>
					<div className="recordingSelectionGridItem">
						<RecordingSelectionCard
							userData={userData}
							environment={environment}
							setRecording={setRecording}
							activityIdToActivityName={activityIdToActivityName}
							activityIds={environmentMistakeActivityIds}
							label={"Mistake"}
						/>
					</div>
				</div>
				<div className="recordingDisplayGridContainer">
					{
						recording ? (
							<div>
								<div className="recordingDisplayGridItem">
									<TableContainer component={Paper}>
										<Table>
											<TableHead>
												<TableRow>
													<TableCell>Recording Steps</TableCell>
												</TableRow>
											</TableHead>
											<TableBody>
												{recording?.steps.map((step) => (
													<TableRow>
														<TableCell>{step}</TableCell>
													</TableRow>
												))}
											</TableBody>
										</Table>
									</TableContainer>
								</div>
							
								<div className="recordingDisplayGridItem">
									<Button variant="contained" color="primary" onClick={selectRecording} className="recordingSelectionButton">
										Select Recording
									</Button>
								</div>
								
							</div>
							
							) : (
								<div className="recordingDisplayGridItem">
									<Typography variant="h6" color="textSecondary">
										No recording selected
									</Typography>
								</div>
							)
					}
				</div>
			</div>
		</div>
	);
};

export default RecordingSelection;
