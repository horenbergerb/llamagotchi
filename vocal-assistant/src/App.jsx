import "./App.css";
import { useState, useRef, useEffect } from "react";
import AudioRecorder from "./AudioRecorder";
import io from 'socket.io-client';

const socket = io('http://localhost:5005');

const App = () => {
    const [audioQueue, setAudioQueue] = useState([]);
    const [isPlaying, setIsPlaying] = useState(false);

    let playbackQueue = Promise.resolve();

    const playAudio = async () => {
        if (audioQueue.length > 0) {
            const audioUrl = audioQueue[0];
            setAudioQueue(audioQueue.slice(1));
    
            // Create a new promise for the current audio and add it to the chain
            playbackQueue = playbackQueue
                .then(() => {
                    return new Promise((resolve) => {
                        const audio = new Audio(audioUrl);
                        audio.onended = resolve;
                        audio.play();
                    });
                })
                .catch(console.error); // Log errors for easier debugging
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