import yaml
from aws_util import AWS_Client


def set_credentials():
    access_key = input('Please enter your AWS ACCESS_KEY:') or None
    secret_access_key = input(
        'Please enter your AWS SECRET_ACCESS_KEY:') or None
    region = input(
        'Please specify default region(Default in us-east-1):') or 'us-east-1'
    return access_key, secret_access_key, region


def read_yaml():
    with open('config.yaml', 'r') as config:
        data = yaml.load(config, Loader=yaml.FullLoader)
    return data


def main():
    access_key, secret_access_key, region = set_credentials()
    data_list = read_yaml()
    server_list = list(data_list.keys())
    for server in server_list:
        config = data_list[server]
        client = AWS_Client(config)
        client.set_client(access_key, secret_access_key, region)
        client.set_block_device_mapping()
        client.set_userdata()
        client.get_latest_ami()
        client.create_instance()


main()
