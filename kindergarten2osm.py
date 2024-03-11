#!/usr/bin/env python3
# -*- coding: utf8

# kindergarten2osm
# Converts kindergartens from Utdanningsdirektoratet api feed to osm format for import/update
# Swagger documenta: https://data-nbr.udir.no/swagger/index.html
# Usage: python kindergarten2osm.py [-noadjust]
# Use "-noadjust" argument to avoid relocation of nodes to middle of buildings
# Default output filename: "barnehager.osm"


import urllib.request, urllib.error
import html
import json
import sys
import time
import os
import errno
import math


version = "1.0.0"

relocate_tolerance = 15  # Max. meter relocation of node

building_folder = "~/Jottacloud/osm/bygninger/"  # Folder containing import building files (default folder tried first)


brands = [
	'Espira',
#	'Eventus',
	'FUS',
#	'Sammen',
	'NLM',
	'Norlandia',
	'Kanvas',
#	'Kidsa',
	'Læringsverkstedet'
]


name_conversions = {
	'Alle': 'alle',
	'Allé': 'alle',
	'Allè': 'alle',
	'Barnehage': 'barnehage',
	'Barnehagen': 'barnehage',
	'Barnehave': 'barnehave',
	'Barnehagetun': 'barnehagetun',
	'Bhg': 'barnehage',
	'Doslo': "d'Oslo",
	"D'oslo": "d'Oslo",
	'Du': 'du',
	'Fam': 'familie',
	'Fam.': 'familie',
	'Familie': 'familie',
	'Familiebarnehage': 'familiebarnehage',
	'Familiesenter': 'familiesenter',
	'Foreldreeid': 'foreldreeid',
	'Friluftsbarnehage': 'friluftsbarnehage',
	'Friluftsbarnehager': 'friluftsbarnehager',
	'Friluftsliv': 'friluftsliv',
	'Grendehus': 'grendehus',
	'Gard': 'gard',
	'Gards': 'gards',
	'Gardsbarnehage': 'gardsbarnehage',
	'Gård': 'gård',
	'Gårds': 'gårds',
	'Gårdsbarnehage': 'gårdsbarnehage',
	'Ii': 'II',
	'Kirke': 'kirke',
	'Kirkes': 'kirkes',
	'Kommunale': 'kommunale',
	'Kristelig': 'kristelig',
	'Kristelige': 'kristelige',
	'Kultur': 'kultur',
	'Kulturbarnehage': 'kulturbarnehage',
	'Kunst': 'kunst',
	'Menighet': 'menighet',
	'Menighets': 'menighets',
	'Menighetsbarnehage': 'menighetsbarnehage',
	'Midlertidig': 'midlertidig',
	'Midlertidige': 'midlertidige',
	'montessoribarnehage': 'Montessoribarnehage',
	'Musikk': 'musikk',
	'Musikkbarnehage': 'musikkbarnehage',
    'Natur': 'natur',
    'Naturbarnehage': 'naturbarnehage',
	'Of': 'of',
	'Omsorg': 'omsorg',
	'Open': 'open',
	'Opne': 'opne',
	'Oppvekstsenter': 'oppvekstsenter',
	'Oppveksttun': 'oppveksttun',
	'Oppvekstområde': 'oppvekstområde',
#	'Oppvekst': 'oppvekst'
    'Privat': 'privat',
    'Private': 'private',
    'Sentrum': 'sentrum',
    'Skog': 'skog',
    'Skole': 'skole',
    'Skoles': 'skoles',
    'Skule': 'skule',
    'Skules': 'skules',
    'Skoleordning': 'skoleordning',
    'Sokn': 'sokn',
    'Stall': 'stall',
    'steinerbarnehage': 'Steinerbarnehage',
	'Terrasse': 'terrasse',
	'Tilbud': 'tilbud',
	'Torg': 'torg',
	'Tur': 'tur',
	'Ved': '',
	'ved': '',
	'Veg': 'veg',
	'Vei': 'vei',
	'Åpen': 'åpen',
	'Åpne': 'åpne',

	'4H-Gård': '4H-gård',
	'A2g': 'A2G',
	'Abc': 'ABC',
	'Ac': 'AC',
	'Amh': 'AMH',
	'Bcc': 'BCC',
	'Bmb': 'BMB',
 	'Biss': 'BISS',
 	'Cb': 'CB',
 	'drøbak': 'Drøbak',
 	'Fbhd': 'FBHD',
 	'Fus': 'FUS',
 	'Hjr': 'HJR',
 	'Ikb': 'IKB',
 	'Imi': 'IMI',
 	'Imi-Kirken': 'IMI-kirken',
 	'ITrygge': 'I Trygge',
 	'Kfum': 'KFUM',
 	'Kfuk': 'KFUK',
	'Kfuk-Kfum': 'KFUK-KFUM',
	'Mkaf': 'MKAF',
	'Nab': 'NAB',
	"Nbu's": "NBU's",
	'Nlm': 'NLM',
	'Nlm-Barnehage': 'NLM-barnehage',
	'Nlm-Barnehagene': 'NLM-barnehagene',
	'Nvh': 'NVH',
	'Nvh-Barnehagen': 'NVH-barnehagen',
	'Nrk': 'NRK',
	'Rs': 'RS',
	'Sio': 'SiO',
	'Sit': 'SiT',
    'Sn': 'SN',
	'visthus': 'Visthus',

    'Avdeling': 'avd.',
    'avdeling': 'avd.',
    'Avd.': 'avd.',
    'Avd': 'avd.',
    'avd': 'avd.'
}

phrase_conversions = {
	'Akrobaten - barnehage': 'Akrobaten barnehage',
	'familie barnehage': 'familiebarnehage',
	'Landbruks barnehage': 'landbruksbarnehage',
	'Samholderen i': 'Samholderen',
	'Barnehage- og Vaktmester- Tjenester': 'Barnehage- og vaktmestertjenester',
	'1 Samisk og 3 Norske Avdelinger': '',
	'Av Solungen': 'Solungen',
	'Sr Bank': 'SR-Bank',
	'0 - 6': '0-6'
}

company_conversions = {
	'Al': '',
	'AL': '',
	'A/L': '',
	'ANS': '',
	'Ans': '',
	'AS': '',
	'As': '',
	'A/s': '',
	'A/S': '',
	'BA': '',
	'Ba': '',
	'B/A': '',
	'Barnehagedrift': 'barnehage',
	'DA': '',
	'Da': '',
	'Drift': '',
	'HF': '',
	'Hf': '',
	'Holding': '',
	'Ltd': '',
	'SA': '',
	'Sa': '',
	'Si': '',
	'Sso': 'SSO',
	'Stiftelse': '',
	'Stiftelsen': '',
	'stiftelsen': '',
	'Stiftinga': '',
	'Ul': ''
}



# Output message

def message (line):

	sys.stdout.write (line)
	sys.stdout.flush()



# Open file/api, try up to 5 times, each time with double sleep time

def try_urlopen (url):

	tries = 0
	while tries < 5:
		try:
			return urllib.request.urlopen(url)

		except OSError as e:  # Mostly "Connection reset by peer"
			if e.errno == errno.ECONNRESET:
				message ("\tRetry %i in %ss...\n" % (tries + 1, 5 * (2**tries)))
				time.sleep(5 * (2**tries))
				tries += 1			
	
	message ("\n\nError: %s\n" % e.reason)
	message ("%s\n\n" % url.get_full_url())
	sys.exit()



# Compute approximation of distance between two coordinates, (lon,lat), in kilometers.
# Works for short distances.

def compute_distance (point1, point2):

	lon1, lat1, lon2, lat2 = map(math.radians, [point1[0], point1[1], point2[0], point2[1]])
	x = (lon2 - lon1) * math.cos( 0.5*(lat2+lat1) )
	y = lat2 - lat1
	return 6371000.0 * math.sqrt( x*x + y*y )  # Metres



# Tests whether point (x,y) is inside a polygon.
# Ray tracing method.

def inside_polygon (point, polygon):

	if polygon[0] == polygon[-1]:
		x, y = point
		n = len(polygon)
		inside = False

		p1x, p1y = polygon[0]
		for i in range(n):
			p2x, p2y = polygon[i]
			if y > min(p1y, p2y):
				if y <= max(p1y, p2y):
					if x <= max(p1x, p2x):
						if p1y != p2y:
							xints = (y-p1y) * (p2x-p1x) / (p2y-p1y) + p1x
						if p1x == p2x or x <= xints:
							inside = not inside
			p1x, p1y = p2x, p2y

		return inside

	else:
		return None



# Calculate centre of polygon, or of list of nodes

def polygon_centre (polygon):

	length = len(polygon)
	if polygon[0] == polygon[-1]:
		length -= 1

	x = 0
	y = 0
	for node in polygon[:length]:
		x += node[0]
		y += node[1]
	return (x / length, y / length)



# Replace special characters with space

def remove_delimiters(string):

	result = ""
	last_c = " "
	for c in string:
		if c.isalnum():
			result += c
			last_c = c
		elif last_c != " ":
			result += " "
			last_c = " "

	return result.strip()



# Fix name

def transform_name(name, keep_company):

	name = name.replace("A/S", "AS").replace("A/L", "AL").replace("B/A", "BA").replace("V/", "ved ")  # Transform before splitting at "/"
	name = name.replace("/", " / ")

	if name == name.upper():
		name = name.title()

	name_split = name.split()
	name = ""
	for word in name_split:
		if word[-1] in [",", "-", ")"]:
			word_without_comma = word[:-1]
		else:
			word_without_comma = word

		if word_without_comma in name_conversions:
			name += name_conversions[ word_without_comma ]
		elif word_without_comma in company_conversions:
			if not keep_company:
				name += company_conversions[ word_without_comma ]
			elif len(word_without_comma) <= 3:
				name += word_without_comma.upper()
			else:
				name += word_without_comma
		else:
			name += word_without_comma

		if word[-1] in [",", "-", ")"]:
			name += word[-1] + " "
		else:
			name += " "

	for phrase in phrase_conversions:
		name = name.replace(phrase, phrase_conversions[ phrase ])

	name = name.strip(".,-/ ").replace(" ,", ",").replace(",,", ",").replace("  ", " ").strip()
	name = name[0].upper() + name[1:]

	return name



# Load official municipality and county names

def load_municipalities():

	global municipalities, counties

	url = "https://ws.geonorge.no/kommuneinfo/v1/kommuner"
	file = urllib.request.urlopen(url)
	municipality_data = json.load(file)
	file.close()

	municipalities = {}
	for municipality in municipality_data:
		municipalities[ municipality['kommunenummer'] ] = municipality['kommunenavnNorsk']
	municipalities['2100'] = "Longyearbyen"

	url = "https://ws.geonorge.no/kommuneinfo/v1/fylker"
	file = urllib.request.urlopen(url)
	county_data = json.load(file)
	file.close()

	counties = {}
	for county in county_data:
		counties[ county['fylkesnummer'] ] = county['fylkesnavn']
	counties['21'] = "Svalbard"



# Load kindergartens from api, convert tags and store as features

def load_kindergartens():

	message ("Loading list of kindergartens ...")

	# Load basic information of all kindergartens

	url = "https://data-nbr.udir.no/v3/enheter?sidenummer=1&antallPerSide=30000"
	file = urllib.request.urlopen(url)
	kindergarten_data = json.load(file)
	file.close()

	first_count = 0
	for kindergarten_entry in kindergarten_data['Enheter']:
		if (kindergarten_entry['ErAktiv'] == True
				and kindergarten_entry['ErBarnehage'] == True):
			first_count += 1

	message (" %s kindergartens\n" % first_count)

	if kindergarten_data['AntallSider'] > 1:
		message ("*** Note: There are more data from API than loaded\n")

	# Convert to geojson
	
	if len(sys.argv) > 1:
		filename = sys.argv[1]

	message ("Loading each kindergarten ...\n")

	operators = set()
	names = set()

	count = 0
	geocode = 0

	# Iterate all kindergartens and produce OSM file

	for kindergarten_entry in kindergarten_data['Enheter']:

		if (kindergarten_entry['ErAktiv'] != True
				or kindergarten_entry['ErBarnehage'] != True
				or any(word in kindergarten_entry['Navn'].lower() for word in ["felles", "vikar", "administrasjon", "spes.ped"])):
#				or kindergarten['ErInaktivIBasil'] == True):
			continue

		feature = {
			'geometry': {},
			'properties': {}
		}

		tags = feature['properties']

		message ("\r%i " % (first_count - count))

		# Load kindergarten details

		url = "https://data-nbr.udir.no/v3/enhet/" + str(kindergarten_entry['Orgnr'])
		file = try_urlopen(url)
		kindergarten = json.load(file)
		file.close()

		# Get coordinate

		if kindergarten['Koordinat']:
			latitude = kindergarten['Koordinat']['Breddegrad']
			longitude = kindergarten['Koordinat']['Lengdegrad']
			if not(latitude or longitude):
				latitude = 0
				longitude = 0
		else:
			latitude = 0
			longitude = 0

		feature['geometry'] = {
			'type': 'Point',
			'coordinates': [ longitude, latitude ]
		}

		# Fix kindergarten name

		name = kindergarten['Navn']
		original_name = name

		if kindergarten['Karakteristikk']:  # Department
			if any(word in kindergarten['Karakteristikk'].lower() for word in ["administrasjon", "funksjonshem", "rådgjevar"]):  # Skip
				continue

			if "avd" not in kindergarten['Karakteristikk'].lower():
				name += ", avd. " + kindergarten['Karakteristikk']
			else:
				name += ", " + kindergarten['Karakteristikk']

		name = transform_name(name, keep_company=False)
		names.add(name)

		# Generate tags

		tags['amenity'] = "kindergarten"
		tags['name'] = name
		tags['ref:barnehage'] = kindergarten['Orgnr']

		if kindergarten['Epost']:
			email = kindergarten['Epost'].lower()
			if "@mt.kommune" in email and "@mt.kommune.no" not in email:
				email += ".no"
			tags['email'] = email

		if kindergarten['Url'] and not("@" in kindergarten['Url']):
			website = kindergarten['Url'].lower().lstrip("/").replace("www2.", "").replace("www.", "").replace(" ","").strip()
			tags['website'] = "https://" + website

		if kindergarten['Telefon']:
			phone = kindergarten['Telefon'].replace("  ", " ").strip()
			if phone:
				if phone[:3] == "+47":
					phone = phone[3:].strip()
				if phone[:4] == "0047":
					phone = phone[3:].strip() 
				phone = phone.replace("+", "").lstrip("0").strip()
				phone = "+47 " + phone
				tags['phone'] =  phone
#				tags['ORIGINAL_PHONE'] = kindergarten['Telefon']

		if kindergarten['AntallBarn']:
			tags['capacity'] = str(kindergarten['AntallBarn'])

		if kindergarten['AlderstrinnFra']:
			tags['min_age'] = kindergarten['AlderstrinnFra']

		if kindergarten['AlderstrinnTil']:
			tags['max_age'] = kindergarten['AlderstrinnTil']			

		# Get operator

		if kindergarten['ErOffentligBarnehage'] == True:
			tags['operator:type'] = "public"
		elif kindergarten['ErPrivatBarnehage'] == True:
			tags['operator:type'] = "private"

		opreator = ""
		for parent in kindergarten['ForeldreRelasjoner']:
			if parent['Relasjonstype']['Navn'] == "Eierstruktur" and parent['Enhet']['Navn']:  # Owner

				operator = transform_name(parent['Enhet']['Navn'], keep_company=True)
				tags['operator'] = operator
				operators.add(operator)
				break

		for brand in brands:
			if brand in name or brand in operator:
				tags['brand'] = brand
				break

		# Get kindergarten type

		for category in kindergarten['Barnehagekategorier']:
			if category['Navn'] == "Familiebarnehage" or "familie" in name.lower():
				tags['FAMILY'] = "Familiebarnehage"
			if category['Navn'] == "Åpen barnehage" or any(n in name.lower() for n in ["åpen", "åpne", "open", "opne"]):
				tags['OPEN'] = "Åpen barnehage"


		if kindergarten['ErInaktivIBasil'] == True:
			tags['basil:fixme'] = "Nedlagt? Inaktiv i Basil."

		# Generate extra tags for help during import

		if kindergarten['DatoFoedt']:
			tags['start_date'] = kindergarten['DatoFoedt'][0:10]

		tags['DATE_UPDATED'] = kindergarten['DatoEndret'][0:10]
#		tags['MUNICIPALITY'] = "#%s %s" % (kindergarten['Kommune']['Kommunenr'], kindergarten['Kommune']['Navn'])
#		tags['COUNTY'] = "#%s %s" % (kindergarten['Fylke']['Fylkesnr'], kindergarten['Fylke']['Navn'])
		tags['MUN_REF'] = kindergarten['Kommune']['Kommunenr']
		tags['MUNICIPALITY'] = municipalities[ kindergarten['Kommune']['Kommunenr'] ]
		tags['COUNTY'] = counties[ kindergarten['Fylke']['Fylkesnr'] ]
		tags['LANGUAGE'] = kindergarten['Maalform']['Navn']

		if kindergarten['Karakteristikk']:
			tags['DEPARTMENT'] = kindergarten['Karakteristikk']

		tags['ENTITY_CODES'] = "; ".join(["%i.%s" % (code['Prioritet'], code['Navn']) for code in kindergarten['Naeringskoder']])
		tags['KINDERGARTEN_CODES'] = str("; ".join([code['Navn'] for code in kindergarten['Barnehagekategorier']]))

		if name != original_name:
			tags['ORIGINAL_NAME'] = original_name

		if kindergarten['Koordinat']:
			tags['LOCATION_SOURCE'] = kindergarten['Koordinat']['GeoKilde']

		address = kindergarten['Beliggenhetsadresse']
		if address:
			address_line = ""
			if address['Adresse'] and (address['Adresse'] != "-"):
				address_line = address['Adresse'] + ", "
			if address['Postnr']:
				address_line += address['Postnr'] + " "
			if address['Poststed']:
				address_line += address['Poststed']
			if address['Land'] and address['Land'] != "Norge":
				address_line += ", " + address['Land']
			if address_line:
				tags['ADDRESS'] = address_line

		# Build search string

		search = remove_delimiters(name.lower())
		if "barnehage" not in search:
			search += " barnehage"
		if tags['MUNICIPALITY'].lower() not in search:
			search += " " + tags['MUNICIPALITY'].lower()
		if address['Poststed'] and address['Poststed'].lower() not in search:
			search += " " + address['Poststed'].lower()
		search = search.replace("  ", " ").strip().replace(" ", "+")
		tags['SEARCH'] = search

		if not (longitude or latitude):
			tags['GEOCODE'] = "yes"
			geocode += 1

		# Add to geojson feature collection

		features.append(feature)
		count += 1

	# Save name files for verification

	file = open("barnehageeiere.txt", "w")
	file.write("\n".join(sorted(operators)))
	file.close()

	file = open("barnehagenavn.txt", "w")
	file.write("\n".join(sorted(names)))
	file.close()

	message ("\r    \t%i kindergartens loaded\n" % count)
	message ("\t%i kindergartens need geocoding\n" % geocode)



# Adjust node locations to middle of building (if inside building)

def adjust_locations(municipality_id):

	if municipality_id == "2100":  # No building file for Svalbard
		return 0

	# Load building file for municipality

	filename = "bygninger_%s_%s.geojson" % (municipality_id, municipalities[ municipality_id ].replace(" ", "_"))

	if not os.path.isfile(filename):
		test_filename = os.path.expanduser(building_folder + filename)
		if os.path.isfile(test_filename):
			filename = test_filename
		else:
			message("*** File '%s'not found\n" % filename)
			return 0

	file = open(filename)
	building_data = json.load(file)
	file.close()

	buildings = [building for building in building_data['features'] if building['geometry']['type'] == "Polygon"]

	# Add polygon bbox to speed up overlap test later

	for building in buildings:
		building['min_bbox'] = (min([ node[0] for node in building['geometry']['coordinates'][0] ]), \
								min([ node[1] for node in building['geometry']['coordinates'][0] ]))
		building['max_bbox'] = (max([ node[0] for node in building['geometry']['coordinates'][0] ]), \
								max([ node[1] for node in building['geometry']['coordinates'][0] ]))

	count = 0

	# Iterate all kindergartens in municipality and relocate slightly if inside building

	for kindergarten in features:
		if kindergarten['properties']['MUN_REF'] != municipality_id:
			continue

		node = kindergarten['geometry']['coordinates']

		# Identify building around kindergarten node

		for building in buildings:
			if (building['min_bbox'][0] < node[0] <  building['max_bbox'][0]
					and building['min_bbox'][1] < node[1] < building['max_bbox'][1]
					and inside_polygon(node, building['geometry']['coordinates'][0])):

				new_node = [ 0.5 * (building['min_bbox'][0] + building['max_bbox'][0]),
							 0.5 * (building['min_bbox'][1] + building['max_bbox'][1])]
				distance = compute_distance(new_node, node)

				if distance < relocate_tolerance and inside_polygon(new_node, building['geometry']['coordinates'][0]):
					kindergarten['geometry']['coordinates'] = new_node
					kindergarten['properties']['RELOCATED'] = str(int(distance))
					count += 1
#				else:
#					kindergarten['properties']['FIXME'] = "Adjust position"

				break

	return count



# Save kindergartens in geojson file

def save_file(filename):

	# Make sure points are not identical

	points = set()
	for feature in features:
		point = feature['geometry']['coordinates']
		point = ( round(point[0], 7), round(point[1], 7)) 
		while point in points:
			point = ( point[0], point[1] + 0.00002)
		points.add(point)
		if point != feature['geometry']['coordinates']:
			feature['geometry']['coordinates'] = point

	# Save geojson file

	kindergartens_geojson = {
		'type': 'FeatureCollection',
		'features': features
	}

	file = open(filename, "w")
	json.dump(kindergartens_geojson, file, indent=2, ensure_ascii=False)
	file.close()

	message ("Saved %i kindergartens to '%s' file\n" % (len(features), filename))



# Main program

if __name__ == '__main__':

	message ("\nkindergarten2osm\n")

	features = []  # Will contain all kindergartens

	load_municipalities()
	load_kindergartens()

	if "-noadjust" not in sys.argv:
		message ("Adjust locations ...\n")
		count = 0
		for municipality_id in sorted(list(municipalities.keys())):
			message ("\r%s " % municipality_id)
			count += adjust_locations(municipality_id)
		message ("\r    \t%i kindergartens relocated within buildings\n" % count)

	save_file("barnehager.geojson")
	message ("\n")
