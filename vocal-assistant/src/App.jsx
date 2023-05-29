import "./App.css";
import { useState, useRef } from "react";
import AudioRecorder from "./AudioRecorder";


const App = () => {
    return (
        <div>
            <h1>React Audio Recorder</h1>
            <AudioRecorder />
        </div>
    );
};
export default App;