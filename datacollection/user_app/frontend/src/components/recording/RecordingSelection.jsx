import React, {useEffect, useState} from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Button, FormControl, InputLabel, Select, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@material-ui/core';
import axios from 'axios';
import {MenuItem} from "@mui/material";

const useStyles = makeStyles(theme => ({
	root: {
		display: 'flex',
		width: '100%',
	},
	leftSection: {
		width: '20%',
		marginRight: '20px',
	},
	rightSection: {
		width: '80%',
	},
	formControl: {
		margin: theme.spacing(1),
		minWidth: 120,
	},
	table: {
		minWidth: 650,
	},
}));


const RecordingSelection = (props) => {
	
	const {userData, environment, activities, setRecording} = props;
	
	const [environmentScheduledActivities, setEnvironmentScheduledActivities] = useState([])
	const [activityIdToMistakeBoolean, setActivityIdToMistakeBoolean] = useState({})
	const [activityIdToName, setActivityIdToName] = useState({})
	
	const classes = useStyles();
	const [selectedActivityId, setSelectedActivityId] = useState('');
	const [recordingData, setRecordingData] = useState([]);
	
	useEffect(() => {
		
		const idToBooleanMap = {};
		const idToActivityNameMap = {}
		const environmentSchedule = userData["recording_schedules"][environment];
		
		const normalActivities = environmentSchedule["normal"];
		const mistakeActivities = environmentSchedule["mistake"];
		const recordedActivities = environmentSchedule["recorded"];
		
		const filteredNormalActivities = normalActivities.filter((activity_id) => !recordedActivities.includes(activity_id));
		const filteredMistakeActivities = mistakeActivities.filter((activity_id) => !recordedActivities.includes(activity_id));
		
		filteredNormalActivities.forEach(activity_id => {
			idToBooleanMap[activity_id] = false
		});
		
		filteredMistakeActivities.forEach(activity_id => {
			idToBooleanMap[activity_id] = true
		});
		
		setActivityIdToMistakeBoolean(idToBooleanMap)
		setEnvironmentScheduledActivities([...filteredNormalActivities, ...filteredMistakeActivities])
		
		activities.map((activity) => idToActivityNameMap[activity.id] = activity.name)
		setActivityIdToName(idToActivityNameMap)
		
		}, [userData, environment, activities]	);
	
	
	const handleButtonClick = async () => {
		try {
			const response = await axios.get('http://localhost:5000/activities/${selectedActivityId}/unassigned/recordings');
			setRecordingData(response.data);
		} catch (error) {
			console.error('API call failed:', error);
		}
	};
	
	return (
		<div className={classes.root}>
			
			<div className={classes.leftSection}>
				<FormControl className={classes.formControl}>
					<InputLabel id="dropdown-label">Select Activity</InputLabel>
					<Select
						labelId="dropdown-label"
						value={selectedActivityId}
						onChange={event => setSelectedActivityId(event.target.value)}
					>
						{
							environmentScheduledActivities.map((activityId) => {
								return (
									<MenuItem value={activityId}>{activityIdToName[activityId]}</MenuItem>
								)
							})
						}
					</Select>
				</FormControl>
				<Button variant="contained" color="primary" onClick={event => handleButtonClick(event.target.value)}>Fetch Recording</Button>
			</div>
			
			
			<div className={classes.rightSection}>
				<TableContainer component={Paper}>
					<Table className={classes.table} aria-label="table">
						<TableHead>
							<TableRow>
								<TableCell>Column 1</TableCell>
								<TableCell>Column 2</TableCell>
								<TableCell>Column 3</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							{recordingData.map(row => (
								<TableRow key={row.id}>
									<TableCell component="th" scope="row">
										{row.column1}
									</TableCell>
									<TableCell>{row.column2}</TableCell>
									<TableCell>{row.column3}</TableCell>
								</TableRow>
							))}
						</TableBody>
					</Table>
				</TableContainer>
			</div>
		</div>
	);
	
}

export default RecordingSelection;