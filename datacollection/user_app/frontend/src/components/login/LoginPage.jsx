import React, { useState } from 'react';
import axios from 'axios';
import AppBar from "../atoms/AppBar";

const LoginPage = (props) => {
	
	const {setUserData, setEnvironment, setActivities} = props
	
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState('');
	
	const handleSubmit = async (event) => {
		event.preventDefault();
		
		try {
			const response = await axios.post('http://localhost:5000/login', { username, password });
			
			if (response.data) {
				setUserData(response.data);
			} else {
				setError('Invalid username or password');
			}
		} catch (err) {
			setError('Something went wrong, please try again');
		}
	};
	
	return (
		<div>
			{/*Define Header component for the AppBar component also display tabs based on loggedIn state*/}
			<div className="header">
				<AppBar userData={} />
			</div>
			
			
			<h1>Login</h1>
			<form onSubmit={handleSubmit}>
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