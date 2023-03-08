import json
import random
random.seed(1)
from random import random

## TODO: Add documentation

def get_updated_value(current_value, volatility):
    updated_value = current_value
    mod = 0.5
    # change likelihood of moving in a certain direction if outside [0,1]
    if updated_value > 1:
        mod = 0.8
    elif updated_value < 0:
        mod = 0.2
    dir_ = 1 if random() >= mod else -1
    # size of "jumps" directly correlated with volatility
    max_to_add = volatility / 100.0
    updated_value += (random() * max_to_add * dir_)
    return updated_value

def update_agent_data(data_json):
    '''Passes in list of Company agent types as JSON string and returns the updated values'''
    data_list = json.loads(data_json)
    updated_data = dict()
    for company_dict in data_list:
        # get data from stock listing agent
        stock_listing = company_dict['stockListing']
        # get relevant attributes of stock listing agent
        value = stock_listing['value']
        volatility = stock_listing['volatility']
        # calculate the next value
        new_value = get_updated_value(value, volatility)
        # add to data structure to return
        company_name = company_dict["name"]
        updated_data[company_name] = new_value
    # return updated data in json string form
    return json.dumps(updated_data)
