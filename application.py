import os
from flask import Flask, render_template, json, request
import urllib, urllib2
import xml.etree.ElementTree as ET
import json


application = Flask(__name__)
ZILLOW_URL = "http://www.zillow.com/webservice/GetSearchResults.htm"
ZILLOW_API_KEY = os.environ.get('ZILLOW_API_KEY', None)

def format_address_to_uri(address, cityStateZip):
    # Takes the given street address and cityStateZip, and formats
    # the URI string
    parameters = {'zws-id' : ZILLOW_API_KEY, 'address': address, 'citystatezip' : cityStateZip}
    uri = ZILLOW_URL + '?' + urllib.urlencode(parameters)
    return uri


# Home page
@application.route("/", methods=['GET'])
def main():    
    return render_template('search.html')

# POST Method to invoke search
@application.route("/", methods=['POST'])
def search():
    # Retrieve the entered values from the form
    _address   = request.form['inputAddress']
    _cityState = request.form['inputCityState']
    _zip       = request.form['inputZip']

    if (_cityState == u"" and _zip == u""):
        return handle_error(501)

    cityStateZip = _zip if _zip != "" else _cityState
    # Format the info for the URL request
    uri = format_address_to_uri(_address, cityStateZip)
    try:
        response_xml_str = urllib2.urlopen(uri).read()
    except Exception, e:
        # Trigger an error
        return handle_error(4)
    
    xml_dom = ET.fromstring(response_xml_str)
    formatted_response = process_zillow_response(xml_dom)
    return formatted_response

def process_zillow_response(xml_data):
    error_code = xml_data.find("message/code").text
    if error_code != "0":
        return handle_error(int(error_code))

    # Process Each Section Individually
    response = {}

    # Links Section
    response['links'] = format_links_section(xml_data)
    # Address Section
    response['address'] = format_address_section(xml_data)
    # Zestimate 
    response['zestimate'] = format_zestimate_section(xml_data)
    # Local Real Estate
    response['localRealEstate'] = format_local_real_estate_section(xml_data)

    response = json.dumps(response)
    return response, 200

# DATA FORMATTERS
def format_links_section(xml_data):
    home_details    = xml_data.find("response/results/result/links/homedetails").text
    home_details    = "Home Details Page;{0}".format(home_details)
    # home_details    = "<a href={0}>Home Details Page</a>".format(home_details)

    graphs_and_data = xml_data.find("response/results/result/links/graphsanddata").text
    graphs_and_data = "Chart Data Page;{0}".format(graphs_and_data)
    map_this_home   = xml_data.find("response/results/result/links/mapthishome").text
    map_this_home   = "Map this Home Page;{0}".format(map_this_home)
    comparables     = xml_data.find("response/results/result/links/homedetails").text
    comparables     = "Comparables;{0}".format(comparables)


    formatted_links = [home_details, graphs_and_data, map_this_home, comparables]
    return formatted_links

def format_address_section(xml_data):
    street    = xml_data.find("response/results/result/address/street").text
    city      = xml_data.find("response/results/result/address/city").text
    state     = xml_data.find("response/results/result/address/state").text
    zipcode   = xml_data.find("response/results/result/address/zipcode").text
    latitude  = xml_data.find("response/results/result/address/latitude").text
    longitude = xml_data.find("response/results/result/address/longitude").text

    line_0 = street
    line_1 = "{0}, {1} {2}".format(city, state, zipcode)
    line_2 = "Coordinates: {0}, {1}".format(latitude, longitude)
    formatted_address = [line_0, line_1, line_2]

    return formatted_address

def format_zestimate_section(xml_data):
    amount       = xml_data.find("response/results/result/zestimate/amount").text
    amount       = "Rent Zestimate: ${0}".format(amount)
    last_updated = xml_data.find("response/results/result/zestimate/last-updated").text
    last_updated = "Last Updated: {0}".format(last_updated)
    value_change = xml_data.find("response/results/result/zestimate/valueChange").text
    value_change = "30-day change: ${0}".format(value_change)
    value_low    = xml_data.find("response/results/result/zestimate/valuationRange/low").text
    value_high   = xml_data.find("response/results/result/zestimate/valuationRange/high").text
    value_range  = "Value Range: ${0} to ${1}".format(value_low, value_high)

    formatted_zestimate_section = [amount, last_updated, value_change, value_range]
    return formatted_zestimate_section

def format_local_real_estate_section(xml_data):
    region_name = xml_data.find("response/results/result/localRealEstate/region").get('name')
    region_type = xml_data.find("response/results/result/localRealEstate/region").get('type')
    region_id = xml_data.find("response/results/result/localRealEstate/region").get('id')
    region_string = "Name: {0} (Type: {1}; ID: {2})".format(region_name, region_type, region_id)

    zindex_value = xml_data.find("response/results/result/localRealEstate/region/zindexValue").text
    zindex_value = "Zillow Home Value Index;{0}".format(zindex_value)

    region_overview_link = xml_data.find("response/results/result/localRealEstate/region/links/overview").text
    region_overview_link = "Link to Region overview;{0}".format(region_overview_link)
    for_sale_by_owner_link = xml_data.find("response/results/result/localRealEstate/region/links/forSaleByOwner").text
    for_sale_by_owner_link = "Link to For Sale by Owner homes page;{0}".format(for_sale_by_owner_link)
    for_sale_link = xml_data.find("response/results/result/localRealEstate/region/links/forSale").text
    for_sale_link = "Link to for sale homes page;{0}".format(for_sale_link)

    formatted_local_real_estate_section = [region_string,\
                                            zindex_value,\
                                            region_overview_link,\
                                            for_sale_by_owner_link,\
                                            for_sale_link]
    return formatted_local_real_estate_section

def handle_error(error_code):
    error_help = ""

    # 1 - service error
    if error_code == 1:
        error_help = "Check to see if your url is properly formed: delimiters, character cases, etc."
    # 2 - incorrect ZWSID
    elif error_code == 2:
        error_help = "Check if you have provided a ZWSID in your API call. If yes, check if the ZWSID is keyed in correctly. If it still doesn't work, contact Zillow to get help on fixing your ZWSID."
    # 3 - web services unavailable
    elif error_code == 3:
        error_help = "The Zillow Web Service is currently not available. Please come back later and try again."
    # 4 - api call unavailable
    elif error_code == 4:
        error_help = "The Zillow Web Service is currently not available. Please come back later and try again."
    # 500 - invalid or missing address parameter
    elif error_code == 500:
        error_help = "Check if the input address matches the format specified in the input parameters table. When inputting a city name, include the state too. A city name alone will not result in a valid address."
    # 501 - invalid or missing citystatezip parameter
    elif error_code == 501:
        error_help = "Check if the input address matches the format specified in the input parameters table. When inputting a city name, include the state too. A city name alone will not result in a valid address."
    # 502 - no results found
    elif error_code == 502:
        error_help = "Sorry, the address you provided is not found in Zillow's property database."
    # 503 - failed to resolve city, state, zip
    elif error_code == 503:
        error_help = "Please check to see if the city/state you entered is valid. If you provided a ZIP code, check to see if it is valid."
    # 504 - no coverage for specified area
    elif error_code == 504:
        error_help = "The specified area is not covered by the Zillow property database."
    # 505 - timeout
    elif error_code == 505:
        error_help = "Your request timed out. The server could be busy or unavailable. Try again later."
    # 506 - address string too long
    elif error_code == 506:
        error_help = "Address string was too long. If address is valid, try using abbreviations."
    # 507 - no exact match found
    elif error_code == 507:
        error_help = "No exact match found. Verify that the given address is correct."
    # 508 - no exact match found for input address
    elif error_code == 508:
        error_help = "No exact match found. Verify that the given address is correct."
    else:
        error_help = "Unrecognized Error."
    error_string = "Error code: {0}. {1}".format(error_code, error_help)

    return error_string, error_code

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
