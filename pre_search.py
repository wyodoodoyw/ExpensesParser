import re
def pre_search(search_term):
    usa_airports = ['SFO', 'LAX', 'SAN', 'PSP', 'SMF',
                    'SNA', 'MCO', 'TPA', 'FLL', 'PBI',
                    'MIA', 'RSW', 'SRQ', 'HNL', 'KOA',
                    'OGG', 'LAS', 'ORD', 'DTW', 'MPS',
                    'STL', 'CVG', 'CLE', 'CMH', 'IND',
                    'EWR', 'BOS', 'LGA', 'PHL', 'PIT',
                    'IAD', 'BDL', 'ATL', 'AUS', 'DFW',
                    'IAH', 'BNA', 'MSY', 'CHS', 'DEN',
                    'PHX', 'SEA', 'SLC', 'PDX', 'ANC',
                    'U.S.A', 'US', 'USA']
    hawaii_airports = ['LIH', 'Lihue', 'OGG', 'Maui']
    can_airports = ['YYC', 'YEG', 'YFC', 'YQX', 'YHZ',
                    'YUL', 'YOW', 'YQB', 'YYT', 'YYZ',
                    'YVR', 'YYJ', 'YWG', 'YDF', 'YXX',
                    'YYR', 'ZBF']
    if search_term in usa_airports and search_term not in hawaii_airports:
        return {'type': 'destination', 'q': 'U.S.'}
    elif search_term in ['BNE', 'MEL', 'Brisbane', 'Melbourne', 'Australia']:
        return {'type': 'country', 'q': 'AU'}
    elif search_term in ['BRU', 'LGG', 'Brussels', 'Liège', 'Liege', 'Belgium']:
        return {'type': 'country', 'q': 'BE'}
    elif search_term in ['DEL', 'BOM', 'Delhi', 'Mumbai', 'Bombay', 'India']:
        return {'type': 'country', 'q': 'IN'}
    elif search_term in ['DUB', 'SNN', 'Dublin', 'Shannon', 'Ireland']:
        return {'type': 'country', 'q': 'IE'}
    elif search_term in ['FRA', 'MUC', 'TXL', 'Frankfort', 'Munich', 'Berlin', 'Germany']:
        return {'type': 'country', 'q': 'DE'}
    elif search_term in ['Hong Kong', 'HK', 'HKG']:
        return {'type': 'country', 'q': 'HK'}
    elif search_term in ['KIN', 'MBJ']:
        return {'type': 'country', 'q': 'JM'}
    elif search_term in ['LIS', 'OPO', 'Lisbon', 'Porto', 'Portugal']:
        return {'type': 'country', 'q': 'PT'}
    elif search_term in ['LHR', 'LGW', 'London', 'Heathrow', 'Gatwick', 'England', 'UK', 'U.K.']:
        return {'type': 'country', 'q': 'GB'}
    elif search_term in ['MAD', 'BCN', 'Madrid', 'Barcelona', 'Spain']:
        return {'type': 'country', 'q': 'ES'}
    elif search_term in ['MTY', 'TQO']:
        return {'type': 'country', 'q': 'MX'}
    elif search_term in ['NRT', 'HND', 'KIX', 'Narita', 'Haneda', 'Osaka', 'Tokyo', 'Japan']:
        return {'type': 'country', 'q': 'JP'}
    elif search_term in ['CDG', 'LYS', 'NCE', 'TLS', 'Paris', 'Lyon', 'Nice', 'Toulouse', 'France']:
        return {'type': 'country', 'q': 'FR'}
    elif search_term in ['FCO', 'MXP', 'VCE', 'Rome', 'Milan', 'Venice', 'Italy']:
        return {'type': 'country', 'q': 'IT'}
    elif search_term in ['GRU', 'GIG', 'Sao Paulo', 'Rio de Janeiro', 'Rio', 'Brazil']:
        return {'type': 'country', 'q': 'BR'}
    elif search_term in ['SIN', 'QPG', 'Singapore']:
        return {'type': 'country', 'q': 'SG'}
    elif search_term in ['ZRH', 'GVA', 'BSL', 'Zurich', 'Geneva', 'Basel', 'Swiss', 'Switzerland']:
        return {'type': 'country', 'q': 'CH'}
    elif re.findall(r'Y[A-Z]{2}', search_term) or search_term in ['Canada']:
        return {'type': 'destination', 'q': 'Canada'}
    elif re.search(r'[A-Z]{3}', search_term):
        return {'type': 'airport_code', 'q': search_term}
    else:
        return {'type': 'destination', 'q': search_term}
        # year = datetime.today().year
        # month = f'{datetime.today().month:02d}'