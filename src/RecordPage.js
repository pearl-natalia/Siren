import React, { useState } from "react";
import axios from "axios";
import "./RecordPage.css"; // Ensure this file exists for styling
import "@fortawesome/fontawesome-free/css/all.min.css";
import MapboxComponent from "./Mapbox";

function RecordPage() {
  const [isRecording, setIsRecording] = useState(false);

  const handleButtonClick = async () => {
    try {
      // Toggle the recording state
      setIsRecording((prevState) => !prevState);

      // Make a POST request
      const response = await axios.post("http://localhost:5000/");
      console.log("Script Output:", response.data.output);
      console.log("Script Error:", response.data.error);
    } catch (error) {
      console.error("Error running script:", error);
    }
  };

  return (
    <div id="recordPage">
      <MapboxComponent />
      <div id="dashcamFootageContainer">
        <div id="dashcamFootage"></div>
        <div id="dashcamInfo">
          <div id="speedLimitBorder">
            <div id="speedLimit">
              <p>
                <strong>
                  SPEED
                  <br />
                  LIMIT
                  <br />
                  <span style={{ fontSize: "40px" }}> 50</span>
                </strong>
              </p>
            </div>
          </div>
        </div>
      </div>
      <button id="recordBtn" onClick={handleButtonClick}>
        <i className={`fas ${isRecording ? "fa-stop" : "fa-play"}`} />
      </button>
    </div>
  );
}

export default RecordPage;
