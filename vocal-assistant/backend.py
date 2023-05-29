from flask import Flask, request, abort, send_file, current_app, make_response
from mimetypes import guess_extension
from pydub import AudioSegment
import wave
import sys
import os

app = Flask(__name__)

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
            dst = os.path.join(
                'audio_inputs/',
                'audio_record_{i}.wav'.format(i=i))
            if not os.path.exists(dst): break
            i += 1

        # Save the file to disk.
        file.save(dst)

        response = make_response('', 200)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
        return response
 
    response = make_response('Uh oh', 400)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    return response  

@app.route('/reverse-audio', methods=['POST'])
def reverse_audio():
    audio_file = request.files['audio']
    
    try:
        # Validate and load the WAV file
        audio = wave.open(audio_file, 'rb')
    except wave.Error:
        return "Invalid audio file format. Please upload a valid WAV file."

    # Convert the audio data to an AudioSegment for processing
    audio_data = AudioSegment.from_wav(audio_file)
    reversed_audio = audio_data.reverse()

    reversed_audio_path = 'reversed_audio.wav'
    reversed_audio.export(reversed_audio_path, format='wav')

    # Close the WAV file
    audio.close()

    return send_file(reversed_audio_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
