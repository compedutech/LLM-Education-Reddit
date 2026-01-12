import os
import sys
import csv
import string
from datetime import datetime
from transformers import pipeline
import logging.handlers
import pandas as pd
import re 
#import nltk
#from nltk.corpus import stopwords

    

input_file = r"/RawPost"
output_file= r"/Subreddit"

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
handle_stat = open(r"/Subreddit/stat_subreddit.csv", 'w', encoding='UTF-8', newline='')
writer_stat = csv.writer(handle_stat)
handle_sub = open(r"/subreddit.csv", 'w', encoding='UTF-8', newline='')
writer_sub = csv.writer(handle_sub)
subList={}

allPost=0
sublist=['microsaas','intltousa','careeradvice','aiwars','itcareerquestions','chatgpt','teachers','professors','artificialinteligence','chatgptpromptgenius','chatgptautomation','chanceme','learnmachinelearning','csmajors','sideproject','advice','openai','localllama','sgexams','machinelearning','entrepreneur','singularity','edtech','promptengineering','stealthgpt','australianteachers','aitah','nextgenaitool','studentsph','artificial','uniuk','ibo','teaching','askacademia','chatgpt_occult','jeeneetards','phd','gpt3','trueoffmychest','findapath','teachingresources','learnmath','geminiai','gradschool','bard','askprofessors','university','askteachers','askprogramming','indians_studyabroad','getstudying','teenagers','academia','vent','school','aikilledmystartup','indian_academia','student','chatgptjailbreak','collegerant','webdev','ai_news_by_ai','marginal','students','surveycircle','languagelearning','gradadmissions','wgu','canadianteachers','studying','python','medicalschool','chatgptcoding','study','writingwithai','llmdevs','comptia','mba','leetcode','changemyview','esl_teachers','jee','originalityhub','homeschool','mlquestions','omscs','apstudents','googlegeminiai','ntu','onlineeslteaching','artificialsentience','futuretechfinds','gptappsengine','igcse','step1','languagetechnology','universityofauckland','catpreparation','ucsd','psychologystudents','mcat','cscareerquestionseu','cbse','chineselanguage','lawschool','hdfidelity','aipromptprogramming','odysseybookclub','ai_agents','anki','bioinformatics','tutorshelpingtutors','machinelearningnews','ontariograde12s','ollama','premed','cervantes_ai','self','adjuncts','historyteachers','venting','getdisciplined','using_ai_in_education','codingbootcamp','englishteachers','newerestspace','artificialntelligence','futurology','alevel','language_exchange','usyd','askphysics','preply','snhu','datascience','uiuc','uopeople','toefladvice','uwaterloo','gamedev','physics','chatgpt_prompts','agi','softwareengineering','gre','collegeadmissionsph','monash','dreamingspanish','electricalengineering','programmingbuddies','developerspak','perplexity_ai','adviceph','suss','germany','productivityapps','pennstateuniversity','c_programming','business_ideas','technepal','scienceteachers','indiacareers','sat','umd','chatgptgonewild','summerprogramresults','albuquerque','notebooklm','llm','deepthoughts','aiautomations','aipromptsforeducators','offmychestindia']

def process_file(input_file,output_file):
	log.info(f"Input: {input_file} ")
    
	input_handle = open(input_file, mode='r',encoding='UTF-8',newline='',errors='ignore')
	output_handle = open(output_file, mode='w',encoding='UTF-8',newline='',errors='ignore')
	output_writer = csv.writer(output_handle)

	total_post =0
	
	
	for line in csv.reader(input_handle):
		try:
			text = line[5]
			
			if text== "":
				continue
			else:
				
				text=text.strip().lower()
				if text=="suicidewatch":
					print(line[7])
				
				if text in sublist:
					total_post +=1
					subList[text]=subList.get(text,0)+1
					#print("Found it")
					output_writer.writerow(line)
			
		except Exception as e:
			log.warning(f"Error occuredfailed: {e}")
			writer_stat.writerow(f"Not Completed : {total_post:,} ")
			log.info(f"Not Completed : {total_post:,}")
			output_handle.close()

	global allPost
	allPost+=total_post
	output_handle.close()
	writer_stat.writerow([input_file,f"{total_post:,} "])
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
	for file_in,file_out in input_files:
		process_file(file_in,file_out)
	sorted_subs = dict(sorted(subList.items(), key=lambda item: item[1], reverse=True))
	for key,value in sorted_subs.items():
		writer_sub.writerow([key,value])
	writer_stat.writerow(["Total ",f"{allPost:,} "])
	handle_stat.close()
	handle_sub.close()
	



