import AppBar from "../atoms/AppBar";
import ActivityTable from "./ActivityTable";
import ActivitySelector from "./ActivitySelector";
import "./Preferences.css"

const Preferences = (props) => {
	const {userData, environment, activities} = props
	
	return (
		<div>
			<div className="header">
				<AppBar userData={userData} />
			</div>
			
			<div className="preferences-container">
				
				<div className="content">
					
					<div className="selection">
						
						{/*List of all selected activities*/}
						<div className="selected-preferences">
							{userData && userData.activity_preferences ? (
								<ActivityTable
									activityIdList={userData.activity_preferences}
									activities={activities}
									label={"Preferences"}
								/>
							) : (
								<div className="no-preferences">No preferences found.</div>
							)}
						</div>
						
						
						{/*List of all normal activities in current environment*/}
						<div className="environment-selection">
							{userData && userData.recording_schedules && userData.recording_schedules[environment] && userData.recording_schedules[environment].normal_activities ? (
								<ActivityTable
									activityIdList={userData.recording_schedules[environment].normal_activities}
									activities={activities}
									label={"Normal Activities"}
								/>
							) : (
								<div className="no-activities">No normal activities selected.</div>
							)}
						</div>
						
						
						{/*List of all mistake activities in current environment*/}
						<div className="environment-selection">
							{userData && userData.recording_schedules && userData.recording_schedules[environment] && userData.recording_schedules[environment].mistake_activities ? (
								<ActivityTable
									activityIdList={userData.recording_schedules[environment].mistake_activities}
									activities={activities}
									label={"Mistake Activities"}
								/>
							) : (
								<div className="no-activities">No mistake activities selected.</div>
							)}
						</div>
					</div>
					
					
					<div className="update-selection">
						
						<div className="veg-selection">
							{userData ? (
								<ActivitySelector
									activityPreferences={userData.activity_preferences || []}
									activities={activities}
									activityCategory={"Veg"}
									userId={userData.id}
								/>
							) : (
								<div>No preferences found.</div>
							)}
						</div>
						
						<div className="non-veg-selection">
							{userData ? (
								<ActivitySelector
									activityPreferences={userData.activity_preferences || []}
									activities={activities}
									activityCategory={"Non-Veg"}
									userId={userData.id}
								/>
								
							) : (
								<div>No non-veg preferences found.</div>
							)}
						</div>
					</div>
				</div>
			</div>
		</div>
	)
}

export default Preferences;