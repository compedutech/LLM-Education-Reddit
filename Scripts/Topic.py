import re
import numpy as np
import pandas as  pd
import csv
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import LdaModel,CoherenceModel# spaCy for preprocessing
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
import nltk
#nltk.download('stopwords')
#nltk.download('punkt_tab')
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import time
from collections import Counter
from smart_open import open  # for transparently opening remote files
import os
import sys
import csv
import string
import json
stop_words = stopwords.words('english')
stop_words.extend(['chatgpt', 'claude', 'gemini','llm','large language model','student','students','professor','professors','teacher','teachers','course','courses','university','universities','school','schools','college','colleges','like','use','used','using','one','get','also','would','could','may'])
#print(stop_words)
stemmer = SnowballStemmer("english")
input_file=r"/Negative"
handle_theme = open(r"/themes_subreddit_negative_f.csv", 'w', encoding='UTF-8', newline='')
writer_theme = csv.writer(handle_theme)

def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    text=text.lower()
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            if re.search('[//]', token):
                  continue
            #re.sub('http[s]?://\S+', '', token)
            filtered_tokens.append(token)
    #stems = [stemmer.stem(t) for t in filtered_tokens if t not in stop_words]
    stems = [t for t in filtered_tokens if t not in stop_words]
    return stems
#tokenize words
def sent_to_words(sentences):
  for sentence in sentences:
    yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))
    #deacc=True removes punctuation

def preprocess(data):
   tokenized_text = tokenize_and_stem(data)
   return tokenized_text
def preprocess_bert(data):
    if data is None:
        return " "
    tokenized_text = tokenize_and_stem(data)
    return " ".join(tokenized_text)


def getFiles():
	input_files = []
	if os.path.isdir(input_file):
		for file in os.listdir(input_file):
			if not os.path.isdir(file) and file.endswith(".csv"):
				input_name = os.path.splitext(os.path.splitext(os.path.basename(file))[0])[0]
				input_files.append((os.path.join(input_file, file)))
	else:
		input_files.append((input_file))
	return input_files
representation_model = KeyBERTInspired()
topic_model= BERTopic(representation_model=representation_model,language="english")
topic,probs= topic_model.fit_transform([preprocess_bert(line[7]) for files in getFiles() for line in csv.reader(open(files, mode='r',encoding='UTF-8',newline='',errors='ignore'))])

#print(topic_model.get_topic_info())
for row in topic_model.get_topic_info().itertuples():
        #print(f"Index: {row.Index}, Topic: {row.Topic}, Count: {row.Count}, Name: {row.Name}, Representation: {row.Representation}, Representative_Docs: {row.Representative_Docs}")
        print(f"Index: {row.Index}, Topic: {row.Topic}, Count: {row.Count}, Name: {row.Name}, Representation: {row.Representation}")
        writer_theme.writerow([row.Topic,row.Count, row.Name, row.Representation,row.Representative_Docs])
        print("*************")


handle_theme.close()

def process_file(input_file):
	 
	input_handle = open(input_file, mode='r',encoding='UTF-8',newline='',errors='ignore')

	file_size = os.stat(input_file).st_size
	
	for line in csv.reader(input_handle):
		try:
			text = line[7]
			if text== "":
				continue
		except Exception as e:
			print(f"Error occuredfailed: {e}")
			input_handle.close()
			
	input_handle.close()
	
def handle_files():
	input_files = []
	if os.path.isdir(input_file):
		for file in os.listdir(input_file):
			if not os.path.isdir(file) and file.endswith(".csv"):
				input_name = os.path.splitext(os.path.splitext(os.path.basename(file))[0])[0]
				input_files.append((os.path.join(input_file, file)))
	else:
		input_files.append((input_file))
	for file_in in input_files:
		process_file(file_in)
                
def getFiles():
	input_files = []
	if os.path.isdir(input_file):
		for file in os.listdir(input_file):
			if not os.path.isdir(file) and file.endswith(".csv"):
				input_name = os.path.splitext(os.path.splitext(os.path.basename(file))[0])[0]
				input_files.append((os.path.join(input_file, file)))
	else:
		input_files.append((input_file))
	return input_files