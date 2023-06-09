import { useState, useRef } from "react";

const mimeType = "audio/wav";

const AudioRecorder = () => {
	const [permission, setPermission] = useState(false);

	const mediaRecorder = useRef(null);

	const [recordingStatus, setRecordingStatus] = useState("inactive");

	const [stream, setStream] = useState(null);

	const [audio, setAudio] = useState(null);

	const [audioChunks, setAudioChunks] = useState([]);

	const getMicrophonePermission = async (event) => {
		event.preventDefault();
		if ("MediaRecorder" in window) {
			try {
				const mediaStream = await navigator.mediaDevices.getUserMedia({
					audio: true,
					video: false,
				});
				setPermission(true);
				setStream(mediaStream);
			} catch (err) {
				alert(err.message);
			}
		} else {
			alert("The MediaRecorder API is not supported in your browser.");
		}
	};

	const startRecording = async (event) => {
		event.preventDefault();
		setRecordingStatus("recording");
		const media = new MediaRecorder(stream, { type: mimeType });

		mediaRecorder.current = media;

		mediaRecorder.current.start();

		let localAudioChunks = [];

		mediaRecorder.current.ondataavailable = (event) => {
			event.preventDefault();
			if (typeof event.data === "undefined") return;
			if (event.data.size === 0) return;
			localAudioChunks.push(event.data);
		};

		setAudioChunks(localAudioChunks);
	};

	const stopRecording = (event) => {
		event.preventDefault();
		setRecordingStatus("inactive");
		mediaRecorder.current.stop();

		mediaRecorder.current.onstop = () => {
			const audioBlob = new Blob(audioChunks, { type: mimeType });
			const audioUrl = URL.createObjectURL(audioBlob);

			setAudio(audioUrl);

			setAudioChunks([]);

            // Create form data that contain the recording.
            let formData = new FormData();
            formData.append("input_audio_file", audioBlob);

            // Send the form data to the server.
            fetch('http://localhost:5005/upload-input-audio', {
                method: "POST",
                cache: "no-cache",
                body: formData,
                mode: 'cors'
            }).then(resp => {
                if (resp.status === 200) {
					// Reset recording state
					setAudio(null);
					setAudioChunks([]);
					setRecordingStatus("inactive");
                } else {
                console.error("Error:", resp)
                }
            }).catch(err => {
                console.error(err);
            });
		};
	};

	return (
		<div>
			<main>
				<div className="audio-controls">
					{!permission ? (
						<button onClick={getMicrophonePermission} type="button">
							Get Microphone
						</button>
					) : null}
					{permission && recordingStatus === "inactive" ? (
						<button onClick={startRecording} type="button">
							Start Recording
						</button>
					) : null}
					{recordingStatus === "recording" ? (
						<button onClick={stopRecording} type="button">
							Stop Recording
						</button>
					) : null}
				</div>
			</main>
		</div>
	);
};

export default AudioRecorder;
