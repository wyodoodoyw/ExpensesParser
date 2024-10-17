def parse(data, year, month):
    for i in range(find_start_line(data), find_end_line(data)):
        new_destination = Destination()

        line = data[i]

        if 'Canada' in line:
            new_destination.destination = 'Canada'
        elif 'Jamaica' in line:
            destination = 'Jamaica - Other'
        elif 'Mexico - Other' in line:
            destination = 'Mexico - Other'
        elif 'U.S.' in line:
            destination = 'U.S.'
        else:
            dest_list = re.findall(r'[A-Z]{3}\)', line)
            last_index_destination = line.index(dest_list[len(dest_list) - 1]) + 5
            destination = line[0:last_index_destination]

        line = line[len(destination):]
        country_code = re.findall(r'[A-Z]{2}', line)[0]
        # station column could be Airport code (ex. ALG) or * for multiple
        if re.search(r'[A-Z]{3}', line):
            airport_code = re.findall(r'[A-Z]{3}', line)[0]
        else:
            airport_code = '*'
        # destinations can be bracelet or per diem
        if not '$' in line:
            bracelet_provided = True
            previous_allowance = None
            adjustment = None
            status = None
            percent_change = None
            breakfast = None
            lunch = None
            dinner = None
            snack = None
            total = None
        else:
            bracelet_provided = False
            price_list = re.findall(r'\d{1,3}\.\d{2}', line)
            percentage_list = re.findall(r'\d{1,2}\.\d{1,2}\%', line)
            previous_allowance = price_list[0]
            adjustment = price_list[1]
            status = ('*No Change' in line)
            percent_change = percentage_list[0]
            breakfast = price_list[2]
            lunch = price_list[3]
            dinner = price_list[4]
            snack = price_list[5]
            total = price_list[6]

        new_destination = {
            destination: {
                'country_code': country_code,
                'airport_code': airport_code,
                'bracelet_provided': bracelet_provided,
                'previous_allowance': previous_allowance,
                'adjustment': adjustment,
                'status': status,
                'percent_change': percent_change,
                'breakfast': breakfast,
                'lunch': lunch,
                'dinner': dinner,
                'snack': snack,
                'total': total
            }
        }
        if 'Zurich' in destination:
            new_destination[destination]['airport_code'] = '*'
        save(new_destination, year, month)