import boto3


class AWS_Client():
    def __init__(self, config):
        self.instance_type = config['instance_type']
        self.ami_type = config['ami_type']
        self.architecture = config['architecture']
        self.root_device_type = config['root_device_type']
        self.virtualization_type = config['virtualization_type']
        self.min_count = config['min_count']
        self.max_count = config['max_count']
        self.volumes = config['volumes']
        self.users = config['users']
        self.key_name = config.get('key_name', None)

        self.ec2 = None
        self.ssm = None
        self.block_device_mapping = []
        self.userdata = "#!/bin/bash\n"
        self.latest_ami_id = None

    def set_client(self, access_key, secret_access_key, region):
        self.ec2 = boto3.client('ec2', aws_access_key_id=access_key,
                                aws_secret_access_key=secret_access_key, region_name=region)
        self.ssm = boto3.client('ssm', aws_access_key_id=access_key,
                                aws_secret_access_key=secret_access_key, region_name=region)

    def set_block_device_mapping(self):
        for volume in self.volumes:
            self.block_device_mapping.append(
                {
                    'DeviceName': volume['device'],
                    'Ebs': {
                        'VolumeSize': volume['size_gb']
                    }
                }
            )

    def set_userdata(self):
        for volume in self.volumes:
            self.userdata += f"mkdir {volume['mount']}\n"
            self.userdata += f"mount {volume['device']} {volume['mount']}\n"
            self.userdata += f"echo {volume['device']}  {volume['mount']}  {volume['type']}  defaults,nofail  0  2 > /etc/fstab\n"
            self.userdata += f"chmod 707 /{volume['mount']}\n"
        for user in self.users:
            self.userdata += f"adduser {user['login']}\n"
            self.userdata += f"cd /home/{user['login']}\n"
            self.userdata += f"mkdir .ssh\n"
            self.userdata += f"chmod 700 .ssh\n"
            self.userdata += f"cd .ssh\n"
            self.userdata += f"curl http://169.254.169.254/latest/meta-data/public-keys/0/openssh-key >> authorized_keys\n"
            self.userdata += f"chmod 600 authorized_keys\n"
            self.userdata += f"chown -R {user['login']}:{user['login']} /home/{user['login']}/\n"

    def get_latest_ami(self):
        ami_path = [
            f'/aws/service/ami-amazon-linux-latest/{self.ami_type}-ami-{self.virtualization_type}-{self.architecture}-{self.root_device_type}']
        response = self.ssm.get_parameters(Names=ami_path)
        self.latest_ami_id = response['Parameters'][0]['Value']

    def create_instance(self):
        response = self.ec2.run_instances(
            InstanceType=self.instance_type,
            ImageId=self.latest_ami_id,
            MaxCount=self.max_count,
            MinCount=self.min_count,
            BlockDeviceMappings=self.block_device_mapping,
            UserData=self.userdata,
            KeyName=self.key_name,

        )
        return response
