from django.shortcuts import render, redirect
import speech_recognition as sr
from django.http import HttpResponse
from .forms import AudioForm
from .models import Audio, TestText
import os
from django.conf import settings
from django.core.files import File
from google.cloud import speech



# Create your views here.
r = sr.Recognizer()
mic = sr.Microphone()

def recorded_home(request):
    return render(request, 'speechtotext/home.html')


def speechtotext_googlecloudapi(audio_saved, save_to_text=None):
    text = ""
    file_path = settings.MEDIA_ROOT+str(audio_saved.audio_file)
    client = speech.SpeechClient()
    with open(file_path, "rb") as audio_file:
        audio_data = audio_file.read()
    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-IN",
    )
    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        text = text+result.alternatives[0].transcript
    if len(text)>0:
        if save_to_text == "Yes":
            TestText.objects.create(text=text)
            data = TestText.objects.filter(text__icontains = text)
            text = ""
            for i in data:
                text = text+i.text+"\n"
    else:
        text = "No Audio detected"
    return text

def speechtotext_pythonlibrary(audio_saved, save_to_text=None):
    text = ""
    file_path = settings.MEDIA_ROOT+str(audio_saved.audio_file)
    with sr.AudioFile(file_path) as srs:
        try:
            r.adjust_for_ambient_noise(srs)
            audio = r.record(srs)
            text = r.recognize_google(audio,language="en-US")
            if save_to_text == "Yes":
                TestText.objects.create(text=text)
                data = TestText.objects.filter(text__icontains = text)
                text = ""
                for i in data:
                    text = text+i.text+"\n"
        except sr.UnknownValueError:
            text = "Speech recognition could not understand audio"
        except sr.RequestError as e:
            text = f"Could not request results from Google Speech Recognition service; {e}"
    return text

def record_audio_upload(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == "POST":
        audio = request.FILES.get('audio')
        audio_saved = Audio.objects.create(audio_file=audio)
        
        text = speechtotext_googlecloudapi(audio_saved, save_to_text = "Yes")
        # text = speechtotext_pythonlibrary(audio_saved, save_to_text = "Yes")
        return HttpResponse(text)

    elif request.method == 'POST':
        form = AudioForm(request.POST, request.FILES)
        if form.is_valid():
            audio = form.cleaned_data['audio_file']
            audio = Audio.objects.create(audio_file=audio)

            text = speechtotext_googlecloudapi(audio)
            # text = speechtotext_pythonlibrary(audio)

            return render(request,'speechtotext/upload_file.html', {'form': form, 'data':str(text)})
    form = AudioForm()
    return render(request, 'speechtotext/upload_file.html', {'form': form})





def record_audio_mic(request):
    file_name = '/audio_files/microphone_gen.wav'
    file_path = settings.MEDIA_ROOT+file_name
    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=15, phrase_time_limit=5)
        
        # write audio to a WAV file
        with open(file_path, "wb") as f:
            f.write(audio.get_wav_data())
        
        # save into db audio file
        local_file = open(file_path, 'rb')
        djangofile = File(local_file)
        audio_save = Audio()
        audio_save.audio_file.save('audio_record.wav', djangofile, save=True)
        local_file.close()

        try:
            text = r.recognize_google(audio, language='en-IN')
            return render(request,'speechtotext/upload_file.html', {'data':str(text)})
        except sr.UnknownValueError:
            message = "Speech recognition could not understand audio"
            return render(request, 'speechtotext/upload_file.html', {'data':message})
        except sr.RequestError as e:
            message = f"Could not request results from Google Speech Recognition service; {e}"
            return render(request, 'speechtotext/upload_file.html', {'data':message})



