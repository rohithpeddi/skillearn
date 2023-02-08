import React, {useEffect, useState} from 'react';
import home3 from './sample_images/1.jpeg';
import {Typography} from "@mui/material";
import Box from "@mui/material/Box";
import './DataCollectionLiveFrame.css'

const DataCollectionLiveFrame = () => {
    const [src, setSrc] = useState('');

    useEffect(() => {
        const updateImage = async () => {
            // const response = await fetch('/Users/akshay/WebstormProjects/skillearn/datacollection/error/frontend/sample_images/1.jpeg');
            // const dataUrl = await response.blob();
            setSrc('/Users/akshay/WebstormProjects/skillearn/datacollection/error/frontend/sample_images/1.jpeg');
        };

        updateImage();

        const intervalId = setInterval(updateImage, 3000);
        return () => clearInterval(intervalId);
    }, []);

    return (
        <Box className="data_collection_live_frame">
            <Typography variant="h6" align="center" borderBottom="2px solid"> {"LIVE VIEW"}</Typography>
            <iframe src={home3} width="100%" height="500" frameBorder="0" allowFullScreen/>
        </Box>
    )

};

export default DataCollectionLiveFrame;
