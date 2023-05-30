import React, { useEffect, useState } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Home from './components/home/Home';
import Preferences from './components/preferences/Preferences';
import Recording from './components/recording/Recording';
import Annotation from './components/annotation/Annotation';
import LoginPage from './components/login/LoginPage';
import AdminPage from "./components/admin/AdminPage";
import Review from "./components/review/Review";

const App = () => {
    const [userData, setUserData] = useState(false);
    const [environment, setEnvironment] = useState(false);
    const [activities, setActivities] = useState(false);
    
    useEffect(() => {
        if (!userData) {
            setUserData(false);
            setEnvironment(false);
            setActivities(false);
        }
    }, [userData]);
    
    return (
        <BrowserRouter>
            <div className="App">
                <Routes>
                    {userData ? (
                        userData.username === 'admin' ? (
                            <Route
                                exact
                                path="/admin"
                                element={
                                    <AdminPage
                                        userData={userData}
                                        environment={environment}
                                        activities={activities}
                                        setUserData={setUserData}
                                        setEnvironment={setEnvironment}
                                        setActivities={setActivities}
                                    />
                                }
                            />
                        ) : (
                            <>
                            <Route
                                exact
                                path="/"
                                element={
                                    <Home
                                        userData={userData}
                                        environment={environment}
                                        activities={activities}
                                        setUserData={setUserData}
                                        setEnvironment={setEnvironment}
                                        setActivities={setActivities}
                                    />
                                }
                            />
                            <Route
                                path="/preferences"
                                element={
                                    <Preferences
                                        userData={userData}
                                        environment={environment}
                                        activities={activities}
                                        setUserData={setUserData}
                                        setEnvironment={setEnvironment}
                                        setActivities={setActivities}
                                    />
                                }
                            />
                            <Route
                                path="/recording"
                                element={
                                    <Recording
                                        userData={userData}
                                        environment={environment}
                                        activities={activities}
                                        setUserData={setUserData}
                                        setEnvironment={setEnvironment}
                                        setActivities={setActivities}
                                    />
                                }
                            />
                            <Route
                                path="/review"
                                element={
                                    <Review
                                        userData={userData}
                                        environment={environment}
                                        activities={activities}
                                        setUserData={setUserData}
                                        setEnvironment={setEnvironment}
                                        setActivities={setActivities}
                                    />
                                }
                            />
                            <Route
                                path="/annotation"
                                element={
                                    <Annotation
                                        userData={userData}
                                        environment={environment}
                                        activities={activities}
                                        setUserData={setUserData}
                                        setEnvironment={setEnvironment}
                                        setActivities={setActivities}
                                    />
                                }
                            />
                        </>
                        )
                    ) : (
                        <Route path="*" element={<Navigate to="/login" />} />
                    )}
                    <Route
                        path="/login"
                        element={<LoginPage setUserData={setUserData} setEnvironment={setEnvironment} setActivities={setActivities}/>}
                    />
                </Routes>
            </div>
        </BrowserRouter>
    );
};

export default App;
