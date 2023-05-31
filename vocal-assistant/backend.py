from flask import Flask, request, abort, send_file, current_app, make_response, send_from_directory
from flask_socketio import SocketIO, emit
from mimetypes import guess_extension
from pydub import AudioSegment
import wave
import sys
import os
import time
import requests

import whisper
import pyaudio
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from llama_cpp import Llama
import numpy as np
from multiprocessing import Process
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

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

model = whisper.load_model("base")

def transcribe_audio(filename='output.wav'):
    global model

    result = model.transcribe(filename)
    print(result["text"])
    return result["text"]

prompt_template = """{prompt}

### Response:
"""

#model_bin = "/media/captdishwasher/Samshmung/horenbergerb/llama/llama.cpp/models/Wizard-Vicuna-13B-Uncensored.ggmlv3.q5_0.bin"
#model_bin = "/media/captdishwasher/Samshmung/horenbergerb/llama/llama.cpp/models/WizardLM-30B-Uncensored.ggmlv3.q5_0.bin"
#LLM = Llama(model_path=model_bin, n_ctx=2048, n_batch=512, n_gpu_layers=100)

def complete_instruction_kobold(instruction):
    body = {'prompt': prompt_template.format(prompt=instruction),
            'top_k': 0,
            'top_p': 1,
            'temperature': 0.7,
            'tfs': 0.95,
            'top_a': 0.1,
            'rep_pen': 1.1,
            'max_length': 300}
    response = requests.post('http://127.0.0.1:5000/api/v1/generate', json=body)
    print(response.json(), file=sys.stderr)
    socketio.emit('text.ready', {'text': prompt_template.format(prompt=instruction) + response.json()['results'][0]['text']})

    return response.json()['results'][0]['text']

def complete_instruction(instruction):
    global LLM

    prompt = prompt_template.format(prompt=instruction)
    tokens = LLM.tokenize(prompt.encode('utf-8'))
    print('Input prompt: {}'.format(instruction))
    print('Generating...')
    output = LLM(prompt, top_k=0, top_p=1, temperature=0.7, tfs_z=0.70, repeat_penalty=1.1, max_tokens=300)
    print(output['choices'][0]['text'])
    return output['choices'][0]['text']

def make_voice_response(response, outfile='voice.wav'):
    audio_array = generate_audio(response, history_prompt='v2/en_speaker_6')
    i = np.iinfo(np.int16)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    audio_array = (audio_array * abs_max + offset).clip(i.min, i.max).astype(np.int16)
    write_wav(outfile, SAMPLE_RATE, audio_array)

def generate_and_send_responses(input_filename):
    instruction = transcribe_audio(input_filename)
    response = complete_instruction_kobold(instruction)
    #response = 'I love ligma. Ligma is one of the coolest things in the world. We should all eat more ligma every day.'
    counter = 0
    for sentence in response.split('.'):
        sentence = sentence.strip()
        # terminate if the sentence is just whitespace
        if not sentence:
            break
        print('Converting sentence to voice')
        print('Sentence: {}'.format(sentence))
        make_voice_response(sentence + '.', outfile='audio_outputs/voice{}.wave'.format(counter))
        print('Sending sentence to frontend')
        socketio.emit('audio.ready', {'filename': 'voice{}.wave'.format(counter)})
        counter += 1

@app.route('/upload-input-audio', methods=['POST'])
def upload_input_audio():
    if 'input_audio_file' in request.files:
        file = request.files['input_audio_file']
        # Get the file suffix based on the mime type.
        print(file, file=sys.stderr)
        print(file.mimetype, file=sys.stderr)

        # Generate a unique file name with the help of consecutive numbering.
        i = 1
        while True:
            dst = 'audio_record_{i}.wav'.format(i=i)
            if not os.path.exists(os.path.join('audio_inputs/', dst)): break
            i += 1

        # Save the file to disk.
        file.save(os.path.join('audio_inputs/', dst))

        generate_and_send_responses(os.path.join('audio_inputs/', dst))

        response = make_response('', 200)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
        return response
 
    response = make_response('Uh oh', 400)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    return response

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'audio_outputs/'), filename)

if __name__ == '__main__':
    socketio.run(app, port=5005, debug=True)
