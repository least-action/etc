#!/usr/bin/python3

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta


def refine_string(full_str):
	refined_str = full_str
	refined_str = re.sub('[,\."\'\-_~!…’‘]+', ' ', refined_str)
	return refined_str


def extract_keyword_from_string_list(str_list):
	keyword_count = dict()
	for each_str in str_list:
		refined_str = refine_string(each_str)
		keywords = refined_str.split()
		for each in keywords:
			try:
				keyword_count[each] += 1
			except KeyError:
				keyword_count[each] = 1

	return keyword_count


def get_naver_news_list_from_page(base_url, date, page, deduplicate=True):
	url = base_url + '&date=' + date + '&page=' + str(page)
	html = urlopen(url)
	soup = BeautifulSoup(html, "html.parser")
	articles = soup.find(id='main_content').find('div', {'class': 'list_body'}).findAll('li')

	title_list = []
	if (deduplicate):
		news = dict()
		for each in articles:
			title = each.findAll('a')[-1].text.strip() # some article doesn't have image
			# article_body = each.find('dd').find('span', {'class': 'lede'}).text
			publisher = each.find('dd').find('span', {'class': 'writing'}).text

			# key = title + article_body + publisher # EPA uploads same articles with differnce front of body
			key = title + publisher
			news[key] = title
		title_list += [v for k, v in news.items()]

	else:
		for each in articles:
			title = each.findAll('a')[-1].text.strip() # some article doesn't have image
			title_list.append(title)

	return title_list


def main():
	# set variable
	base_url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=001'
	KST = datetime.utcnow() + timedelta(hours=9)
	date = KST.strftime('%Y%m%d') # form: 20191107
	num_of_pages = 30
	max_n_of_top = 10
	common_word = {'첫', '등', '벌써', '오늘'}

	# get title from naver page
	news_title_list = []
	for page in range(num_of_pages):
		news_title_list += get_naver_news_list_from_page(base_url, date, page+1, deduplicate=True)

	# counting keywords
	keyword_table = extract_keyword_from_string_list(news_title_list)
	sorted_keywords_table = sorted(keyword_table.items(), key=lambda kv: kv[1], reverse=True)

	# print result
	idx = -1
	count = 0
	while (count < max_n_of_top):
		try:
			idx += 1
			if (sorted_keywords_table[idx][0] in common_word):
				continue
			else:
				print('{:>5} : {}'.format(sorted_keywords_table[idx][1], sorted_keywords_table[idx][0]))
				count += 1
		except IndexError:
			print('no more keyword')
			break

	
if __name__ == '__main__':
	main()
