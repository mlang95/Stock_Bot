import discord
import asyncio
import requests
import re
import random
from datetime import datetime
from discord.utils import get
from datetime import timedelta
from iexfinance import Stock
import iexfinance
from ballpark import business
from bot_token_test import the_bot_token
from html import unescape
from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.request
import prettytable
from scipy.signal import savgol_filter as smooth #for supres
from numpy import array #list to array
import numpy as np
import io
import shutil
import random
from pandas.io.html import read_html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pyautogui
from pprint import pprint
import string
asyncio.sleep(10)
client = discord.Client()

last_activity_timer = datetime.now() #set our last activity to 'now'
inactivity_channel = discord.Object(id='1234') #set this to a channel id where we should send an inactivity message after 15 minutes

class Shout():
	def __init__(self,mention,ticker,time,price,currentprice,sentiment): #mention ticker time price currentprice sentiment
		self.mention = mention
		self.ticker = ticker
		self.time = time
		self.sentiment = sentiment
		self.price = price
		self.currentprice = currentprice
def Ticker_Check(string):
	Words = string.split(" ")
	ignore = ["LOL",'LMAO','ROFL',"CEO","CNBC","IDK"]
	for word in Words:
		if word.isupper() and len(word) in [2,3 ,4] and string.upper() != string:
			wordLetters = word.split()
			for letter in wordLetters:
				if letter not in wordLetters:
					return False
				else:
					if word not in ignore:
						return True

def Find_Tickers(string):
	Words = string.split(" ")
	letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYQ")
	Tickers = []
	ignore = ["LOL",'LMAO','ROFL',"CEO","CNBC","IDK"]
	for word in Words:
		if word.isupper() and len(word)in [2,3 ,4] and string.upper() != string:
			wordLetters = word.split()
			for letter in wordLetters:
				notTicker = False
				if letter not in wordLetters:
					notTicker = True
				if notTicker is False:
					if word not in ignore:
						try: #checks to see if we can find the ticker on finviz
							page = urlopen("https://finviz.com/quote.ashx?t="+ word + "&ty=c&ta=0&p=d").read()
							Tickers.append(word)
						except:
							print("%s couldn't be found on finviz, not adding" % word)
	return Tickers

def Find_Price(string):
	words = string.split(" ")
	for word in words:
		try:
			return float(word)
		except:
			pass
	else:
		return 'None'
		
def Get_Price(ticker):
		try:
			page = urlopen("https://finviz.com/quote.ashx?t="+ ticker + "&ty=c&ta=0&p=d").read()
			soup = BeautifulSoup(page, "html5lib")
			table = soup.find_all('table')
			table_body = table[3].find('tbody') #is the 4th table on the page afaik
			cells = table_body.find_all('td')
			currentPrice = ''
			i=0
			while i < (len(cells)):
			#may have to str() everything to get it to work
				if 'Price' in cells[i]:
					return cells[i+1].text
				i+=1
		except:
			print("failed to get price")
			return str(0)
			
			
	
def Sentiment_Check(string):
	words = string.lower().split(" ")
	bullish = ["up","bull","long","over","green","bullish","bounce"]
	bearish = ["down","short","bear","under","red","bearish","drop"]
	for word in words:
		for bull in bullish:
			if word in bull:
				return "bullish"
		for bear in bearish:
			if word in bear:
				return "bearish"
	return 'None'
		
	
	
def Capture_Message(message,tab,newline,time):
	if Ticker_Check(message.content):
		TickersAndTimes = open("TickersAndTimes.txt","a+")
		Tickers = Find_Tickers(message.content)
		Price = Find_Price(message.content)
		Sentiment = Sentiment_Check(message.content)
		mention = "<@"+message.author.id+">"
		for ticker in Tickers:
			currentPrice = Get_Price(ticker)
			TickersAndTimes.write(mention+tab+ticker+tab+time+tab+str(Price)+tab+currentPrice+tab+Sentiment+newline) #mention ticker time price currentprice sentiment
		TickersAndTimes.close()


@client.event
@asyncio.coroutine
def on_message(message):
	global last_activity_timer #global variable, variable, etc is required to pull 'globals' between coroutines
	tab="\t"
	newline = "\n"
	time = "%s:%s" % (datetime.now().hour,datetime.now().minute)
	if message.author == client.user: #ignore messages from ourselves (the bot)
		return
	elif message.server.id =="317462567532625944":
		Capture_Message(message,tab,newline,time)
	
	if message.content.upper().startswith('!TODAYSEARNINGS'):
		last_activity_timer = datetime.now()
		page = urlopen("https://www.nasdaq.com/earnings/earnings-calendar.aspx").read()
		soup = BeautifulSoup(page, "html5lib")
		table = soup.find('table')
		#print(table)
		table_body = table.find('tbody')
		rows = table_body.find_all('tr')
		data = prettytable.PrettyTable(["PM/AH","Ticker","Consensus","# of est","#Last Yr EPS"])
		columns_to_grab = [0,1,4,5,7]
		new_rows = []
		for row in rows:
			cols = row.find_all('td')
			if "Pre-market" in str(cols[0]): #turn cols[0] to a string - .text gives us nothing
				cols[0].clear() #clear the existing data
				cols[0].append("PM") #add in PM
				new_rows.insert(0,cols)
			else:
				cols[0].clear()
				cols[0].append("AH")
				new_rows.append(cols) #end of list = append
			Name = str(cols[1]).split() #Shorten the name to just the Ticker to save space
			for word in Name:
				if '(' in word:
					Half_Ticker = word.replace('(','')
					Ticker = Half_Ticker.replace(')','')
					cols[1].clear()
					cols[1].append(Ticker)
		for row in new_rows:
			cols = [ele.text.strip() for ele in (row[x] for x in columns_to_grab)]
			data.add_row(cols)
			if len(data.get_string()) > 1800:
				yield from client.send_message(message.channel, "```" + data.get_string(sortby='PM/AH', reversesort=True) + "```")
				data.clear_rows()
		yield from client.send_message(message.channel, "```" + data.get_string() + "```")


	#End !upcomingearnings
	
	elif message.content.upper().startswith('!BUY') or message.content.upper().startswith('!SELL'):
		split_message = message.content.upper().split(' ')
		if len(split_message) > 1:
			Ticker = split_message[1]
		else:
			Ticker = 'HMNY'
		Number = random.uniform(0,100)
		List = ['#'+Ticker+'? Sure, why not?','BEEP BOOP what the fuck do I know?',"According to my probability back-testing algorithm, you have a " + str(round(Number,4)) + "% chance of successfully doing your ass in with " + Ticker, "Seems like a shitty idea, go for it", "I've seen better ideas on Wall Street Bets","You're going to make StockTwits Proud buying "+Ticker,'#'+Ticker+' will blow up again tomorrow... feel sorry for those of you that panicked','#'+Ticker+' got in at 6.22 with 1k shares. Your best trades just go.','#'+Ticker+' 60 mullion shares traded and UP big. What else do you need to know! ','#'+Ticker+ ' I was gonna short this but then I got high','In 4 weeks #'+Ticker+' will be in a $110.9 Billion Market. Cheap Here', Ticker + '? far from worried lol',Ticker + ' has to go eventually, right?']
		String = random.choice(List)
		yield from client.send_message(message.channel, "```" + String + "```")
		
	#End !buy or !sell
	
	elif message.content.upper().startswith('!BLOOMBERG'):
		#DRIVER = 'chromedriver'
		chrome_options = Options()
		chrome_options.add_argument('--headless')
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--disable-dev-shm-usage')
		driver = webdriver.Chrome(executable_path="C:/Users/Liquid Trading LLC/Desktop/le_stock_bot/chromedriver.exe")
		#driver = webdriver.Chrome(DRIVER)
		#print("driver")
		driver.get('https://finviz.com/')
		#maximize_window()
		#print("google'd")
		screenshot = driver.get_screenshot_as_file('C:/Users/Liquid Trading LLC/Desktop/finviz.png')
		yield from client.send_file(message.channel, "C:/Users/Liquid Trading LLC/Desktop/finviz.png", content='', filename= "finviz.png")
		#print("screenshot")
		driver.quit()
		#print("quit")
		#yield from client.send_file(message.channel, screenshot, content="", filename="bloomberg.png")
	
	
	elif message.content.upper().startswith('!UPGRADE') or message.content.upper().startswith('!DOWNGRADE'):
		split_message = message.content.split(' ')
		Ticker = split_message[1]
		driver = webdriver.Chrome()
		driver.get("https://finviz.com/quote.ashx?t="+ Ticker + "&ty=c&ta=0&p=d")
		table = driver.find_element_by_xpath('//div[@class="fullview-ratings-outer"]/table//table/..')
		table_html = table.get_attribute('innerHTML')
		page = urlopen("https://finviz.com/quote.ashx?t="+ Ticker + "&ty=c&ta=0&p=d").read()
		soup = BeautifulSoup(page, "html5lib")
		table = soup.find_all('table')
		for i in range(len(table)):
			print(table[i].text)
		table_body = table[7].find('tbody') #is the ?th table on the page afaik
		Date = ''
		Up_Down = ''
		Company = ''
		Weight = ''
		Price = ''
		data = prettytable.PrettyTable(["Date","Type","Company","Weight","Price"])
		i = 0
		cells = table_body.find_all('td')
		while i < len(rows):
			Date = cells[0+i].text
			Up_Down = cells[1+i].text
			Company = cells[2+i].text
			Weight = cells[3+i].text
			Price = cells[4+i].text
			data.add_row([Date, Up_Down, Weight, Price])
			i+=5
			if len(data.get_string()) > 1500:
				yield from client.send_message(message.channel, "```" + data.get_string() + "```")
				data.clear_rows()
		yield from client.send_message(message.channel, "```" + data.get_string() + "```")
	#End Upgrade
	
	elif message.content.upper().startswith("!HALT"):
		page = urlopen("https://www.nasdaqtrader.com/trader.aspx?id=TradeHalts").read()
		soup = BeautifulSoup(page, "html5lib")
		table = soup.find(id='divTradeHaltResults').find_all('table') #//*[@id="divTradeHaltResults"] comes up empty for some reason
		print(table)
		rows = soup.find_all('td')
		print(rows)
		
	
	elif message.content.upper().startswith('!DATA'):
	#!newdata cbrp
	#For CBRP Price is : 6.59 || Volume : 257,671 || Float : 42.42M || Short Float  : 15.76% || Avg Volume : 1.22M || Change : 4.56% || Earnings: October 9 AMC
		split_message = message.content.split(' ')
		k=1
		while (k) < len(split_message):
			Ticker= split_message[k]
			page = urlopen("https://finviz.com/quote.ashx?t="+ Ticker + "&ty=c&ta=0&p=d").read()
			soup = BeautifulSoup(page, "html5lib")
			table = soup.find_all('table')
			table_body = table[3].find('tbody') #is the 4th table on the page afaik
			cells = table_body.find_all('td')
			Shares_Outstanding = ''
			Earnings = ''
			Float = ''
			Short_Float = ''
			Rel_Vol = ''
			Average_Volume = ''
			Volume_Today =''
			Price =''
			Change = ''
			Beta = ''
			Volume =''
			i=0
			while i < (len(cells)):
			#may have to str() everything to get it to work
				if 'Shs Outstand' in cells[i]:
					Shares_Outstanding = cells[i+1].text
				if 'Earnings' in cells[i]:
					Earnings = cells[i+1].text
				if 'Shs Float' in cells[i]:
					Float = cells[i+1].text
				if 'Short Float' in cells[i]:
					Short_Float = cells[i+1].text
				if 'Rel Volume' in cells[i]:
					Rel_Vol = cells[i+1].text
				if 'Avg Vol' in cells[i]:
					Average_Volume = cells[i+1].text
				if 'Volume' == cells[i].text:
					Volume_Today = cells[i+1].text
				if "Price" in cells[i]:
					Price = cells[i+1].text
				if "Change" in cells[i]:
					Change = cells[i+1].text
				if "Beta" in cells[i]:
					Beta = cells[i+1].text
				i+=1
			Columns = '||'
			Price_String = '%s Price : %s' % (Ticker, Price)
			Volume_String = 'Volume : %s' % Volume_Today # Volume_Today, Shares_Outstanding, Float, Short_Float, Rel_Vol, Beta, Change, Earnings
			Shares_String = 'Shares : %s' % Shares_Outstanding
			Float_String = 'Float : %s' % Float
			Short_String = 'Short Float : %s' % Short_Float
			Rel_String = 'Rel Volume : %s' % Rel_Vol
			Beta_String = 'Beta : %s' % Beta
			Change_String = 'Change : %s' % Change
			Earnings_String = 'Earnings : %s' % Earnings
			All_Data_In_Strings = [Price_String, Volume_String, Shares_String,Short_String,Rel_String,Beta_String,Change_String,Earnings_String]

			padding = max(map(len,All_Data_In_Strings))
			print(padding)
			New_String = '{0} {1} {2} {3} {4}\n{5} {6} {7} {8} {9}\n{10} {11} {12} {13} {14}'.format(Price_String.ljust(padding),Columns, Volume_String.ljust(padding),Columns, Shares_String.ljust(padding),Float_String.ljust(padding), Columns, Short_String.ljust(padding),Columns,Rel_String.ljust(padding),Beta_String.ljust(padding),Columns,Change_String.ljust(padding),Columns,Earnings_String.ljust(padding))
			print(New_String)
			String = "```%s Price : %s \t\t|| Volume : %s \t\t|| Shares : %s\n\t Float : %s \t\t|| Short Float : %s \t\t|| Rel Volume : %s\n\t Beta : %s \t\t\t|| Change : %s \t\t|| Earnings : %s ```" % (Ticker, Price, Volume_Today, Shares_Outstanding, Float, Short_Float, Rel_Vol, Beta, Change, Earnings)
			yield from client.send_message(message.channel, "`"+New_String+"`")	
			k+=1
				
	# end !data

	# elif message.content.upper().startswith('!DATA'):
		# last_activity_timer = datetime.now()
		# #For crbp Price is : 6.59 || Volume : 257,671 || Float : 42.42M || Short Float  : 15.76% || Avg Volume : 1.22M || Prev Close : 6.45
		# stock_name = message.content[6:] #cut out !data *space* (will it get multiple if we do STOCK, STOCK1, STOCK2 ?)
		# doForLoop = False
		# if "," in stock_name:
			# stock_name = stock_name.replace(" ", "").split(",")
			# doForLoop = True
		# try:
			# if doForLoop:
				# the_message = ""
				# for x in stock_name:
					# x = x.upper()
					# stock_data = Stock(stock_name)
					# the_message = the_message + "{} - {} || Price : ${:,.2f} || Volume : {} || Float : {} || Short Float  : {:.3%} || Avg Volume : {} || Prev Close : ${:,.2f}\n\n".format(
					# stock_data.get_company_name()[x], stock_data.get_company()[x]["symbol"], stock_data.get_price()[x], human_format(stock_data.get_volume()[x]), human_format(stock_data.get_float()[x]),
					# (stock_data.get_short_interest()[x]/stock_data.get_float()[x]), human_format(stock_data.get_quote()[x]['avgTotalVolume']), stock_data.get_previous()[x]['close']
					# )
					
				# yield from client.send_message(message.channel, the_message.rstrip('\n')) #rstrip last \n out
			# else:
				# stock_data = Stock(stock_name)
				# yield from client.send_message(message.channel, "{} - {} || Price : ${:,.2f} || Volume : {} || Float : {} || Short Float  : {:.3%} || Avg Volume : {} || Prev Close : ${:,.2f}".format(
				# stock_data.get_company_name(), stock_data.get_company()["symbol"], stock_data.get_price(), human_format(stock_data.get_volume()), human_format(stock_data.get_float()),
				# (stock_data.get_short_interest()/stock_data.get_float()), human_format(stock_data.get_quote()['avgTotalVolume']), stock_data.get_previous()['close']
				# ))
		# except iexfinance.utils.exceptions.IEXSymbolError as error:
			# yield from client.send_message(message.channel, "Error: {0}".format(error))
		# except ValueError as error:
			# yield from client.send_message(message.channel, "Error: {0}".format(error))

#end !data

	elif message.content.lower().startswith("!join"):
		pyautogui.click(1220,400)
	elif message.content.lower().startswith("!leave"):
		yield from client.disconnect()
	elif message.content.startswith('!news'):
		last_activity_timer = datetime.now()
		stock_name = message.content[6:]
		try:
			stock_data = Stock(stock_name)
			message_to_send = "News for: {} - {}".format(stock_data.get_company_name(), stock_data.get_company()["symbol"])
			for x in stock_data.get_news(last=5):
				message_to_send += "\n{} - {}".format(unescape(x["headline"]), x["url"])
			yield from client.send_message(message.channel, message_to_send)
		except iexfinance.utils.exceptions.IEXSymbolError as error:
			yield from client.send_message(message.channel, "Error: {0}".format(error))
		except ValueError as error:
			yield from client.send_message(message.channel, "Error: {0}".format(error))

#end !news


	elif message.content.upper().startswith('!EARNINGS'):
		last_activity_timer = datetime.now()
		stock_name = message.content[10:]
		try:
			stock_data = Stock(stock_name)
			page = urlopen("https://finviz.com/quote.ashx?t="+ stock_name + "&ty=c&ta=0&p=d").read()
			soup = BeautifulSoup(page, "html5lib")
			table = soup.find_all('table')
			table_body = table[3].find('tbody') #is the 4th table on the page afaik
			cells = table_body.find_all('td')
			i=0
			Future_Earnings = ''
			EPS_Next = ''
			TTM = ''
			while i < (len(cells)):
				if 'EPS next Q' in cells[i]:
					EPS_Next = cells[i+1].text
				elif 'Earnings' in cells[i]:
					Future_Earnings = cells[i+1].text
				elif 'EPS (ttm)' in cells[i]:
					TTM = cells[i+1].text
				i+=1
			stock_data_earnings = stock_data.get_earnings()[0]
			stock_data_earnings_two = stock_data.get_earnings()[1]
			stock_data_earnings_three = stock_data.get_earnings()[2]
			stock_data_earnings_four = stock_data.get_earnings()[3]
			yield from client.send_message(message.channel, "{} - {}```\nReport Date: {}\t Expected : {} \tEPS(ttm) : {}\nReport Date : {}\tConsensus : {}\tActual : {}\nReport Date : {}\tConsensus : {}\tActual : {} \
			\nReport Date : {}\tConsensus : {}\tActual : {}\nReport Date : {}\tConsensus : {}\tActual : {}```".format(
			stock_data.get_company_name(), stock_data.get_company()["symbol"],Future_Earnings,EPS_Next,TTM, stock_data_earnings["EPSReportDate"], stock_data_earnings["consensusEPS"], stock_data_earnings["actualEPS"],
			stock_data_earnings_two["EPSReportDate"], stock_data_earnings_two["consensusEPS"], stock_data_earnings_two["actualEPS"],
			stock_data_earnings_three["EPSReportDate"], stock_data_earnings_three["consensusEPS"], stock_data_earnings_three["actualEPS"],
			stock_data_earnings_four["EPSReportDate"], stock_data_earnings_four["consensusEPS"], stock_data_earnings_four["actualEPS"]
			))
		except iexfinance.utils.exceptions.IEXSymbolError as error:
			yield from client.send_message(message.channel, "Error: {0}".format(error))
		except ValueError as error:
			yield from client.send_message(message.channel, "Error: {0}".format(error))

#end !earnings

	elif message.content.startswith('!heatmap'):
		urllib.request.urlretrieve('https://finviz.com/grp_image.ashx?bar_sector_t.png', "heatmap.png")
		yield from client.send_file(message.channel, 'heatmap.png')

#end !heatmap

	elif message.content.upper().startswith('!TREEMAP'):
		last_activity_timer = datetime.now()
		e = discord.Embed()
		e.set_image(url="https://finviz.com/map.ashx?t=sec")
		#e.set_thumbnail(url=""https://finviz.com/map.ashx?t=sec")
		yield from client.send_message(message.channel, embed=e)
		
# end !treemap

	elif message.content.lower().startswith("!shout"):
		f = open("TickersAndTimes.txt","r")
		lines = f.readlines()
		Alerts = []
		test = False
		for line in lines:
			alert = line.split("\t")
			for shout in Alerts:
				test = False
				if alert[1] == shout.ticker:
					print(alert[1],shout.ticker)
					test = True
			if test is False:
				print("appending %s" % alert[1])
				try:
					Alerts.append(Shout(alert[0],alert[1],alert[2],alert[3],alert[4],alert[5])) #mention ticker time price currentprice sentiment
				except:
					print("failure to append")
		alertString = ''
		space = ' '
		tab = '\t'
		newline = '\n'
		for alert in Alerts:

			page = urlopen("https://www.nasdaq.com/market-activity/stocks/"+str(alert.ticker)).read()
			print("page")
			soup = BeautifulSoup(page, "html5lib")
			print("soup")
			tr = soup.find_all("tr","summary-data__row")
			for i in tr:
				td = i.find_all("td","summary-data__cell")
				c = 0
				while c < len(td):
					print(td[c])
					if td[c] == "Today's High/Low":
						print("Found it!")
						string = td[c+1].split("/")
						high = string[0]
						low = string[1]
						highdiff = (high - alert.price)/alert.price
						lowdiff = (alert.price-low)/low
						if lowdiff > highdiff:
							change = "decreased"
							highlow = low
							difference = lowdiff
						else:
							change = "increased"
							highlow = high
							difference = highdiff
					c+=1
				else:
					highlow = "fuck"
					difference = "can't find it"
					change = "dunno"
			stringToAdd=alert.mention+" alerted us of " + alert.ticker + " at " + alert.time + " and $"+alert.price+". It then went from $" +alert.currentprice + " to $" + highlow + " giving us a " + difference + "% " + change + "." + newline
			if (len(alertString) + len(stringToAdd)) < 2000:
				alertString += stringToAdd
			else:
				if (len(alertString)) < 2000:
					yield from client.send_message(message.channel,alertString)
		yield from client.send_message(message.channel,alertString)


	elif message.content.upper().startswith('!HOTSTOCKS'):
		f = open("pprint.txt","w")
		last_activity_timer = datetime.now()
		page = urlopen("https://finviz.com/").read()
		soup = BeautifulSoup(page, "html5lib")
		tables = soup.find_all('table',class_='t-home-table')
		for i in tables:
			table_rows = i.find_all('tr', onmouseout="this.className='table-light-cp-row';")
			print(i.text)
			f.write(str(pprint(i)))
			print("NEXT TABLE")
			for j in table_rows:
				print(j.text)
				print("NEXT ROW")
		f.close()
	elif message.content.upper().startswith('!CHART'):
		#!chart d amzn
		split_message = message.content.upper().split(' ')
		if 'D' in split_message[1]:
			time = 'd'
			#daily
		elif '1M' in split_message[1]:
			time = '1m'
			#intraday is premium? not sure what the timeframe is set as
		elif 'W' in split_message[1]:
			time = 'w'
			#week
		elif 'MO' in split_message[1]:
			time = 'm'
			#month
		else:
			time = 'd'
		ticker = split_message[2]
		e = discord.Embed()
		e.set_image(url="https://finviz.com/chart.ashx?t="+ticker+"&ty=c&ta=0&p="+time+"&s=l")
		yield from client.send_message(message.channel, embed=e)
	#end !chart

	elif message.content.upper().startswith('!IPOLIST'):
		last_activity_timer = datetime.now()
		page = urlopen("https://www.nasdaq.com/markets/ipos/activity.aspx?tab=upcoming").read()
		soup = BeautifulSoup(page, "html5lib")
		table = soup.find('table')
		#print(table)
		table_body = table.find('tbody')
		rows = table_body.find_all('tr')
		if len(rows) == 3 and 'NASDAQ' in rows[0].text:
			yield from client.send_message(message.channel, "```ain't none of them IPO sum bitches left dis here month```")
		else:
			data = prettytable.PrettyTable(["Company Name","Symbol","Market","Price","Shares","Offer Amount","Expected IPO Date"])
			for row in rows:
				cols = row.find_all('td')
				cols = [ele.text.strip() for ele in cols]
				data.add_row(cols)
				if len(data.get_string()) > 1500:
					yield from client.send_message(message.channel, "```" + data.get_string() + "```")
					data.clear_rows()
			yield from client.send_message(message.channel, "```" + data.get_string() + "```")

		#print(data.get_string())
		
#end !ipolist


	elif message.content.startswith('!calendar'):
		last_activity_timer = datetime.now()
		page = urlopen("https://anasdaq.econoday.com/byday.asp").read()
		soup = BeautifulSoup(page, "html5lib")
		table = soup.find_all('table')
		#print(table[6])
		table_body = table[6].find('tbody')
		rows = table_body.find_all('tr')
		data = prettytable.PrettyTable(["Time","For","Event","Value Name","Consensus","Actual"])
		#data.vrules = prettytable.ALL
		#data.hrules = prettytable.ALL
		for row in rows[3:]:
			cols = row.find_all('td')
			cols = [ele.text.strip() for ele in cols]
			if len(cols) == 6:
				data.add_row(cols)
				if len(data.get_string()) > 1500: #if our string is big, send and reset
					yield from client.send_message(message.channel, "```" + data.get_string() + "```")
					data = prettytable.PrettyTable(["Time","For","Event","Value Name","Consensus","Actual"])
					#data.vrules = prettytable.ALL
					#data.hrules = prettytable.ALL
		yield from client.send_message(message.channel, "```" + data.get_string() + "```") #send after we're 'really' done

#end !calendar


	elif message.content.startswith('!fda'):
		last_activity_timer = datetime.now()
		page = urlopen("https://www.biopharmcatalyst.com/calendars/fda-calendar").read()
		soup = BeautifulSoup(page, "html5lib")
		table = soup.find('table')
		#print(table)
		table_body = table.find('tbody')
		rows = table_body.find_all('tr')
		data = prettytable.PrettyTable(["TICKER","DRUG","STAGE","CATALYST"])
		count = 1
		columns_to_grab = [0,2,3,4]
		for row in rows:
			cols = row.find_all('td')
			cols = [ele.text.strip() for ele in (cols[x] for x in columns_to_grab)]
			cols[1] = cols[1].splitlines()[0] #split off the drug stuff
			cols[3] = cols[3].splitlines()[0] #split off the catalyst notes
			#print(cols)
			if len(data.get_string()) > 1000:
				yield from client.send_message(message.channel, "```" + data.get_string() + "```")
				data = prettytable.PrettyTable(["TICKER","DRUG","STAGE","CATALYST"])
				count = count + 1
			data.add_row(cols)
			if count > 2:
				break

#end !fda


	elif message.content.startswith('!ta'):
		last_activity_timer = datetime.now()
		stock_name = message.content[4:]
		data = prettytable.PrettyTable(["Levels","Price"])
		try:
			stock_data = Stock(stock_name)
			key_stats = stock_data.get_key_stats()
			recent_data = stock_data.get_chart()
			recent_data_input = []
			for ele in recent_data:
				recent_data_input.append(ele["high"])
			#print(recent_data_input)
			sup_res_data = gentrends(recent_data_input)
			sup_res_data.seek(0) #return to 0, otherwise we get an empty file?
			data.add_row(["52-Week High",key_stats["week52high"]])
			data.add_row(["52-Week Low",key_stats["week52low"]])
			yield from client.send_message(message.channel, "```" + data.get_string() + "```")
			yield from client.send_file(message.channel, sup_res_data, content="", filename="daschart.png")
		except iexfinance.utils.exceptions.IEXSymbolError as error:
			yield from client.send_message(message.channel, "Error: {0}".format(error))
		except ValueError as error:
			yield from client.send_message(message.channel, "Error: {0}".format(error))

#end !ta

	elif message.content.startswith('!command'):
		list_of_commands = ['ta [stock]','todaysearnings','data [stock]','news [stock]','earnings [stock]','fda','calendar','ipolist','heatmap','chart [timeframe (D,W,M)] [stock]','buy [stock]','sell [stock]','bloomberg (in development)','upgrades/downgrades (in development)']
		text =  ''
		for command in list_of_commands:
			text += '!' + command + '\n'
		yield from client.send_message(message.channel, text)
		
#end !commands


#END on_message

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def gentrends(x, window=1/3.0, charts=True): #from https://github.com/dysonance/Trendy/blob/master/trendy.py
    """
    Returns a Pandas dataframe with support and resistance lines.
    :param x: One-dimensional data set
    :param window: How long the trendlines should be. If window < 1, then it
                   will be taken as a percentage of the size of the data
    :param charts: Boolean value saying whether to print chart to screen
    """

    import numpy as np
    import pandas as pd

    x = np.array(x)

    if window < 1:
        window = int(window * len(x))

    max1 = np.where(x == max(x))[0][0]  # find the index of the abs max
    min1 = np.where(x == min(x))[0][0]  # find the index of the abs min

    # First the max
    if max1 + window > len(x):
        max2 = max(x[0:(max1 - window)])
    else:
        max2 = max(x[(max1 + window):])

    # Now the min
    if min1 - window < 0:
        min2 = min(x[(min1 + window):])
    else:
        min2 = min(x[0:(min1 - window)])

    # Now find the indices of the secondary extrema
    max2 = np.where(x == max2)[0][0]  # find the index of the 2nd max
    min2 = np.where(x == min2)[0][0]  # find the index of the 2nd min

    # Create & extend the lines
    maxslope = (x[max1] - x[max2]) / (max1 - max2)  # slope between max points
    minslope = (x[min1] - x[min2]) / (min1 - min2)  # slope between min points
    a_max = x[max1] - (maxslope * max1)  # y-intercept for max trendline
    a_min = x[min1] - (minslope * min1)  # y-intercept for min trendline
    b_max = x[max1] + (maxslope * (len(x) - max1))  # extend to last data pt
    b_min = x[min1] + (minslope * (len(x) - min1))  # extend to last data point
    maxline = np.linspace(a_max, b_max, len(x))  # Y values between max's
    minline = np.linspace(a_min, b_min, len(x))  # Y values between min's

    # OUTPUT
    trends = np.transpose(np.array((x, maxline, minline)))
    if charts is True:
        trends = pd.DataFrame(trends, index=np.arange(0, len(x)),
                          columns=['Data', 'Max Line', 'Min Line'])
        import matplotlib as mpl
        mpl.use('Agg')
        import matplotlib.pyplot as plt
        fig = plt.figure()
        the_plot = fig.add_subplot(111)
        the_plot.plot(trends)
        outputStream = io.BytesIO()
        plt.savefig(outputStream)

    return outputStream

@asyncio.coroutine
# def auto_restart():
	# global last_activity_timer, inactivity_channel
	# yield from client.wait_until_ready()
	# while not client.is_closed:
		# elapsedTime = datetime.now() - last_activity_timer
		# if(elapsedTime.seconds > 900): # 15 minutes * 60 seconds = 900 seconds
			# #work some message magic
			# #yield from client.send_message(inactivity_channel, "some message here")
		# yield from asyncio.sleep(60) #sleep for 1 minute

# #end 15 minutes inactivity

@client.event
@asyncio.coroutine
def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
#end on_ready


client.run("","") #token!
