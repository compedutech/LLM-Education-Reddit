import os
import sys
import csv
import string
from datetime import datetime
from transformers import pipeline
import logging.handlers
import pandas as pd
import re 
import praw
import time
from prawcore.exceptions import TooManyRequests
#from prawcore.exceptions import Forbidden


    

input_file = r"/SubredditPosts"
output_file= r"/SubredditAPI"
#You need to get the secret, personal and agent keys from the official Reddit API documentation
secret= ""
personal= ""
agent= ""
reddit = praw.Reddit(
    client_id=personal,
    client_secret=secret,
    user_agent=agent,
	ratelimit_seconds=605
)

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
handle_stat = open(r"/stat_api.csv", 'w', encoding='UTF-8', newline='')
writer_stat = csv.writer(handle_stat)
writer_stat.writerow(["File Name","Total Posts","User Deleted Posts","Removed Posts","Active Posts","Unsure Posts"])
max_retries = 5
retry_delay = 10  # seconds
allPost,deleted,removed,active,unsure=0,0,0,0,0
def check_reddit_post_status(submission_id):
    """Checks if a Reddit post is deleted or removed."""
    global max_retries, retry_delay
    score=0
    for attempt in range(max_retries):
      try:
        submission = reddit.submission(id=submission_id)
        # Ensure the object is loaded by accessing an attribute
        _ = submission.title
        score = submission.score  # Accessing score to trigger a fetch
        if submission.author is None:
            return "User_deleted",score
        elif not submission.is_robot_indexable:
            return "removed",score
        else:
            return "active",score
        break
      except TooManyRequests as e:
        print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
        if retry_delay < 321:
           retry_delay *= 2  # Exponential backoff
        else:
           retry_delay = 10

      except Exception as e:
        print(f"Error checking post status: {e}")
        return "error",score
    return "retry_exceeded",score

def process_file(input_file,output_file):
	log.info(f"Input: {input_file} ")
    
	input_handle = open(input_file, mode='r',encoding='UTF-8',newline='',errors='ignore')
	output_handle = open(output_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
	output_writer = csv.writer(output_handle)

	total_post =0
	t_deleted,t_removed,t_active,t_unsure=0,0,0,0
	
	
	for line in csv.reader(input_handle):
		try:
			id = line[0]
			
			if id== "":
				continue
			else:
				total_post +=1
				status,score = check_reddit_post_status(id)
				if(status=="User_deleted"):
					t_deleted+=1
				elif(status=="removed"):
					t_removed+=1
				elif(status=="active"):
					t_active+=1
				else:
					t_unsure+=1
				line.append(status)
				line.append(score)
				output_writer.writerow(line)
			
		except Exception as e:
			log.warning(f"Error occuredfailed: {e}")
			#writer_stat.writerow([input_file,"Not Completed",f"{total_post:,}"])
			log.info(f"{input_file} Not Completed : {total_post:,}")
			#output_handle.close()

	global allPost,deleted,removed,active,unsure
	allPost+=total_post
	deleted+=t_deleted
	removed+=t_removed
	active+=t_active
	unsure+=t_unsure
	output_handle.close()
	writer_stat.writerow([input_file,f"{total_post:,} ",f"{t_deleted:,} ",f"{t_removed:,} ",f"{t_active:,} ",f"{t_unsure:,} "])
	log.info(f"Complete : {total_post:,} : {input_file}")


if __name__ == "__main__":
	input_files = []
	if os.path.isdir(input_file):
		for file in os.listdir(input_file):
			if not os.path.isdir(file) and file.endswith(".csv"):
				input_name = os.path.splitext(os.path.splitext(os.path.basename(file))[0])[0]
				input_files.append((os.path.join(input_file, file),os.path.join(output_file, file)))
				
	else:
		input_files.append((input_file,os.path.join(output_file, input_file)))
	log.info(f"Processing {len(input_files)} files")
	
	#pipe = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",num_labels=2)
	for file_in,file_out in input_files:
		process_file(file_in,file_out)
	
	writer_stat.writerow(["Total ",f"{allPost:,} ",f"{deleted:,} ",f"{removed:,} ",f"{active:,} ",f"{unsure:,} "])
	handle_stat.close()
	



