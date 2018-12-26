import json
import urllib.parse
import urllib.request
import os

def read_serpwow_key():

	serpwow_api_key = None

	try:
		if os.path.isfile('search.key'):
#			print("found 1")
			with open('search.key', 'r') as f:
				serpwow_api_key = f.readline().strip()
		else:
#			print("found 2")
			with open(os.path.join('..', 'search.key'), 'r') as f:
				serpwow_api_key = f.readline().strip()		

	except:
		raise IOError('search.key file not found')

	return serpwow_api_key
	

def run_query(search_terms, size=10):

	serpwow_api_key = read_serpwow_key()
	print(serpwow_api_key)
	if not serpwow_api_key:
		raise KeyError('Serpwow Key not found')

	root_url = 'https://api.serpwow.com/live/search'

	querystring = urllib.parse.quote(search_terms)
	search_url = ('{root_url}?api_key={key}&q={query}&num={size}').format(root_url=root_url, key=serpwow_api_key, query=querystring, size=size)

	results = []

	try:
		response = urllib.request.urlopen(search_url).read().decode('utf-8')
		json_response = json.loads(response)

		for post in json_response['organic_results']:
			if 'snippet' in post:
				results.append({'title' : post['title'], 'link': post['link'], 'summary': post["snippet"][:200] })
			else :
				results.append({'title' : post['title'], 'link': post['link']})

	except:
		print("Error while querying the Serpwow API")

	return results
	
def main():	
	search_terms = input("Enter Query : ")
	results = run_query(search_terms)
	for post in results:
		print("title : {0}  - link : {1}".format(post['title'], post['link']))
		if 'summary' in post:
			print(post['summary'])
		print('\n \n')





if __name__ == '__main__':
	main()
	


