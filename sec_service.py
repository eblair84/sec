from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

sec_full_index = 'https://sec.gov/Archives/edgar/full-index/'
sec_data = 'https://sec.gov/Archives/'


@app.route('/filings/<co>/<yr>/<qtr>')
def get_filings(co,yr,qtr, filing):
#	took this out of play for now.
	'''company = request.args.get('co')
	year = request.args.get('yr')
	qtr = request.args.get('qtr')'''
	return co_filings(co,yr,qtr, filing)

@app.route('/mat_news/<co>/<yr>/<qtr>')
def get_mat_news(co,yr,qtr):
#	Material news is 8-K. Mergers, material agreements, etc
	filings = []
	routes = []
	mat_news = {}
	filings = get_filings(co,yr,qtr,'8-K')
	print(len(filings))
	i = 1 
	for filing in filings:
#	Data comes in the format [CIK|company|form|date|url to data]
		filing_parts = filing.split('|')
		url = sec_data + filing_parts[4] 
		content = get_text_from_url(url)
		html_content = ''
		html_content = get_html_from_text(content)
		html_path = '/home/clamb/code/sec_filings/templates/'+ co + '_' + yr + '_' + qtr + '_' + str(i) + '.html'
#	Grab the html from the 4th part of data, post split, and write it to a file
#	Then append the route of the data to an array of links and return those to the user
		with open(html_path,'w+') as hp:
			hp.write(html_content)
			hp.close()

		routes.append('https://flask.gorwellconsulting.com/one_filing/' + co + '_' + yr + '_' + qtr  + '_' +str(i) + '.html')
		i += 1
	mat_news[''+ co + ''] = routes
	return mat_news

@app.route('/one_filing/<filing>')
def show_html(filing):
#	Very simple HTML rendering tool that comes with the flask framework
	return render_template(filing)

def form_type(filing):
#	Not implemented yet.

	form_types = {'4':'insider','8-K':'Material news'}
	if filing in form_types:
		return form_types[filing]
	return 'Other/not implemented'

def get_text_from_url(url):
#	Get the text from a given URL
	r = requests.get(url)
	return r.text

def get_html_from_text(response_text):
#	Isolation the text from a file that contains text, html and binary formats
	html_content = ''
	start = 0
	end = 0
	start
	if '<!DOCTYPE>' in response_text:
		start = response_text.index('<!DOCTYPE html>')
	elif '<HTML>' in response_text.upper():
		start = response_text.upper().index('<HTML>')
	if '</HTML>' in response_text.upper():
		end = response_text.upper().index('</HTML>')

	html_content = response_text[start:(end+len('</html>'))]
	return html_content


def get_co_cik(co_seed):
#	CIK number is needed for isolating a given company's filings in the master.idx file
#	This URL will used to 'scrape' that number.

	ticker_query =  r'https://www.sec.gov/cgi-bin/browse-edgar?company=&match=&CIK={}&filenum=&State=&Country=&SIC=&owner=exclude&Find=Find+Companies&action=getcompany'.format(co_seed)
	r = requests.get(ticker_query)
	soup = BeautifulSoup(r.text, 'lxml')
#	Get the span tag text, and extract CIK number from the class tag attached, up to 11 characters

	cik_text = soup.find('span', {'class':'companyName'}).find('a').text[:11]
		
#	Get rid of leading 0's and newline characters
	return cik_text.strip('0').rstrip()

def co_filings(co,yr,qtr, filing):
	filings = []
	url = sec_full_index + str(yr) + '/' + qtr.upper() + '/master.idx'
	content = get_text_from_url(url)
	co_cik = get_co_cik(co)
	print(co_cik)
	try:
#	Attempt to get only the lines of text that correspond to the company in question.

		start_of_co_filings = content.index(co_cik)
		end_of_co_filings = content.rindex(co_cik)
	except ValueError as ve:
		print(ve)
		return 'Not found'
	
	filings = content[start_of_co_filings:end_of_co_filings].split('\n') #content.split('\n')
	filingDict = {}
	insider = []
	mat_news = []
	other = []
	for filing in filings:
		if '|' + filing + '|' in filing:
			filings.append(filing)
	filingDict['form ' + filing] = filings 
	return filings # content[start_of_co_filings:end_of_co_filings].split('\n')
