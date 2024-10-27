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

    # --- Australia ---
    elif search_term in ['Sydney', 'SYD']:
        return {'type': 'airport_code', 'q': 'SYD'}
    elif search_term in ['BNE', 'MEL', 'Brisbane', 'Melbourne', 'Australia']:
        return {'type': 'country_code', 'q': 'AU'}

    # --- Britain ---
    elif search_term in ['LHR', 'LGW', 'London', 'Heathrow', 'London Heathrow', 'Gatwick']:
        return {'type': 'destination', 'q': 'London (LHR) / Gatwick (LGW) '}
    elif search_term in ['Edinburgh', 'EDI']:
        return {'type': 'airport_code', 'q': 'EDI'}
    elif search_term in ['Glasgow', 'GLA']:
        return {'type': 'airport_code', 'q': 'GLA'}
    elif search_term in ['Manchester', 'MAN']:
        return {'type': 'airport_code', 'q': 'VRA'}

    # --- Costa Rica ---
    elif search_term in ['Liberia', 'LIR']:
        return {'type': 'airport_code', 'q': 'LIR'}
    elif search_term in ['San Jose', 'SJO']:
        return {'type': 'airport_code', 'q': 'SYD'}

    # --- Cuba ---
    elif search_term in ['Cayo Coco', 'CCC']:
        return {'type': 'airport_code', 'q': 'CCC'}
    elif search_term in ['Havana', 'HAV']:
        return {'type': 'airport_code', 'q': 'HAV'}
    elif search_term in ['Santa Clara', 'SNU']:
        return {'type': 'airport_code', 'q': 'SNU'}
    elif search_term in ['Varadero', 'VRA']:
        return {'type': 'airport_code', 'q': 'VRA'}

    # --- Dominican Republic ---
    elif search_term in ['Puerto Plato', 'POP']:
        return {'type': 'airport_code', 'q': 'POP'}
    elif search_term in ['Punta Cana', 'PUJ']:
        return {'type': 'airport_code', 'q': 'PUJ'}

    # --- Mexico ---
    elif search_term in ['MTY', 'TQO']:
        return {'type': 'destination', 'q': 'Mexico'}
    elif search_term in ['Cancun', 'CUN']:
        return {'type': 'airport_code', 'q': 'CUN'}
    elif search_term in ['Cozumel', 'CZM']:
        return {'type': 'airport_code', 'q': 'CZM'}
    elif search_term in ['Huatulco', 'HUX']:
        return {'type': 'airport_code', 'q': 'HUX'}
    elif search_term in ['Mexico', 'Mexico City', 'MEX']:
        return {'type': 'airport_code', 'q': 'MEX'}
    elif search_term in ['Puerto Vallarta', 'PVR']:
        return {'type': 'airport_code', 'q': 'PVR'}
    elif search_term in ['San Jose del Cabo', 'SJD']:
        return {'type': 'airport_code', 'q': 'SJD'}
    elif search_term in ['Santa Lucia', 'NLU']:
        return {'type': 'airport_code', 'q': 'NLU'}

    # --- Asia - East ---
    elif search_term in ['Hong Kong', 'HK', 'HKG']:
        return {'type': 'country_code', 'q': 'HK'}
    elif search_term in ['NRT', 'HND', 'KIX', 'Narita', 'Haneda', 'Osaka', 'Tokyo', 'Japan']:
        return {'type': 'country_code', 'q': 'JP'}
    elif search_term in ['SIN', 'QPG', 'Singapore']:
        return {'type': 'country_code', 'q': 'SG'}
    elif search_term in ['Beijing', 'PEK']:
        return {'type': 'airport_code', 'q': 'PEK'}
    elif search_term in ['Shanghai', 'PVG']:
        return {'type': 'airport_code', 'q': 'PVG'}

    # --- Asia - South ---
    elif search_term in ['DEL', 'BOM', 'Delhi', 'Mumbai', 'Bombay', 'India']:
        return {'type': 'country_code', 'q': 'IN'}

    # --- Caribbean/Sun ---
    elif search_term in ['KIN', 'MBJ']:
        return {'type': 'country_code', 'q': 'JM'}

    # --- Europe ---
    elif search_term in ['BRU', 'LGG', 'Brussels', 'Liège', 'Liege', 'Belgium']:
        return {'type': 'country_code', 'q': 'BE'}
    elif search_term in ['DUB', 'SNN', 'Dublin', 'Shannon', 'Ireland']:
        return {'type': 'country_code', 'q': 'IE'}
    elif search_term in ['FRA', 'MUC', 'TXL', 'Frankfort', 'Munich', 'Berlin', 'Germany']:
        return {'type': 'country_code', 'q': 'DE'}
    elif search_term in ['LIS', 'OPO', 'Lisbon', 'Porto', 'Portugal']:
        return {'type': 'country_code', 'q': 'PT'}
    elif search_term in ['MAD', 'BCN', 'Madrid', 'Barcelona', 'Spain']:
        return {'type': 'country_code', 'q': 'ES'}
    elif search_term in ['CDG', 'LYS', 'NCE', 'TLS', 'Paris', 'Lyon', 'Nice', 'Toulouse', 'France']:
        return {'type': 'country_code', 'q': 'FR'}
    elif search_term in ['FCO', 'MXP', 'VCE', 'Rome', 'Milan', 'Venice', 'Italy']:
        return {'type': 'country_code', 'q': 'IT'}
    elif search_term in ['ZRH', 'GVA', 'BSL', 'Zurich', 'Geneva', 'Basel', 'Swiss', 'Switzerland']:
        return {'type': 'country_code', 'q': 'CH'}

    # --- South America ---
    elif search_term in ['GRU', 'GIG', 'Sao Paulo', 'Rio de Janeiro', 'Rio', 'Brazil']:
        return {'type': 'country_code', 'q': 'BR'}
    elif search_term in ['Bogota', 'BOG']:
        return {'type': 'airport_code', 'q': 'BOG'}
    elif search_term in ['Cartagena', 'CTG']:
        return {'type': 'airport_code', 'q': 'CTG'}

    # --- Canada ---
    elif re.findall(r'Y[A-Z]{2}', search_term) or search_term in ['Canada']:
        return {'type': 'destination', 'q': 'Canada'}

    # --- Else ---
    elif re.search(r'[A-Z]{3}', search_term):
        return {'type': 'airport_code', 'q': search_term}
    else:
        return {'type': 'destination', 'q': search_term}
