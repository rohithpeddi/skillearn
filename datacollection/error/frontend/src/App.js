import React, {useState} from 'react'
import Select from 'react-select';
import "./App.css"

function convert(arr) {
    return arr.map((element) => {
        return {value: element, label: element}
    });
}

function CustomDropdown({
                            arr,
                            setSelectedActivity,
                            setSelectedPlace,
                            setSelectedPerson,
                            setSelectedRecordingNumber,
                            setSelectedActivityType,
                            menu_number
                        }) {

    const handleChange = (e) => {
        if (menu_number === 0) {
            setSelectedActivity(e.value);
        }
        if (menu_number === 1) {
            setSelectedPlace(e.value);
        }
        if (menu_number === 2) {
            setSelectedPerson(e.value);
        }
        if (menu_number === 3) {
            setSelectedRecordingNumber(e.value);
        }
        if (menu_number === 4) {
            setSelectedActivityType(e.value);
        }
    };
    return (
        <div>
            <Select options={convert(arr)} onChange={handleChange}/>
        </div>
    );
}


const App = () => {
    const activity = ["COFFEE", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10"];
    const place = ["PL1", "PL2", "PL3", "PL4", "PL5", "PL6", "PL7"];
    const person = ["P1", "P2", "P3", "P4", "P5", "P6"];
    const recording_number = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const activity_type = ["STANDARD", "ERROR"];

    const [selectedActivity, setSelectedActivity] = useState("NO-ACTIVITY-SELECTED");
    const [selectedPlace, setSelectedPlace] = useState("NO-PLACE-SELECTED");
    const [selectedPerson, setSelectedPerson] = useState("NO-PERSON-SELECTED");
    const [selectedRecordingNumber, setSelectedRecordingNumber] = useState("NO-RECORDING-NUMBER-SELECTED");
    const [selectedActivityType, setSelectedActivityType] = useState("NO-ACTIVITY-TYPE-SELECTED");


    const renderImages = () => {
        const step_heading = [
            'STEP - 1',
            'STEP - 2',
            'STEP - 3',
            'STEP - 4',
            'STEP - 5',
            'STEP - 6',
            'STEP - 7',
            'STEP - 8',
            'STEP - 9',
            'STEP - 10',
            'STEP - 11',
            'STEP - 12',
            'STEP - 13',
            'STEP - 14',
            'STEP - 15'
        ];
        const step_description = [
            ' Complete description corresponding to step1 is here',
            'STEP - 2 complete description. all details corresponding to step2 is here',
            'STEP - 3 complete description. all details corresponding to step3 is here',
            'STEP - 4 complete description. all details corresponding to step4 is here',
            'STEP - 5 complete description. all details corresponding to step5 is here',
            'STEP - 6 complete description. all details corresponding to step6 is here',
            'STEP - 7 complete description. all details corresponding to step7 is here',
            'STEP - 8 complete description. all details corresponding to step8 is here',
            'STEP - 9 complete description. all details corresponding to step9 is here',
            'STEP - 10 complete description. all details corresponding to step10 is here',
            'STEP - 11 complete description. all details corresponding to step11 is here',
            'STEP - 12 complete description. all details corresponding to step12 is here',
            'STEP - 13 complete description. all details corresponding to step13 is here',
            'STEP - 14 complete description. all details corresponding to step14 is here',
            'STEP - 15 complete description. all details corresponding to step15 is here'
        ];

        return step_heading.map((heading_element, index) => (
            <div>
                <div>
                    <h2 className="step_header">{heading_element}</h2>
                    <content className="step_header">{step_description[index]})</content>
                </div>

                <div className="flxBtn">
                    <div>
                        <button className="button button1">START</button>
                    </div>
                    <div>
                        <button className="button button1">STOP</button>
                    </div>
                    <div>
                        <button className="button button1">DELETE</button>
                    </div>
                </div>

            </div>
        ))
    }


    const generateDiv = () => {
        //replace this with onclick upload button - use useState for setting up response
        const res = ['S1', 'S2', 'S3', 'S4', 'S5']
        return res.map((elem, index) => {
            return <div key={index}>
                <h4>{elem}</h4>
            </div>
        })
    }


    return (
        <div className='flx'>
            <div>
                <div>
                    <h4>ACTIVITY</h4>
                    <CustomDropdown arr={activity} setSelectedActivity={setSelectedActivity} menu_number={0}/>
                </div>
                <div>
                    <h4>PLACE</h4>
                    <CustomDropdown arr={place} setSelectedPlace={setSelectedPlace} menu_number={1}/>
                </div>
                <div>
                    <h4>PERSON</h4>
                    <CustomDropdown arr={person} setSelectedPerson={setSelectedPerson} menu_number={2}/>
                </div>
                <div>
                    <h4>RECORDING NUMBER</h4>
                    <CustomDropdown arr={recording_number} setSelectedRecordingNumber={setSelectedRecordingNumber}
                                    menu_number={3}/>
                </div>
                <div>
                    <h4>TYPE</h4>
                    <CustomDropdown arr={activity_type} setSelectedActivityType={setSelectedActivityType}
                                    menu_number={4}/>
                </div>
            </div>
            <div className="step_header">
                <div>
                    <div className="flxBtn">
                        <div>
                            <button className="button button1">DATA COLLECTION</button>
                        </div>
                        <div>
                            <button className="button button1">DATA ANNOTATION</button>
                        </div>
                        <div>
                            <button className="button button1">APPLICATION</button>
                        </div>
                    </div>
                </div>
                <div className="step_header">
                    <div className="step_header">
                        <h1> {selectedActivity} </h1>
                        <div className="flxBtn">
                            <div>
                                <button className="button button1">START</button>
                            </div>
                            <div>
                                <button className="button button1">STOP</button>
                            </div>
                            <div>
                                <button className="button button1">UPLOAD</button>
                            </div>
                        </div>
                    </div>
                    <div className="rossDiv">
                        {renderImages()}
                    </div>
                </div>
            </div>
            <div>
                <div>
                    <h4>STEP COMPLETION STATUS</h4>
                    {generateDiv()}
                </div>
                <div>
                    <h4>UPLOAD QUEUE</h4>
                    {generateDiv()}
                </div>
            </div>
        </div>
    );
};

export default App;

