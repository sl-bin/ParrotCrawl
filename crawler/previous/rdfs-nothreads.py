#!/usr/bin/python3
# DFS Webcrawler Implementation ------------------------------------------------
#
#	To execute, use the following argument format:
#		dfs.py [ URL of starting page ] [ depth constraint ] [ user query term ]
#		Example:	dfs.py http://cultofthepartyparrot.com 2 basket
#-------------------------------------------------------------------------------

import sys
import urllib.request
from bs4 import BeautifulSoup
import json
import copy

import re
import string


def relevant_text(tag):
	return	tag.name == "title" or\
			tag.name == "p" or\
			tag.name == "div" or\
			tag.name == "span" or\
			tag.name == "h1" or\
			tag.name == "h2" or\
			tag.name == "h3" or\
			tag.name == "h4" or\
			tag.name == "h5" or\
			tag.name == "h6"

def querySearch(page, query):
	betterText = ""
	for each in page.find_all(relevant_text):
		betterText += each.get_text()

	# Can be deleted after testing/verification of return text.
	#newText = betterText.replace("\n", " ")
	#print(newText)

	result = betterText.find(query)
	if result >= 0: hasQuery = 1
	else: hasQuery = 0

	return hasQuery

#----------------------------------------------------------------------

# VALIDATE ARGS
if len(sys.argv) < 3:
	print("\tUsage: rdfs.py [starting URL] [depth] [query (optional)]")
	sys.exit(2)

URLParam = str(sys.argv[1])
depthParam = int(sys.argv[2])
if len(sys.argv) < 4: queryParam = None
else: queryParam = str(sys.argv[3])

# Set URL Opener - assign valid user-agent to prevent bot detection
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

# Assign starting values
nextID = 1
currentID = 0
currentURL = URLParam
currentWidth = 0
currentDepth = 0
targetDepth = depthParam
isDead = 0
hasQuery = 0
maxWidth = 0

# Set up dataset:
data = {}

data['input'] = {}
data['input']['url'] = currentURL
data['input']['n'] = targetDepth
data['input']['type'] = "rdfs"
data['input']['search'] = queryParam

data['dimensions'] = {}
data['dimensions']['height'] = 1
data['dimensions']['width'] = 1

data['results'] = []

# Place Starting page entry into dataset:
parentnode = {}
parentnode['id'] = currentID
parentnode['depth'] = currentDepth
parentnode['title'] = ""
parentnode['url'] = currentURL
parentnode['dead'] = 0
parentnode['found'] = 0
parentnode['links'] = 0
parentnode['children'] = []

data['results'].append(copy.deepcopy(parentnode))

# Begin Crawl

while currentDepth < targetDepth:

	# 1. LOAD PARENT PAGE

	# HTML ERROR HANDLING --- TRY / EXCEPT BLOCK --------------------------
	try:
		currentHTML = opener.open(currentURL)
	except urllib.error.HTTPError as err:
		data['results'][currentID]['title'] = "Parent site invalid."
		data['results'][currentID]['dead'] = 1
		sys.exit(2)

	except urllib.error.URLError:
		data['results'][currentID]['title'] = "Parent site invalid."
		data['results'][currentID]['dead'] = 1
		sys.exit(2)

	else:
		currentURL = currentHTML.geturl()	# Update our URL in case a redirect was followed.
		currentRes = currentHTML.info()
		currentType = currentRes.get_content_type() # We only want to open text/html files.

		# Page was successfully opened --> convert to bs4 object.
		currentPage = BeautifulSoup(currentHTML.read(), "html5lib")

		# 2. COLLECT PAGE DATA:

		# Search for Query Term
		if queryParam: hasQuery = querySearch(currentPage, queryParam)

		# Scrape links from page:
		links = currentPage.find_all("a", href=True)

		data['results'][currentID]['title'] = currentPage.title.getText()
		data['results'][currentID]['url'] = currentURL	# <-- Update URL
		data['results'][currentID]['found'] = hasQuery
		data['results'][currentID]['links'] = len(links)

		# 3. PARSE SCRAPED/CHILD LINKS
		linkPool = []
		childrenNodes = []

		for item in links:

			isDead = 0
			hasQuery = 0

			# Make sure Child URL is properly formatted.
			if item['href'] == '' or item['href'][0] == "#":
				data['results'][currentID]['links'] -= 1
				continue

		#	if item['href'][0] == "/":		# Append href value to parent URL, if necessary
		#		childURL = str(urllib.parse.urljoin(currentURL, item['href']))

			else:
			#	childURL = item['href']
				childURL = str(urllib.parse.urljoin(currentURL, item['href']))

			# OPEN CHILD URL

			childNode = {}
			childTitle = ""

			# HTML ERROR HANDLING --- TRY / EXCEPT BLOCK --------------------------
			try:
				childHTML = opener.open(childURL)
			except urllib.error.HTTPError as err:
				isDead = 1
				childTitle = str(err)
				pass

			except urllib.error.URLError:
				isDead = 1
				childTitle = "Incorrect Domain/Server Down"
				pass

			# If Value Error in URL is received, try one final concatenation:
			except ValueError as err:
				try:
					childURL = str(urllib.parse.urljoin(currentURL, childURL))
					childHTML = opener.open(childURL)
				except ValueError as finalErr:
					isDead = 1
					childTitle = "Value Error: Improper/Unknown URL Format."
					pass
				except urllib.error.HTTPError as finalErr:
					# --> Handle child HTTP error page data here.
					isDead = 1
					childTitle = str(err)
					pass
				except urllib.error.URLError:
					# --> Handle URL error page data here.
					isDead = 1
					childTitle = "Incorrect Domain/Server Down"
					pass
				else:
					# If our final attempt to correct the URL succeeded, import the page.
					childRes = childHTML.info()
					childType = childRes.get_content_type()
					childPage = BeautifulSoup(childHTML.read(), "html5lib")
					if childPage.title is None: childTitle = "No Title"
					else: childTitle = childPage.title.getText()
			else:
				childRes = childHTML.info()
				childType = childRes.get_content_type()

				childPage = BeautifulSoup(childHTML.read(), "html5lib")
				if childPage.title is None: childTitle = "No Title"
				else: childTitle = childPage.title.getText()
				if queryParam: hasQuery = querySearch(childPage, queryParam)
			# END OF HTML ERROR HANDLING ------------------------------------------

			# COLLECT CHILD PAGE DATA:
			childNode['id'] = nextID; nextID += 1
			childNode['depth'] = currentDepth + 1
			childNode['title'] = childTitle


			childNode['url'] = childURL
			childNode['dead'] = isDead
			childNode['found'] = hasQuery
			childNode['links'] = 0
			childNode['children'] = []

			# APPEND CHILD ID TO PARENT DATASET
			data['results'][currentID]['children'].append(copy.deepcopy(childNode['id']))

			# APPEND CHILD TO CHILDREN DATASET:
			childrenNodes.append(copy.deepcopy(childNode))

			# IF CHILD IS LIVE AND VALID HTML, ADD TO LINK POOL:
			if childNode['dead'] == 0 and childType == "text/html": linkPool.append(copy.deepcopy(childNode))

		# 4. SELECT NEW LINK FROM LIST

		if len(linkPool) < 1:	# <-- There are no links to select. Assign data and break.
			print("0 Available links, Parrot flying home!")

			for each in childrenNodes:
				data['results'].append(copy.deepcopy(each))
				break

		else:
			nextParent = linkPool[1] # <-- Should be random assignment

		# 5. RECORD ALL TIER DATA TO FILE AS JSON


		# APPEND CHILD NODES TO DATASET
	#	currentWidth = 1	# <-- Account for parent node already in dataset.
		for each in childrenNodes:
			data['results'].append(copy.deepcopy(each))
			currentWidth += 1

	#	if currentWidth > maxWidth: maxWidth = currentWidth

		# Swap first child ID/position with new parent.
		data['results'][(nextParent['id'])]['id'], data['results'][(childrenNodes[0]['id'])]['id'] = data['results'][(childrenNodes[0]['id'])]['id'], data['results'][(nextParent['id'])]['id']
		data['results'][(nextParent['id'])], data['results'][(childrenNodes[0]['id'])] = data['results'][(childrenNodes[0]['id'])], data['results'][(nextParent['id'])]

		# 6. SET UP FOR NEXT ITERATION
		currentURL = data['results'][(childrenNodes[0]['id'])]['url']
		currentID = childrenNodes[0]['id']

		isDead = 0
		hasQuery = 0
		currentDepth += 1

for each in data['results']:
	if each['links'] > 0:
		data['dimensions']['width'] += each['links'] - 1

data['dimensions']['height'] = currentDepth + 1

print(json.dumps(data))
