import { useState } from "react";
import { useNavigate } from "react-router-dom";

const AppBar = ({ userData }) => {
	const navigate = useNavigate();
	const [activeTab, setActiveTab] = useState(0);
	
	const handleTabClick = (index) => {
		setActiveTab(index);
		switch (index) {
			case 0:
				navigate("/");
				break;
			case 1:
				navigate("/preferences");
				break;
			case 2:
				navigate("/recording");
				break;
			case 3:
				navigate("/annotation");
				break;
			default:
				break;
		}
	};
	
	return (
		<div>
			{userData ? (
				<Tabs activeTab={activeTab} onTabClick={handleTabClick}>
					<Tab label="Home" />
					<Tab label="Preferences" />
					<Tab label="Recording" />
					<Tab label="Annotation" />
				</Tabs>
			) : null}
		</div>
	);
}

const Tabs = ({ activeTab, onTabClick, children }) => {
	return (
		<div>
			{React.Children.map(children, (child, index) => {
				return React.cloneElement(child, {
					active: index === activeTab,
					onClick: () => onTabClick(index),
				});
			})}
		</div>
	);
}

const Tab = ({ label, active, onClick }) => {
	return (
		<div
			style={{
				backgroundColor: active ? "grey" : "white",
				display: "inline-block",
				padding: "10px",
				cursor: "pointer",
			}}
			onClick={onClick}
		>
			{label}
		</div>
	);
}

export default AppBar;
