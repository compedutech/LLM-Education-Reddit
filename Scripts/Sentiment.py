import os
import sys
import csv
import string
from datetime import datetime
from transformers import pipeline
import logging.handlers
import pandas as pd
import re 
from transformers import pipeline
import requests
#import nltk
#from nltk.corpus import stopwords

    

input_file = r"/Final"
output_file= r"/All_Sentiment"
output_positive= r"/Positive"
output_negative= r"/Negative"
output_neutral= r"/Neutral"

# sets up logging to the console as well as a file
log = logging.getLogger("bot")
log.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
log_str_handler = logging.StreamHandler()
log_str_handler.setFormatter(log_formatter)
log.addHandler(log_str_handler)
if not os.path.exists("logs"):
	os.makedirs("logs")
log_file_handler = logging.handlers.RotatingFileHandler(os.path.join("logs", "bot.log"), maxBytes=1024*1024*16, backupCount=5)
log_file_handler.setFormatter(log_formatter)
log.addHandler(log_file_handler)
handle_stat = open(r"/stat_sentiment.csv", 'w', encoding='UTF-8', newline='')
writer_stat = csv.writer(handle_stat)
writer_stat.writerow(["File Name","Total Posts","Positive","Negative","Neutral"])

allPost,allPositive,allNegative,allNeutral=0,0,0,0

def preprocess_text(text):
    if pd.isna(text):
        return ""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'\b\w{1,2}\b', '', text)  # Remove short words (optional)
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
	#text = ' '.join([word for word in text.split() if word not in cachedStopWords])
    full_text = ' '.join(new_text)
    return full_text

def classify_comment(pipe,comment):
	try:
		if not comment.strip():  # If the comment is empty after preprocessing
			#log.info(f"returns not sure here")
			return 'not sure',0.0
		result = pipe(comment)
		return result[0].get("label"),result[0].get("score")
	except Exception as e:
		log.info(f"exception is here: {e}")
		return 'not sure',0.0
def does_reddit_link_exist(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
def process_file(pipe,input_file,output_file,output_positive,output_negative,output_neutral):
	log.info(f"Input: {input_file} ")
    
	input_handle = open(input_file, mode='r',encoding='UTF-8',newline='',errors='ignore')
	output_handle = open(output_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
	output_writer = csv.writer(output_handle)
	positive_handle = open(output_positive, mode='w',encoding='UTF-8',newline='',errors='ignore')
	positive_writer = csv.writer(positive_handle)
	negative_handle = open(output_negative, mode='w',encoding='UTF-8',newline='',errors='ignore')
	negative_writer = csv.writer(negative_handle)
	neutral_handle = open(output_neutral, mode='w',encoding='UTF-8',newline='',errors='ignore')
	neutral_writer = csv.writer(neutral_handle)

	total_post,positive,negative,neutral =0,0,0,0
	
	
	
	for line in csv.reader(input_handle):
		try:
			text = line[7]
			#url=line[6]
			
			if text== "":
				continue
			else:
				total_post +=1
				text=preprocess_text(text)
				sentiment,score = classify_comment(pipe,text)
				#print(text)
				#print(sentiment,score)
				#sentiment="positive"
				if sentiment == 'positive':
					positive+=1
					positive_writer.writerow(line)
				elif sentiment == 'negative':
					negative+=1
					negative_writer.writerow(line)
				elif sentiment == 'neutral':
					neutral+=1
					neutral_writer.writerow(line)
				
				line.extend([sentiment,score])
				output_writer.writerow(line)
					
			
		except Exception as e:
			log.warning(f"Error occuredfailed: {e}")
			writer_stat.writerow(f"Not Completed : {total_post:,} ")
			log.info(f"Not Completed : {total_post:,}")
			#output_handle.close()

	global allPost,allPositive,allNegative,allNeutral
	allPost+=total_post
	allPositive+=positive
	allNegative+=negative
	allNeutral+=neutral
	output_handle.close()
	positive_handle.close()
	negative_handle.close()
	neutral_handle.close()
	writer_stat.writerow([input_file,f"{total_post:,} ",f"{positive:,} ",f"{negative:,} ",f"{neutral:,} "])
	log.info(f"Complete : {total_post:,} : {input_file}")


if __name__ == "__main__":
	input_files = []
	if os.path.isdir(input_file):
		for file in os.listdir(input_file):
			if not os.path.isdir(file) and file.endswith(".csv"):
				input_name = os.path.splitext(os.path.splitext(os.path.basename(file))[0])[0]
				input_files.append((os.path.join(input_file, file),os.path.join(output_file, file),os.path.join(output_positive, file),os.path.join(output_negative, file),os.path.join(output_neutral, file)))
				
	else:
		input_files.append((input_file,os.path.join(output_file, input_file)))
	log.info(f"Processing {len(input_files)} files")
	
	model_path = "cardiffnlp/twitter-roberta-base-sentiment-latest"
	pipe = pipeline("sentiment-analysis", model=model_path,truncation=True,max_length=512)

	for file_in,file_out,file_positive,file_negative,file_neutral in input_files:
		process_file(pipe,file_in,file_out,file_positive,file_negative,file_neutral)
	
	writer_stat.writerow(["Total ",f"{allPost:,} ",f"{allPositive:,} ",f"{allNegative:,} ",f"{allNeutral:,} "])
	handle_stat.close()
	



