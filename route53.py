import boto3

route53_client = boto3.client('route53')
iam_client = boto3.client('iam')
user_response = iam_client.get_user()
user_name = user_response['User']['UserName']

CREATE_HOSTED_ZONE_CHOISE = "1"
CREATE_DNS_RECORD_CHOISE = "2"
UPDATE_DNS_RECORD_CHOISE = "3"
REMOVE_DNS_RECORD_CHOISE = "4"
CREATE_DNS_RECORD = "CREATE"
DELETE_DNS_RECORD = "DELETE"
UPDATE_DNS_RECORD = "UPSERT"
DNS_TIME_TO_LIVE = 300


def get_hosted_zones_with_required_tags():
    hosted_zones = route53_client.list_hosted_zones()
    matching_hosted_zones = []

    for hosted_zone in hosted_zones['HostedZones']:
        hosted_zone_id = hosted_zone['Id'].split('/hostedzone/')[1]

        tags_response = route53_client.list_tags_for_resource(
            ResourceType='hostedzone',
            ResourceId=hosted_zone_id)

        tags = tags_response['ResourceTagSet']['Tags']
        owner_tag = None
        created_by_tag = None

        for tag in tags:
            if tag['Key'] == 'Owner' and tag['Value'] == user_name:
                owner_tag = tag
            if tag['Key'] == 'CreatedBy' and tag['Value'] == 'cli':
                created_by_tag = tag

        if owner_tag and created_by_tag:
            matching_hosted_zones.append(hosted_zone)

    return matching_hosted_zones


def create_hosted_zone():
    
    name_for_hosted_zone = input("Enter a name for hosted zone: ")
    secret_key = input("Enter a secret key of your choice (should be unique for each request): ")

    try:
        route_response = route53_client.create_hosted_zone(
            Name=name_for_hosted_zone,
            CallerReference=secret_key,
            HostedZoneConfig={
                'Comment': f'Hosted zone for {name_for_hosted_zone}',
                'PrivateZone': False
            }
        )
    except Exception as e:
        print(f"Could not create hosted zone: {e}")
        return

    hosted_zone_id = route_response['HostedZone']['Id']
    hosted_zone_id = hosted_zone_id.split('/hostedzone/')[1]

    route53_client.change_tags_for_resource(
        ResourceType='hostedzone',
        ResourceId=hosted_zone_id,
        AddTags=[
            {'Key': 'Owner', 'Value': user_name},
            {'Key': 'CreatedBy', 'Value': 'cli'}
        ],
    )
    print(f"Hosted zone named {name_for_hosted_zone} created with id: {hosted_zone_id}")
    return hosted_zone_id, name_for_hosted_zone


def manage_dns_record(matching_zones, command):  
    print("\nChoose the Hosted Zone to create the DNS record in:")
    
    counter = 1
    for zone in matching_zones:
        print(f"[{counter}] {zone['Name']} (ID: {zone['Id']})")
        counter += 1
    
    try:
        chosen_zone_index = int(input("Enter the number of the hosted zone: ")) - 1
        selected_zone = matching_zones[chosen_zone_index]
    except IndexError:
        print(f"Cannot choose zone {chosen_zone_index+1}.")
        return
    except ValueError:
        print(f"Cannot choose zone.")
        return

    name_for_dns_record = input("Enter a name for the DNS record: ")
    ip_target = input("Enter the target ip: ")

    try:
        route53_client.change_resource_record_sets(
            HostedZoneId=selected_zone['Id'],
            ChangeBatch={
                'Comment': f'{command} action: type "A" record for {selected_zone["Name"]}',
                'Changes': [
                    {
                        'Action': command,
                        'ResourceRecordSet': {
                            'Name': name_for_dns_record,
                            'Type': 'A',
                            'TTL': DNS_TIME_TO_LIVE,
                            'ResourceRecords': [
                                {'Value': ip_target}
                            ]
                        }
                    },
                ]
            }
        )
        print(f"{command} action for DNS record {name_for_dns_record} was successful")
    except Exception as e:
        print("YOU CANT DO THAT")
        


def main():
    # hosted_zone_id = None
    # name_for_hosted_zone = None

    while True:
        ask_for_action = input("Enter a number for an action:\n[1]Create hosted zone\n[2]Create DNS record\n[3]Update DNS record\n[4]Remove DNS record\n")
        matching_zones = get_hosted_zones_with_required_tags()

        if ask_for_action == CREATE_HOSTED_ZONE_CHOISE:
            # hosted_zone_id, name_for_hosted_zone = create_hosted_zone()
            create_hosted_zone()

        elif ask_for_action == CREATE_DNS_RECORD_CHOISE:
            if not matching_zones:
                print("No hosted zones found with the required tags.")
                continue

            manage_dns_record(matching_zones,CREATE_DNS_RECORD)

        elif ask_for_action == UPDATE_DNS_RECORD_CHOISE:
            manage_dns_record(matching_zones,UPDATE_DNS_RECORD)
        elif ask_for_action == REMOVE_DNS_RECORD_CHOISE:
            manage_dns_record(matching_zones,DELETE_DNS_RECORD)
        else:
            print("No such option, try again.")

        ask_for_another_action = input("Would you like to do another action? yes/no ").lower()
        if ask_for_another_action != "yes":
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
