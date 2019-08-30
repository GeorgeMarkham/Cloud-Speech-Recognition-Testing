#!/usr/bin/env python
# coding: utf-8

# In[67]:


import time
import boto3
import os

# Starts the transcription jobs based on what is in the S3 Bucket

transcribe = boto3.client('transcribe')
job_uri_base = "s3://YOUR_S3_BUCKET-URL/"

job_list = []

all_files = os.listdir('./timit')
# print(len(all_files))
for i in list(range(0, 10)):
    s = (i*92)
    e = (i*92)+92
    job_list.append(all_files[s:e])
#     print(len(job_list))
    
for job_section in job_list:
    for file in job_section:
        job_name = "thesis_transcription_" + file[:-4]
        job_uri = job_uri_base + file
        try:
            transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': job_uri},
                MediaFormat='wav',
                LanguageCode='en-GB'
            )
        except:
            time.sleep(10)
        time.sleep(3)
    time.sleep(30)


# In[2]:


import time
import boto3
import os
transcribe = boto3.client('transcribe')
job_uri_base = "s3://thesis-asr-testing-bucket/"

jobs = []
jobList = transcribe.list_transcription_jobs(MaxResults=100)
nextToken = jobList['NextToken']
jobs.append(jobList["TranscriptionJobSummaries"])
while len(nextToken) > 0 and nextToken != None:
    print(len(jobs))
    jobList = transcribe.list_transcription_jobs(NextToken=nextToken, MaxResults=100)
    jobs.append(jobList["TranscriptionJobSummaries"])
    try:
        nextToken = jobList['NextToken']
    except:
        break


# In[3]:


import requests
import json
from csv import writer


# Reads the transcriptions and saves them to a file for further processing

timit_labels = {}
with open('./timit.json', 'r') as t:
    timit_labels = json.load(t)
    
    with open('./aws_test.csv', 'w') as of:
        ofWriter = writer(of)
        allJobs = []
        for someJobs in jobs:
            for job in someJobs:
                transcription_job_name = job['TranscriptionJobName']
                job_name_split = transcription_job_name.split('_')
                
                audio_file_name = job_name_split[2] + '_' + job_name_split[3]
                audio_file_name = './timit/' + audio_file_name + '.wav'
                print(audio_file_name)
                
                timit_name = job_name_split[3]

                original = timit_labels[timit_name]
                transcription_job_obj = transcribe.get_transcription_job(TranscriptionJobName=job['TranscriptionJobName'])
                transcript_uri = transcription_job_obj['TranscriptionJob']['Transcript']['TranscriptFileUri']

    #             CreationTime, CompletionTime
                created = transcription_job_obj['TranscriptionJob']['CreationTime']
                completed = transcription_job_obj['TranscriptionJob']['CompletionTime']
                time = completed - created
                time = time.seconds * 1e+9
                print(time)
                res = requests.get(transcript_uri)
                transcript = json.loads(res.text)['results']['transcripts'][0]['transcript']


                res_obj = [audio_file_name, original, transcript, time]
        
                ofWriter.writerow(res_obj)


# In[ ]:




