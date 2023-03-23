import React, {useEffect, useState} from "react";
import axios from "axios";
import styles from "./ActivitySelector.css";

const ActivitySelector = ({ activityPreferences, activities, activityCategory, userId }) => {
	const [selectedActivities, setSelectedActivities] = useState([]);
	const [categoryActivities, setCategoryActivities] = useState([]);
	
	useEffect(() => {
		const categoryActivities = activities.filter((activity) => activity.category === activityCategory);
		setCategoryActivities(categoryActivities);
		const categoryActivityPreferences = activityPreferences.filter((activityId) => {
			const activity = activities.find((activity) => activity.id === activityId);
			return activity.category === activityCategory;
		});
		setSelectedActivities(categoryActivityPreferences);
	}, [activityCategory, activities]);
	
	const handleSelectAll = () => {
		const allActivityIds = activities.map((activity) => activity.id);
		setSelectedActivities(allActivityIds);
	};
	
	const handleUnselectAll = () => {
		setSelectedActivities(activityPreferences);
	};
	
	const handleActivitySelect = (activityId) => {
		if (selectedActivities.includes(activityId)) {
			setSelectedActivities(
				selectedActivities.filter((id) => id !== activityId)
			);
		} else {
			setSelectedActivities([...selectedActivities, activityId]);
		}
	};
	
	const handleApiRequest = () => {
		axios
			.post("/api/endpoint", {
				userId: userId,
				selectedActivities: selectedActivities,
			})
			.then((response) => {
				console.log(response.data);
			})
			.catch((error) => {
				console.log(error);
			});
	};
	
	return (
		<div className={styles.activitySelector}>
			<h2>{activityCategory} Preference Selector</h2>
			<div>
				<label htmlFor="select-all">
					<input
						type="checkbox"
						id="select-all"
						onChange={handleSelectAll}
						checked={selectedActivities.length === activities.length}
					/>
					Select All
				</label>
				<label htmlFor="unselect-all">
					<input
						type="checkbox"
						id="unselect-all"
						onChange={handleUnselectAll}
						checked={selectedActivities.length === 0}
					/>
					Undo Select All
				</label>
			</div>
			<div>
				{categoryActivities.map((activity) => (
					<label key={activity.id} htmlFor={`activity-${activity.id}`} className={styles.activityItem}>
						<input
							type="checkbox"
							id={`activity-${activity.id}`}
							value={activity.id}
							onChange={() => handleActivitySelect(activity.id)}
							checked={selectedActivities.includes(activity.id)}
						/>
						{activity.name}
					</label>
				))}
			</div>
			<button onClick={handleApiRequest}>Update {activityCategory} Preferences</button>
		</div>
	);
};

export default ActivitySelector;
