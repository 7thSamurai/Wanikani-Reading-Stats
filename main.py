#!/bin/python3

# The MIT License (MIT)
#
# Copyright (c) 2021 Zach Collins
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Quick script to find what percentage of the kanji in a text file you will know
# how to read on each level of Wanikani

import sys
import time
import requests
import json

headers = {}

# User information
user_name = ""
user_level = 0

###############################
# Wanikani API stuff          #
###############################

# Initialize Wanikani API stuff
def init_api(key):
	global headers
	global user_name
	global user_level

	headers = {"Authorization": "Bearer %s" % key}

	try:
		url = "https://api.wanikani.com/v2/user"
		response = requests.get(url, headers=headers).json()

		if "error" in response:
			print("Invalid API Key %s" % key)
			exit()

		user_name = response["data"]["username"]
		user_level = response["data"]["level"]
	except:
		print("Error connecting to Wanikani!")
		exit()

# Get a list of the subject pages
def get_pages():
	url = "https://api.wanikani.com/v2/subjects"
	pages = []
	done = 0.0

	while url != None:
		result = get_page(url)
		pages.append(result[0])
		url = result[1]
		done += result[2]

		print("\tRetrieved %i%%" % (done*100))

		# This is really not nessary, as we will only be making a couple of API calls
		# time.sleep(1)

	return pages

# Get a certain page
def get_page(url):
	response = requests.get(url, headers=headers)
	page = response.json()
	next_url = page["pages"]["next_url"]
	percent = page["pages"]["per_page"] / page["total_count"]

	return (page["data"], next_url, percent)

# Get a list of subjects
def get_subjects():
	pages = get_pages()
	subjects = []

	for page in pages:
		for entry in page:
			subjects.append(entry)

	return subjects

# Get a dictionary of kanji from wanikani
def get_kanji():
	subjects = get_subjects()
	kanji = {}

	for entry in subjects:
		if entry["object"] == "kanji":
			kanji[entry["data"]["slug"]] = entry["data"]["level"]

	return kanji

###############################
# Data Analysis stuff         #
###############################

# Checks if a certain Unicode character is a kanji
def is_kanji(char):
	return char >= '\u4e00' and char <= '\u9faf'

# Read the kanji from a text file
def read_kanji(path):
	kanji = []
	text = ""

	try:
		file = open(path, 'r')
		text = file.read()
		file.close()
	except:
		print("File \"%s\" does not exist!" % path)
		exit()

	for char in text:
		if is_kanji(char) and char not in kanji:
			kanji.append(char)

	return kanji

# Prints a row for the statistics table
def print_row(level, user_kanji, file_kanji):
	count = 0

	for kanji in file_kanji:
		if kanji in user_kanji and user_kanji[kanji] <= level:
			count += 1

	count = count / len(file_kanji) * 100
	row = "\t%i\t\t%i%%" % (level, count)

	if level == user_level:
		print("*" + row)
	else:
		print(row)

###############################
# Main                        #
###############################

def print_section(str):
	print(str)
	print("=" * len(str))

def main(path, key):
	init_api(key)

	print_section("Retrieving data from Wanikani...")
	user_kanji = get_kanji()

	print("\nReading data from file...")
	file_kanji = read_kanji(path)

	print_section("\nStatistics for file \"%s\" for user %s(Level %i)" % (path, user_name, user_level))
	print("\tLevel\t\tPercent")

	for level in range(1, 61):
		print_row(level, user_kanji, file_kanji)

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Usage: %s <Path to Text File> <API Key>" % sys.argv[0])
		exit()

	main(sys.argv[1], sys.argv[2])
