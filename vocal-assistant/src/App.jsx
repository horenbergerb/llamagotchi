import "./App.css";
import { useState, useRef, useEffect } from "react";
import AudioRecorder from "./AudioRecorder";
import io from 'socket.io-client';

const socket = io('http://localhost:5005');

const App = () => {
    const [audioQueue, setAudioQueue] = useState([]);
    const [isPlaying, setIsPlaying] = useState(false);

    const playAudio = async () => {
        if (audioQueue.length > 0) {
            setIsPlaying(true);
            const audioUrl = audioQueue[0]; // Get the next audio URL without modifying the array
            setAudioQueue(audioQueue.slice(1)); // Use slice to produce a new array without the first element
            const audio = new Audio(audioUrl);
            audio.onended = () => setIsPlaying(false);  // Play the next audio when this one ends
            await audio.play();
        }
    }

    const onAudioReady = (data) => {
        const audioUrl = `http://localhost:5005/download/${data.filename}?cb=` + new Date().getTime();
        setAudioQueue([...audioQueue, audioUrl]);  // Queue the audio URL
    };

    useEffect(() => {
        socket.on('audio.ready', onAudioReady);
        return () => socket.off('audio.ready');
    }, []);

    useEffect(() => {
        if (!isPlaying) {
            playAudio();
        }
    }, [isPlaying, audioQueue]);

    return (
        <div>
            <h1>React Audio Recorder</h1>
            <AudioRecorder />
        </div>
    );
};
export default App;