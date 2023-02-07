import * as React from 'react';
import Box from '@mui/material/Box';
import Tab from '@mui/material/Tab';
import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import TabPanel from '@mui/lab/TabPanel';
import DataCollection from "./data_collection/DataCollection";

const MainTab = () => {
    const [tabIndex, setTabIndex] = React.useState('1'); // default tab is 1

    const handleChange = (event: React.SyntheticEvent, newValue: any) => {
        setTabIndex(newValue);
    };

    return (
        <Box>
            <TabContext value={tabIndex}>
                <Box>
                    <TabList onChange={handleChange} centered>
                        <Tab label="DATA COLLECTION" value="1"/>
                        <Tab label="DATA ANNOTATION" value="2"/>
                        <Tab label="APPLICATION" value="3"/>
                    </TabList>
                </Box>
                <TabPanel value="1">
                    <DataCollection/>
                </TabPanel>
                <TabPanel value="2">Tab Two</TabPanel>
                <TabPanel value="3">Tab Three</TabPanel>
            </TabContext>
        </Box>
    );
}

export default MainTab;