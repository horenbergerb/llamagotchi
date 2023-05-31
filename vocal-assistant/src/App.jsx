import "./App.css";
import { useState, useRef, useEffect } from "react";
import AudioRecorder from "./AudioRecorder";
import io from 'socket.io-client';

const socket = io('http://localhost:5005');

const App = () => {
    const [audioQueue, setAudioQueue] = useState([]);
    const [isPlaying, setIsPlaying] = useState(false);

    const [text, setText] = useState("");

    const playAudio = async () => {
        if (audioQueue.length > 0) {
            console.log("Starting playAudio");
            setIsPlaying(true);
            const audioUrl = audioQueue[0]; // Get the next audio URL without modifying the array
            setAudioQueue(audioQueue.slice(1)); // Use slice to produce a new array without the first element
            console.log("Frontend playing " + audioUrl);
            const audio = new Audio(audioUrl);
            audio.onended = () => setIsPlaying(false);  // Play the next audio when this one ends
            await audio.play();
            console.log("Frontend done playing " + audioUrl);
        }
    }

    const onAudioReady = (data) => {
        const audioUrl = `http://localhost:5005/download/${data.filename}?cb=` + new Date().getTime();
        setAudioQueue(prevAudioQueue => [...prevAudioQueue, audioUrl]);  // Queue the audio URL
        console.info("Frontend received " + audioUrl);
    };

    const onTextReady = (data) => {
        setText(data.text);  // Assume 'text' is the property containing the text in the data object
    };
    

    useEffect(() => {
        socket.on('audio.ready', onAudioReady);
        return () => socket.off('audio.ready');
    }, []);

    useEffect(() => {
        socket.on('text.ready', onTextReady);
        return () => socket.off('text.ready');
    }, [text]);  // Add 'text' to the dependency array    

    useEffect(() => {
        if (!isPlaying) {
            playAudio();
        }
    }, [isPlaying, audioQueue]);

    return (
        <div>
            <h1>Whisper LLaMa Bark</h1>
            <AudioRecorder />
            <p>{text}</p>
        </div>
    );
};
export default App;