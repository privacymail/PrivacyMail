# Transform maillist.txt to JSON format to import it into django.
import json


service_id = 0
identity_id = 1

print ("The id of the identities have to be unique or existing data in the database will be overwritten!\n"
       "Importing data this way also can't check for duplicates!")
response = input("Creating JSON for importing into empty database? y/N: ")
if (response == 'y'):
    print ("IDs will start with 1!")
else:
    service_id = int(input("Current max service id: "))
    identity_id = int(input("Current max identity id: ")) + 1


input_file = open('maillist.txt', 'r')
input_read = input_file.read().split('##')
data_to_write = []


# Add an identity to the current service being processed.
def add_identities(raw_identities, current_service_id):
    global identity_id
    for i in raw_identities.split('\n')[1:]:
        if i in ['\n', '\r\n', ' ', '']:
            continue
        i_split = i.split(' ')
        # print (i)
        identity = {}
        identity["model"] = "identity.identity"
        identity["pk"] = identity_id
        identity["fields"] = {}
        identity["fields"]["first_name"] = i_split[1]
        identity["fields"]["surname"] = i_split[2]
        identity["fields"]["mail"] = i_split[0].lower()
        identity["fields"]["gender"] = (i_split[3] == 'male')
        identity["fields"]["service"] = current_service_id
        identity["fields"]["approved"] = True
        identity["fields"]["lastapprovalremindersend"] = None
        identity["fields"]["receives_third_party_spam"] = False
        #identity["fields"]["domain"] = i_split[0].split('@')[1]
        data_to_write.append(identity)
        identity_id = identity_id + 1


# Adds a service to the data to be written.
def add_service(raw_service):
    raw_service_split = raw_service.split('\n')
    service_name = raw_service_split[0].split(' ')[0]
    service = {}
    service['model'] = 'identity.service'
    service['pk'] = service_id
    service['fields'] = {}
    service['fields']['url'] = service_name
    service['fields']['name'] = service_name
    # print(service)
    data_to_write.append(service)


# Parse all the services from the file. The functions do the lifting.
for raw_service in input_read:
    if raw_service == '':
        continue
    elif raw_service.split('\n')[1] == '':
        continue
    raw_service = raw_service.strip('\n--\n\n\n')
    service_id = service_id + 1
    add_service(raw_service)
    add_identities(raw_service, service_id)


# Write everything to the json file.
with open("transformed_maillist.json", "w") as data_file:
    json.dump(data_to_write, data_file)
