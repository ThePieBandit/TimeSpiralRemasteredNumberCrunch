import csv
import requests
import json

SCRYFALL_URL_TSR = 'https://api.scryfall.com/cards/search?order=name&q=(set:tsr AND -frame:1997) -t:basic'
SCRYFALL_URL_TSB = 'https://api.scryfall.com/cards/search?order=name&q=(set:tsp or set:fut or set:plc) unique:prints -t:basic'
SCRYFALL_SUFFIXES = (
    ' AND c=w',
    ' AND c=u',
    ' AND c=b',
    ' AND (c=r OR ghostfire)',
    ' AND c=g AND -t:land',
    ' AND c:m',
    ' AND c=c AND t:artifact',
    ' AND -c:g AND t:land'
)

def normalize_colors(colors, name, types):
    if name == "Ghostfire":
        return 'R'
    if len(colors) > 1:
        return 'Gold'
    elif len(colors) == 0:
        if 'Land' in types:
            return 'L'
        else:
            return 'A'
    elif 'Land' in types: #Thanks Dryad Arbor!
        return 'L'
    else:
        return colors[0]

def fetch_cards(uri,data,page=1):
    print('Begin: Download %s, page %s of results' % (uri, page))
    for conditions in SCRYFALL_SUFFIXES:
        try:
            print('Begin: Download %s, page %s of results' % (uri+conditions, page))
            with requests.get(uri+conditions) as response:
                tmp_scryfall_data = response.json()
                for card in tmp_scryfall_data['data']:
                    data[card['name']] = (card['collector_number'], card['name'], normalize_colors(card['colors'], card['name'], card['type_line']), card['image_uris']['normal'])
                if "next_page" in tmp_scryfall_data:
                    fetch_cards(tmp_scryfall_data["next_page"], data, page + 1)
        except Exception as err:
            print('Exception: Was unable to download %s, page %s of results' % (uri+conditions, page))
            print(err)

tsb_data = {}
tsb_images = {}
tsr_data = {}
tsr = [None]*289

fetch_cards(SCRYFALL_URL_TSB, tsb_data)
fetch_cards(SCRYFALL_URL_TSR, tsr_data)


with open('tsr_data.json', mode='w') as json_file:
    json.dump(tsr_data, json_file)


for key in tsr_data:
    tsb_data.pop(key, None)
    try:
      tsr.insert(int(tsr_data[key][0]), key)
    except Exception as err:
      print(err)
for key in tsb_data:
    tsb_images[key] = tsb_data[key][3]

tsb_crunched_out = []
tsb_crunched_maybe = []
tsb_crunched_in = []

last = None
gap = 0
lastIndex = 0

for card in tsr:
    if last == None:
        last = card
        continue
    if card == None:
        gap += 1
        continue
    else:
        lastIndex = tsr_data[card][0]
        print('Gap size ' + str(gap) + ' between ' + last + ' and ' + card)
        tsb_crunched_tmp_maybe_in = []
        tsb_crunched_tmp_out = []
        for possible in tsb_data:
            if tsr_data[last][2] != tsr_data[card][2] and tsb_data[possible][2] != tsr_data[card][2]:
                print('New Section of Cards, ' + possible+ '  is maybe in!')
                tsb_crunched_tmp_maybe_in.append(possible)
            elif possible < last and tsb_data[possible][2] == tsr_data[last][2]:
                tsb_crunched_tmp_out.append(possible)
                print(possible + ' is before ' + last +', It\'s out')
            elif possible < card and tsb_data[possible][2] == tsr_data[card][2]:
                if (gap == 0):
                    tsb_crunched_tmp_out.append(possible)
                    print(possible + ' is before ' + card +', but no space, It\'s out')
                else:
                    tsb_crunched_tmp_maybe_in.append(possible)
                    print(possible + ' is before ' + card)
            else:
                print(possible + ' is after ' + card +', time to check')
                break
        for possible in tsb_crunched_tmp_maybe_in:
            tsb_data.pop(possible, None)
        for possible in tsb_crunched_tmp_out:
            tsb_data.pop(possible, None)
            tsb_crunched_out.append(possible)
        if 0 == gap:
            print('No Gap, all out!')
        elif len(tsb_crunched_tmp_maybe_in) == gap:
            print(str(gap) + ' equals list size, they are all in!')
            tsb_crunched_in = tsb_crunched_in + tsb_crunched_tmp_maybe_in
        else:
            print(str(gap) + ' less than list size, some of these are still possible')
            tsb_crunched_maybe.append((gap, tsb_crunched_tmp_maybe_in))
        # Prepare for next iteration
        last = card
        gap = 0
print('Last index found was ' + lastIndex )
tsb_crunched_maybe.append((288-int(lastIndex), list(tsb_data.keys())))

json_out = {}
with open('TSR_IN.csv', mode='w') as csv_file:
    writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    json_out['in'] = []
    for card in tsb_crunched_in:
        json_out['in'].append({'name': card, 'image': tsb_images[card] })
        writer.writerow([card])
with open('TSR_OUT.csv', mode='w') as csv_file:
    writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    json_out['out'] = []
    for card in tsb_crunched_out:
        json_out['out'].append({'name': card, 'image': tsb_images[card] })
        writer.writerow([card])
with open('TSR_MAYBE.csv', mode='w') as csv_file:
    writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    json_out['possible'] = []
    for possibility in tsb_crunched_maybe:
        possible_cards = []
        for card in possibility[1]:
            possible_cards.append({'name': card, 'image': tsb_images[card] })
        json_out['possible'].append({'gap': int(possibility[0]), 'cards': possible_cards })
        writer.writerow([possibility[0], possibility[1]])

with open('tsr_crunch_data.json', mode='w') as json_file:
    json.dump(json_out, json_file)
