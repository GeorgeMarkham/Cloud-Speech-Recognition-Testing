import io
import os
from os import listdir
import json
import azure.cognitiveservices.speech as speechsdk
import csv
from time import perf_counter_ns
import psutil
import numpy as np

# --------------------------------------------------
# 
# THIS CODE IS HEAVILY RELATED TO AND INFLUENCED BY THE DOCS https://cloud.google.com/speech-to-text/docs/reference/libraries#client-libraries-install-python
# 

# Also I would reccomend using ffmpeg to recode the timit data set as wav before running, for some reason the SDK doesn't consider 
# the wav files from the timit data set to be readable

# You must have a credentials JSON file which you can get from the GCP Console https://console.cloud.google.com/
# --------------------------------------------------

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "YOUR_APPLICATION_CREDENTIALS_FILE.json"

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


client = speech.SpeechClient()

d = "./timit/"
timit_labels = {}

results = []

bytes_sent = []
file_sizes = []


iostat = psutil.net_io_counters(pernic=False)
start_net_bytes = iostat[0]

with open('./timit.json', 'r') as t:
  timit_labels = json.load(t)
  for f in listdir(d):
    if f.endswith(".wav"):
      inp_f = d+f

      input_text = timit_labels[f.split('_')[1][:-4]]

      file_name = os.path.join(os.path.dirname(__file__), inp_f)

      # Loads the audio into memory
      with io.open(file_name, 'rb') as audio_file:
          content = audio_file.read()
          audio = types.RecognitionAudio(content=content)

          config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='en-GB')

          start = perf_counter_ns()
          response = client.recognize(config, audio)
          end = perf_counter_ns()

          bites = psutil.net_io_counters(pernic=False)[0]

          bytes_sent.append(bites - start_net_bytes) #upload only

          file_size = os.path.getsize(inp_f)

          file_sizes.append(file_size)

          print(file_size, bytes_sent[-1])

          start_net_bytes = bites

          result_transcript = response.results[0].alternatives[0].transcript
          print("RESULT:\t", result_transcript)

          res_obj = [audio_file.name, input_text, result_transcript, end-start]
          results.append(res_obj)          


with open('test_gcp.csv', 'w') as csv_out:
  csv_writer = csv.writer(csv_out)
  csv_writer.writerow(['file_name', 'original_text', 'transcription', 'time_taken(ns)'])
  for r in results:
    csv_writer.writerow(r)

# print("Mean:\t{}".format(np.mean(bytes_sent)))
# print("Median:\t{}".format(np.median(bytes_sent)))
# print("Max:\t{}".format(np.max(bytes_sent)))
# print("Min:\t{}".format(np.min(bytes_sent)))

with open('./az_bytes.csv', 'w') as of:
  writer = csv.writer(of)
  writer.writerow(['file_size', 'bytes_sent'])
  for i in range(0, len(bytes_sent)):
    writer.writerow([file_size[i], bytes_sent[i]])