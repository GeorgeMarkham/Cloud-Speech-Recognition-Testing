from os import listdir
import os
import json
import azure.cognitiveservices.speech as speechsdk
import csv
from time import perf_counter_ns
import psutil
import numpy as np

# --------------------------------------------------
# 
# THIS CODE IS HEAVILY RELATED TO AND INFLUENCED BY THE DOCS https://docs.microsoft.com/en-gb/azure/cognitive-services/speech-service/quickstart-python
# 

# Also I would reccomend using ffmpeg to recode the timit data set as wav before running, for some reason the SDK doesn't consider 
# the wav files from the timit data set to be readable
# --------------------------------------------------

print("PID:\t", os.getpid())

d = "./timit/"
timit_labels = {}

speech_key, service_region = "YOUR_SPEECH_API_KEY", "DATACENTER_REGION" # region could be uksouth for example
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

results = []

bytes_sent = []
file_sizes = []


iostat = psutil.net_io_counters(pernic=False)
start_net_bytes = iostat[0]
with open('./timit.json', 'r') as t:
  timit_labels = json.load(t)
  for f in listdir(d):
    if f.endswith(".wav"):
      audio_file = d+f
      input_text = timit_labels[f.split('_')[1][:-4]]

      audio_config = speechsdk.audio.AudioConfig(filename=audio_file)

      speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

      # Test performance, size sent and latency
      start = perf_counter_ns()
      result = speech_recognizer.recognize_once()
      end = perf_counter_ns()

      bts = psutil.net_io_counters(pernic=False)[0]

      bytes_sent.append(bts - start_net_bytes) #upload only

      file_size = os.path.getsize(audio_file)

      file_sizes.append(file_size)

      print(file_size, bytes_sent[-1])
      start_net_bytes = bts

      # Check the result
      if result.reason == speechsdk.ResultReason.RecognizedSpeech:
          print("Recognized: {}".format(result.text))
          res_obj = [str(audio_file), input_text, result.text, end-start]
          results.append(res_obj)
      elif result.reason == speechsdk.ResultReason.NoMatch:
          print("No speech could be recognized: {}".format(result.no_match_details))
      elif result.reason == speechsdk.ResultReason.Canceled:
          cancellation_details = result.cancellation_details
          print("Speech Recognition canceled: {}".format(cancellation_details.reason))
          if cancellation_details.reason == speechsdk.CancellationReason.Error:
              print("Error details: {}".format(cancellation_details.error_details))
              iostat = psutil.net_io_counters(pernic=False)



# print("Mean:\t{}".format(np.mean(bytes_sent)))
# print("Median:\t{}".format(np.median(bytes_sent)))
# print("Max:\t{}".format(np.max(bytes_sent)))
# print("Min:\t{}".format(np.min(bytes_sent)))

with open('./az_bytes.csv', 'w') as of:
  writer = csv.writer(of)
  writer.writerow(['file_size', 'bytes_sent'])
  for i in range(0, len(bytes_sent)):
    writer.writerow([file_size[i], bytes_sent[i]])

with open('test_az.csv', 'w') as csv_out:
  csv_writer = csv.writer(csv_out)
  csv_writer.writerow(['file_name', 'original_text', 'transcription', 'time_taken(ns)'])
  for r in results:
    csv_writer.writerow(r)