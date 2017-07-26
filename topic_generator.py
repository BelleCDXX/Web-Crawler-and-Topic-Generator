import crawl
import re
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.util import ngrams
from collections import Counter
from heapq import nlargest



# ************ functions for parsing the data ***************


def creat_soup():
	# read the url and crawl the url, using BeautifulSoup as the parser
	url = input('Enter the url: ')
	print('\ncrwaling...')
	page = crawl.get_page(url)
	soup = BeautifulSoup(page, 'html.parser')

	return soup



def settle_features():
	'''
		Assign weight to each tag represent they have different impact to the topic.
		Higher weight means more important.

		Also assign weight to ngrams,
		larger ngram has higher weight since its occurance is lower than smaller ngrams
	'''
	weight = {'p': 2, 'title':6, 'h':3, 'div': 1.5, 'span': 1.5, 'bigram':2.5, 'trigram':3.6}

	'''
		Extract only the key content we are interested.
		I choosed the content in tags: 'title', 'h', 'p', 'div' and 'span' to represent the page. 

		For 'title', 'h' and 'p', extract all the content under the tag.

		For 'div', 'span', extract only direct content under the tag,
		so that they won't accidently get the content of their child tag (e.g. script, img...)

		These can be modifies as needed.
	'''

	tags_all = ['title', 'h', 'p']
	tags_direct = ['div', 'span']

	return weight, tags_all, tags_direct



def get_key_content(soup, tags_all, tags_direct):
	'''
		key_content:
		{tag: <tag> [<inner_ tags>] content [</inner_ tags>] </tag>}
	'''

	key_content = dict()

	for tag in (tags_all + tags_direct):
		if tag != 'h':
			key_content[tag] = soup.find_all(tag)
		else:
			key_content['h'] = soup.find_all('h1') + \
							   soup.find_all('h2') + \
							   soup.find_all('h3') + \
							   soup.find_all('h4') + \
							   soup.find_all('h5') + \
							   soup.find_all('h6')
	return key_content



def merge_content(key_content, weight, tags_all, tags_direct):

	'''
		For 'title', 'h' and 'p', extract all the content under the tag.

		For 'div', 'span', extract only direct content under the tag,
		so that they won't accidently get the content of their child tag (e.g. script, img...)

		Assign the weight to different content based on their tag.
	'''
	merge_key_content = dict()

	for tag in tags_all:
	    for each in key_content[tag]:
	        for sentence in each.strings:
	            cur = sentence.strip().lower()
	            if cur:
	                merge_key_content[cur] = merge_key_content.get(cur, 0) + weight[tag]

	for tag in tags_direct:
	    for each in key_content[tag]:
	        cur = each.string
	        if cur and cur.strip():
	            cur = cur.strip().lower()
	            merge_key_content[cur] = merge_key_content.get(cur, 0) + weight[tag]
	return merge_key_content



# ************ functions for topic modeling ***************

'''
	Check if the word is valid
	Here valid defined as a word that contain alphabet and is not a stop word
'''
def valid(word, stop):
    return re.search('[a-z]', word) != None and word not in stop



def get_topics(merge_key_content, weight, stop, valid):

	'''
		choose include trigram or not.
		choose the number of result topics.
	'''

	while True:
		include_trigram = input('\nDo you want to include trigram or not? [y/n]: ')
		if include_trigram in {'y', 'n', 'Y', 'N'}:
			include_trigram = True if include_trigram in {'y', 'Y'} else False
			break
		else:
			print('Please answer y/n.')

	while True:
		num_topics = input('\nHow many topics do you want?(Recomend more than 10 cause the current version may include some garbage in the result) : ')
		try:
			num_topics = int(num_topics)
			break
		except Exception as e:
			print('Please give an integer.')

	'''
		Generate the ngrams and assign the weight to each ngram.
		Get the top topics based on the weight. The more weight the higher rank.
	'''

	unigrams = {}
	for sentence in merge_key_content:
	    for each in word_tokenize(sentence):
	        if valid(each, stop):
	            unigrams[each] = unigrams.get(each,0) + merge_key_content[sentence]

	bigrams = {}
	for sentence in merge_key_content:
	    token = word_tokenize(sentence)
	    cur_bigrams = ngrams(token,2)
	    for each in cur_bigrams:
	    	if valid(each[0], stop) and valid(each[1], stop):
	        	bigrams[each] = bigrams.get(each,0) + merge_key_content[sentence] * weight['bigram']

	
	total_count = Counter()
	total_count.update(unigrams)
	total_count.update(bigrams)
	
	if include_trigram:
		trigrams = {}
		for sentence in merge_key_content:
		    token = word_tokenize(sentence)
		    cur_trigrams = ngrams(token,3)
		    for each in cur_trigrams:
		    	if valid(each[0], stop) and valid(each[1],stop) and valid(each[2], stop):
		        	trigrams[each] = trigrams.get(each,0) + merge_key_content[sentence] * weight['trigram']

		total_count.update(trigrams)
		
	topics = nlargest(num_topics, total_count, key = lambda k:total_count[k])
	topics = [each if type(each) == str else ' '.join(each) for each in topics]

	return topics


# ************ main ***************

if __name__ == "__main__":



	soup = creat_soup()

	weight, tags_all, tags_direct = settle_features()
	key_content = get_key_content(soup, tags_all, tags_direct)
	merge_key_content = merge_content(key_content, weight, tags_all, tags_direct)
	#print(len(merge_key_content))


	stop = set(stopwords.words("english"))
	topics = get_topics(merge_key_content, weight, stop, valid)

	print('\nTopics:\n')
	for each in topics:
		print(each)


