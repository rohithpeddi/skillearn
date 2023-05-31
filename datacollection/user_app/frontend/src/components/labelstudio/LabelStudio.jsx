import AppBar from "../atoms/AppBar";
import "./LabelStudio.css";
import {useEffect, useState} from "react";
import API_BASE_URL from "../../config";
import axios from "axios";
import {Table} from "@mui/material";

const LabelStudio = (props) => {
	
	const {userData, environment, activities, setUserData, setActivities, setEnvironment} = props;
	
	const [annotationActivities, setAnnotationActivities] = useState(null);
	
	const [activityIdToActivityNameMap, setActivityIdToActivityNameMap] = useState({});
	
	useEffect(() => {
		let url = `${API_BASE_URL}/users/${userData.id}/annotation/assignments`;
		axios.get(url)
			.then(response => {
				setAnnotationActivities(response.data);
				console.log(response.data);
			})
			.catch(error => {
				alert("Error: " + error)
				console.log(error);
			});
	}, []);
	
	useEffect(() => {
		let tempActivityIdToActivityNameMap = {};
		
		activities.forEach(activity => {
			tempActivityIdToActivityNameMap[activity.id] = activity.name;
		});
		
		setActivityIdToActivityNameMap(tempActivityIdToActivityNameMap);
	}, [activities]);
	
	const handleCreateProjectsButtonClick = (annotationActivity) => {

	}
	
	const handleDeleteProjectsButtonClick = (annotationActivity) => {

	}
	
	const handleBackupAnnotationsButtonClick = (annotationActivity) => {

	}
	
	const handleCreateRecordingProjectButtonClick = (annotationActivitiyRecording) => {

	}
	
	const handleDeleteRecordingProjectButtonClick = (annotationActivitiyRecording) => {

	}
	
	const handleBackupRecordingAnnotationButtonClick = (annotationActivitiyRecording) => {

	}
	
	
	return (
		<div className="labelStudioContainer">
			<div className="labelStudioHeader">
				<AppBar userData={userData} />
			</div>
			
			<div className="labelStudioContent">
				<div className="labelStudioContentHeader">
					<h1>Label Studio Projects Window</h1>
				</div>
				
				<div className="labelStudioContentBody">
					{
						annotationActivities?.map((annotationActivity, annotationActivityIndex) => (
							<div className="labelStudioActivityContainer" key={annotationActivityIndex}>
								<Table className="labelStudioActivityRecordingsTable" striped bordered hover>
									<thead>
									<tr>
										<th>{activityIdToActivityNameMap[annotationActivity.activity_id]}</th>
										<th><button className="labelStudioButtonCreate" onClick={(annotationActivity) => handleCreateProjectsButtonClick(annotationActivity)}>Create Projects</button></th>
										<th><button className="labelStudioButtonDelete" onClick={(annotationActivity) => handleDeleteProjectsButtonClick(annotationActivity)}>Delete Projects</button></th>
										<th><button className="labelStudioButtonBackup" onClick={(annotationActivity) => handleBackupAnnotationsButtonClick(annotationActivity)}>Backup Annotations</button></th>
									</tr>
									</thead>
									<tbody>
									{annotationActivity.recordings.map((annotationActivityRecording, annotationActivityRecordingIndex) => (
										<tr key={annotationActivityRecordingIndex}>
											<td>{annotationActivityRecording.id}</td>
											<td><button className="labelStudioButtonCreate" onClick={(annotationActivityRecording) => handleCreateRecordingProjectButtonClick(annotationActivityRecording)}>Create Recording Project</button></td>
											<td><button className="labelStudioButtonDelete" onClick={(annotationActivityRecording) => handleDeleteRecordingProjectButtonClick(annotationActivityRecording)}>Delete Recording Project</button></td>
											<td><button className="labelStudioButtonBackup" onClick={(annotationActivityRecording) => handleBackupRecordingAnnotationButtonClick(annotationActivityRecording)}>Backup Recording Annotation</button></td>
										</tr>
									))}
									</tbody>
								</Table>
							</div>
							
							))
					}
				
				</div>
			</div>
		</div>
	);
	
};

export default LabelStudio;