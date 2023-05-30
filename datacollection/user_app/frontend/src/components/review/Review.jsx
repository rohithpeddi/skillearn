import Home from "../home/Home";

const Review = (props) => {
	const {userData, environment, activities, setUserData, setActivities, setEnvironment} = props;
	
	return (
		<div className="reviewContainer">
			<Home userData={userData}
			      environment={environment}
			      activities={activities}
			      setUserData={setUserData}
			      setEnvironment={setEnvironment}
			      setActivities={setActivities} />
		</div>
	);
	
};


export default Review;