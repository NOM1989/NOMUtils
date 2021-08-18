import json

async def read_data(file_name):
    with open(f'{file_name}.json') as x:
        return(json.load(x))

async def write_data(file_name, data_to_dump):
    with open(f'{file_name}.json', 'w') as x:
        json.dump(data_to_dump, x, indent=2)