import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

const LoginPage = (props) => {
	const { setUserData, setEnvironment, setActivities } = props;
	
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState('');
	
	const navigate = useNavigate();
	
	const handleSubmit = async (event) => {
		event.preventDefault();
		
		axios
			.post('http://localhost:5000/login', { username, password })
			.then((loginResponse) => {
				if (loginResponse.data) {
					setUserData(loginResponse.data);
				}
				return axios.get('http://localhost:5000/environment');
			})
			.then((environmentResponse) => {
				if (environmentResponse.data) {
					setEnvironment(environmentResponse.data);
				}
				return axios.get('http://localhost:5000/activities');
			})
			.then((activitiesResponse) => {
				if (activitiesResponse.data) {
					setActivities(activitiesResponse.data);
				}
				navigate('/');
			})
			.catch((apiError) => {
				setError(apiError);
			});
	};
	
	return (
		<div className="login-container">
			{/* Define Header component for the AppBar component also display tabs based on loggedIn state */}
			
			<h1>Login</h1>
			<form className="login-form" onSubmit={handleSubmit}>
				<input
					type="text"
					placeholder="Username"
					value={username}
					onChange={(event) => setUsername(event.target.value)}
				/>
				<input
					type="password"
					placeholder="Password"
					value={password}
					onChange={(event) => setPassword(event.target.value)}
				/>
				<button type="submit">Login</button>
			</form>
			{error && <p>{error}</p>}
		</div>
	);
};

export default LoginPage;
