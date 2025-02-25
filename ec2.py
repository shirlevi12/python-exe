import boto3 
resource = boto3.resource('ec2')
iam_client = boto3.client('iam')
ec2_client = boto3.client('ec2')

response = iam_client.get_user()
user_name = response['User']['UserName']
ami_image = "" 
type_of_instance = ""
dict_of_instances = {}

CREATE_EC2 = "1"
STOP_EC2 = "2"
START_EC2 = "3"
LIST_EC2_CRATED_BY_CLI = "4"
MAX_INSTANCES_ALLOWD_RUNNING = 2
EMPTY_LIST = 0

INSTANCE_TYPE_T3_NANO = 't3.nano'
INSTANCE_TYPE_T4G_NANO = 't4g.nano'
AMI_IMAGE_UBUNTU = 'ubuntu'
AMI_IMAGE_AMAZON = 'amazon'
AMI_IMAGES = {
    AMI_IMAGE_UBUNTU: {
        INSTANCE_TYPE_T3_NANO: 'ami-04b4f1a9cf54c11d0',
        INSTANCE_TYPE_T4G_NANO: 'ami-0a7a4e87939439934'
    },
    AMI_IMAGE_AMAZON: {
        INSTANCE_TYPE_T3_NANO: 'ami-053a45fff0a704a47',
        INSTANCE_TYPE_T4G_NANO: 'ami-0c518311db5640eff'
    }
}

filter_of_running = [{
        'Name':'tag:Owner','Values': [user_name]},
        {'Name':'tag:CreatedBy','Values': ["cli"]},
        {'Name': 'instance-state-name', 'Values': ['running']
        }]

filter_of_stopped = [{
        'Name':'tag:Owner','Values': [user_name]},
        {'Name':'tag:CreatedBy','Values': ["cli"]},
        {'Name': 'instance-state-name', 'Values': ['stopped']
        }]

filter_of_all =[{
        'Name':'tag:Owner','Values': [user_name]},
        {'Name':'tag:CreatedBy','Values': ["cli"]},
        ]

running_instances = resource.instances.filter(
    Filters=[
        {'Name': 'instance-state-name', 'Values': ['running']},
        {'Name': 'tag:Owner', 'Values': [user_name]}  

    ]
)

running_instances_count = len(list(running_instances))

def choose_ec2_type():
    type_of_instance = input("enter a type of instance:\n[1]t3.nano\n[2]t4g.nano\n").lower()

    match type_of_instance:
        case "1": # t3.nano
            type_of_instance = INSTANCE_TYPE_T3_NANO
            ami_image = choose_ec2_ami()
        case "2":# t4g.nano
            type_of_instance = INSTANCE_TYPE_T4G_NANO
            ami_image = choose_ec2_ami()
        case _: #invalid choice
            print("you entered wrong type of instance")
            return choose_ec2_type()
    return type_of_instance, AMI_IMAGES[ami_image][type_of_instance], ami_image

def choose_ec2_ami():
    AMI_choice = input("what ami would you like to use?\n[1]ubuntu\n[2]amazon linux\n").lower()
    match AMI_choice:
        case "1":
            return AMI_IMAGE_UBUNTU
        case "2":
            return AMI_IMAGE_AMAZON
        case _:
            print("you entered wrong type of ami")
            return choose_ec2_ami()

def create_ec2_instance():
    if running_instances_count >= MAX_INSTANCES_ALLOWD_RUNNING:
        print ("sorry you cant have more than 2 running instances")
    else: 
        name_of_instance = input("please enter instance name: ")
        
        type_of_instance, ami_choice, ami_name = choose_ec2_type()

        resource.create_instances(
            ImageId = ami_choice,
            InstanceType = type_of_instance,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': name_of_instance},
                    {'Key': 'Owner', 'Value': user_name},
                    {'Key': 'CreatedBy', 'Value': 'cli'}
                ]
            }]
        )
        
        print (f"instance named '{name_of_instance}' instance type: {type_of_instance} ami: {ami_name} was successfully created")

def start_ec2():
    list_of_stopped_instances = resource.instances.filter(Filters=filter_of_stopped)
    for instance in list_of_stopped_instances:
        for tag in instance.tags:
            if tag['Key'] == 'Name':     
                dict_of_instances[instance.id]= tag['Value']
    if len(dict_of_instances) <= EMPTY_LIST:
        print("you dont have stopped instances")
    else:
        print(f"this is the list of stopped instance \n {dict_of_instances}")
        instance_id_to_start = input("enter instance id you would like to start: ")
        if instance_id_to_start in dict_of_instances:
            ec2_client.start_instances(
                InstanceIds=[instance_id_to_start,],
                )
            print(f"you seccsecfuly started {dict_of_instances[instance.id]} instance")
        else:
            print("this id is invalid")

def stop_ec2():
    list_of_running_instances = resource.instances.filter(Filters=filter_of_running)
    for instance in list_of_running_instances:
        for tag in instance.tags: 
            if tag['Key'] == 'Name':     
                dict_of_instances[instance.id]= tag['Value']
    if len(dict_of_instances) <= EMPTY_LIST:
        print("you dont have stopped instances")
    else:       
        print(f"this is the list of running instance\n {dict_of_instances}")
        instance_id_to_stop = input("enter instance id you would like to stop: ")
        if instance_id_to_stop in dict_of_instances:
            ec2_client.stop_instances(
                InstanceIds=[instance_id_to_stop,],
                )
            print(f"you seccsecfuly stopped {dict_of_instances[instance.id]} instance")
        else:
            print("this id is invalid")

def list_ec2_instances():
    list_of_all_instances = resource.instances.filter(Filters=filter_of_all)
    for instance in list_of_all_instances:
        for tag in instance.tags:
            if tag['Key'] == 'Name':     
                dict_of_instances[instance.id]= tag['Value']
    if len(dict_of_instances) <= EMPTY_LIST:
        print("your list is empty")
    print(f"this is the list of all the instances created: \n {dict_of_instances} ")

def main():
    while True:
        ask_for_action = input("enter a number for an action\n[1]create intance\n[2]stop intance\n[3]start instance\n[4]list of instances created by cli\n ").lower()
        if ask_for_action == CREATE_EC2:
            create_ec2_instance()
        elif ask_for_action == START_EC2:
            start_ec2()
        elif ask_for_action == STOP_EC2:
            stop_ec2()
        elif ask_for_action == LIST_EC2_CRATED_BY_CLI:
            list_ec2_instances()
        else:
            print("you enterd invalid action")

        ask_for_another_action = input("whould you like to do another action? ").lower()
        if ask_for_another_action != "yes":
            break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()