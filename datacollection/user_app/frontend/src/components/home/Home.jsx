import {useNavigate} from "react-router-dom";
import AppBar from "../atoms/AppBar";
import React from "react";

const Home = (props) => {
	
	const {userData, environment, activities} = props;
	const navigate = useNavigate();
	
	return (
		<div>
			
			<div className="header">
				<AppBar userData={userData} />
			</div>
			
			
			
		</div>
	);
	
}

export default Home;