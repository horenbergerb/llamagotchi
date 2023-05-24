import whisper
import pyaudio
import wave
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from llama_cpp import Llama
import os
import numpy as np
os.environ["SUNO_OFFLOAD_CPU"] = "True"
os.environ["SUNO_USE_SMALL_MODELS"] = "True"

preload_models(
text_use_small=True,
coarse_use_small=True,
fine_use_gpu=True,
coarse_use_gpu=True,
fine_use_small=True,
text_use_gpu=True
)

def get_audio_input(seconds=3, filename='output.wav'):
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 2
    fs = 44100  # Record at 44100 samples per second

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()


model = whisper.load_model("base")

def transcribe_audio(filename='output.wav'):
    global model

    result = model.transcribe("output.wav")
    print(result["text"])
    return result["text"]

prompt_template = """{prompt}

### Response:
"""

model_bin = "/media/captdishwasher/Samshmung/horenbergerb/llama/llama.cpp/models/Wizard-Vicuna-13B-Uncensored.ggmlv3.q5_0.bin"
#model_bin = "/media/captdishwasher/Samshmung/horenbergerb/llama/llama.cpp/models/WizardLM-30B-Uncensored.ggmlv3.q5_0.bin"
LLM = Llama(model_path=model_bin, n_ctx=2048, n_batch=512, n_gpu_layers=12)

def complete_instruction(instruction):
    global LLM

    prompt = prompt_template.format(prompt=instruction)
    tokens = LLM.tokenize(prompt.encode('utf-8'))
    print('Input prompt: {}'.format(instruction))
    print('Generating...')
    output = LLM(prompt, top_k=0, top_p=1, temperature=0.7, tfs_z=0.70, repeat_penalty=1.1, max_tokens=300)
    print(output['choices'][0]['text'])
    return output['choices'][0]['text']

def play_wav_file(filename='voice.wav'):
    # Set chunk size of 1024 samples per data frame
    chunk = 1024  

    # Open the sound file 
    wf = wave.open(filename, 'rb')

    # Create an interface to PortAudio
    p = pyaudio.PyAudio()

    # Open a .Stream object to write the WAV file to
    # 'output = True' indicates that the sound will be played rather than recorded
    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    # Read data in chunks
    data = wf.readframes(chunk)

    # Play the sound by writing the audio data to the stream
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # Close and terminate the stream
    stream.close()
    p.terminate()

def make_voice_response(response, outfile='voice.wav'):
    audio_array = generate_audio(response, history_prompt='v2/en_speaker_6')
    i = np.iinfo(np.int16)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    audio_array = (audio_array * abs_max + offset).clip(i.min, i.max).astype(np.int16)
    write_wav(outfile, SAMPLE_RATE, audio_array)

if __name__ == '__main__':
    while True:
        seconds = input("Enter a number of seconds:")
        get_audio_input(seconds=int(seconds))
        instruction = transcribe_audio()
        response = complete_instruction(instruction)
        for sentence in response.split('.'):
            # terminate if the sentence is just whitespace
            if not sentence.strip():
                break
            print('Converting sentence to voice')
            print('Sentence: {}'.format(sentence))
            make_voice_response(sentence + '.')
            print('Playing voice out loud')
            play_wav_file()
            print('Done converting and playing sentence')