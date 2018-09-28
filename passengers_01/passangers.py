# import json

def search_man(man_dict, name):
    for key in man_dict:
        if(name in man_dict[key]):
            return key

def search_carriage(carriage_dict, name):
    for key in carriage_dict:
        if (name in carriage_dict[key]):
            return key

def get_train_info(data):
    train_info = {}
    for train_index in data:
        train_info[train_index['name']] = []
        for carriage in train_index['cars']:
            train_info[train_index['name']].append(carriage['name'])

    return train_info

def man_in_carriage(data):
    carriage_info = {}
    for train_index in data:
        for carriage in train_index['cars']:
            carriage_info[carriage['name']] = carriage['people']
    return carriage_info

def switch(train_from, train_to, count, carriage_dict):

    if (len(carriage_dict[train_from]) < count):
        return False
    else:
        train_part = []
        for i in range(count):
            carriage = carriage_dict[train_from].pop()
            train_part.append(carriage)
        train_part.reverse()
        carriage_dict[train_to].extend(train_part)
        return True

def walk(man, distance, man_dict, carriage_dict): #it will not work if there are not that name
    pos_man_in_carriage = search_man(man_dict, man)
    pos_carriag_in_train = search_carriage(carriage_dict, pos_man_in_carriage)

    destination = carriage_dict[pos_carriag_in_train].index(pos_man_in_carriage) + distance
    if (destination < 0 or destination >=  len(carriage_dict[pos_carriag_in_train])):
        return False
    else:
        person_id = man_dict[pos_man_in_carriage].index(man)
        man_dict[pos_man_in_carriage].pop(person_id)

        dest_carriage = carriage_dict[pos_carriag_in_train][destination]
        man_dict[dest_carriage].append(man)
        return True

def process(data, events, car):
    carriage_dict = get_train_info(data)
    man_dict = man_in_carriage(data)

    for event in events:
        if(event['type'] == 'walk'):
            if(not walk(event['passenger'], event['distance'], man_dict, carriage_dict)):
                return -1
        elif(event['type'] == 'switch'):
            if(not switch(event['train_from'], event['train_to'], event['cars'], carriage_dict)):
                return -1

    return (len(man_dict[car]))

# data = json.load(open('tests/test12.json'))
# trains, events, result = data['trains'], data['events'], data['result']
# answer = process(trains, events, result['car'])
#
# if(answer == result['amount']):
#     print('OK!')

# print(carriage_dict)
# switch('A', 'B', 3, carriage_dict)
# print(carriage_dict)


# print(man_dict)
# walk('Alex', 2, man_dict, carriage_dict)
# print(man_dict)