import React, {useState} from 'react'
import Select from 'react-select';
import "./App.css"
import Iframe from 'react-iframe'

function convert(arr) {
  return arr.map((element) => {
    return {value: element, label: element}
  });
}

function CustomDropdown({arr}) {
  console.log(convert(arr));
  return (
      <div>
        <Select options={convert(arr)}/>
      </div>
  );
}


const App = () => {
  const recipe_name = ["r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10"];
  const person_id = ["p1", "p2", "p3", "p4", "p5", "p6", "p7"];
  const kitchen_id = ["k1", "k2", "k3", "k4", "k5", "k6"];
  const recording_number = [1,2,3,4,5,6,7,8,9,10]
  //useState
  const getData = async () => {
    console.log("here")
    const getData = await fetch('http://localhost:8000/insert')
    const showData = await getData.json()
    console.log(showData)

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
            <h4>Recipe name</h4>
            <CustomDropdown arr={recipe_name}/>
          </div>
          <div>
            <h4>Person Id</h4>
            <CustomDropdown arr={person_id}/>
          </div>
          <div>
            <h4>Kitchen Id</h4>
            <CustomDropdown arr={kitchen_id}/>
          </div>
          <div>
            <h4>Recording Number or time</h4>
            <CustomDropdown arr={recording_number}/>
          </div>
        </div>
        <div>
          <div className='tc'>
            <button onClick={() => {
              getData()
            }} className="button button1">Info
            </button>
          </div>
          <div className="flxBtn">
            <div>
              <button className="button button1">Green</button>
            </div>
            <div>
              <button className="button button1">Green</button>
            </div>
            <div>
              <button className="button button1">Green</button>
            </div>
          </div>
          <div className='tc'>
            <button className="button button1">Green</button>
          </div>
          <div >
            <Iframe url="https://www.sdrive.app/embed/1ptBQD"
                    width="640px"
                    height="320px"
                    id=""
                    className=""
                    display="block"
                    position="relative"/>

          </div>
        </div>
        <div>
          {generateDiv()}
        </div>
      </div>
  );
};

export default App;

// read step info
// realtime video see
