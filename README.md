The Posts Folder containins all the Reddit posts. 
  RawPosts are the initial data extracted from the Pushshift dtaset. 
  Subreddit is the dataset that was filtered from the RawPost based on the subreddit information. 
  Final Dataset is Subreddit minus the posts that have been deleted. The deleted posts were identified via the Reddit API
Results folder contain the results of the analysis
  Sentiment is the categorization of the Final Dataset based on the sentiment results
  Themes is the result of the topic modeling via BertTopic
  Statistics contains the information related to the number of posts
Scripts contain all the Python scrips used to extract and analyze the data
  ExtractRawPost was used to filter out the initial data from the Pushshift Dataset
  SubredditPosts: filter our the posts based on their subreddit information
  RedditAPI_filter: Identify post that were removed or deleted via the reddit API
  Sentiment: Sentiment analysis using RobertaTweet Model from HuggingFace
  Topic: Topic modeling using BertTopic
