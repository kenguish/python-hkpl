"""
hkpl.py
Simple python class to scrap books checked out from the Hong Kong Public Libraries system.

Import "hkpl" into your program, and call fetch_library_info method with the 2 parameters:
	user_barcode: your library card number
	user_pin: your pin number

Created by Kenneth Anguish on 6/24/2010.

"""

import sys, os, re, string
from urllib2 import HTTPError

import re
import mechanize
from BeautifulSoup import BeautifulSoup

def fetch_library_info(user_barcode, user_pin):
	LIBRARY_URL = "https://libcat.hkpl.gov.hk/webpac_eng/login.cgi"

	br = mechanize.Browser()
	br.set_handle_robots(False)
	
	# Set a nice browser agent
	br.addheaders = [ ("User-agent", "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322)") ]
	br.set_handle_refresh(False)

	try:
		br.open( LIBRARY_URL )
	except HTTPError, e:
		sys.exit("%d: %s" % (e.code, e.msg))

	br.select_form(nr=0)
	br["barcode_prompt"] = user_barcode
	
	try:
		# check if it has digit. No digits means library card number
		dummy = int(user_pin)
		br["pin_prompt"] = user_pin
	except:
		# exceptions mean it should be a HKID number
		br["masc_prompt"] = user_pin

	try:
		br.submit()
		
		print "\nHKPL Record of %s" % user_barcode
		# Grab Items out
		br.follow_link(url_regex=r"webpac", nr=6)
		itemsout_response = br.response()
		itemsout_content = itemsout_response.read()
	
		# Parse!
		soup = BeautifulSoup( itemsout_content )
		try:
			items_checkedout_string = soup.body.form.table.contents[7].contents[1].contents[1].contents[1].tr.td.font.next
			print items_checkedout_string
		
			item_no = 1

			items_tr = soup.body.form.table.contents[7].contents[1].contents[1].next.next.contents[3].contents[0].contents[1].contents[0].findNextSiblings('tr')
			for eachbook_row in items_tr:
				checkbox, book_number, book_name, library_location, due_date, renewal_time = eachbook_row.contents
				print "%d. %s %s %s %s %s" % (item_no, book_number.contents[0], string.ljust(book_name.contents[0], 38), string.ljust(library_location.contents[0], 18), due_date.contents[0], renewal_time.contents[0])
				item_no = item_no + 1
		
		except AttributeError, e:
			# Error in parsing
			print "ERROR> Unable to make sense of your borrowed items data"
		except IndexError, ie:
			print "No reservations"
	
	except HTTPError, e:
	    sys.exit("Unable to retrieve library information from HKPL website: %d: %s" % (e.code, e.msg))

if __name__ == "__main__":
	fetch_library_info( "FILL_IN_LIBRARY_CARD_NUMBER", "PIN_NUMBER" )

	print "\n"	


