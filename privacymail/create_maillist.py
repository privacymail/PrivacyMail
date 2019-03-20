# Creates a simple text file with mailadresses.
import names
import os

# Check whether file already exists and what to do.
exists = os.path.isfile('maillist.txt')
if exists:
    print ('File maillist.txt already exists.')
    response = input("Append to file? y/N: ")
    if (response != 'y'):
        response = input('Overwrite file? y/N: ')
        if (response == 'y'):
            os.remove("maillist.txt")
        else:
            print('Exiting.')
            exit(0)


createCount = input("How many mailaddress pairs should be created for each domain? ")
try:
    createCount = int(createCount)
except ValueError:
    print ('Input was not an int.\nExiting.')
    exit (1)


# Create a new line for the file, depending on the gender and the domain.
def createLine(gender, domain):
    fullName = names.get_full_name(gender=gender)
    splitName = fullName.split()
    mailaddress = splitName[0].lower() + '.' + splitName[1].lower() + '@' + domain
    return mailaddress + ' ' + fullName + ' ' + gender


domains = ['newsletterme.de', 'privacyletter.de']
f = open("maillist.txt","a+")
try:
    createCount = int(createCount)
except ValueError:
    print ('Input was not an int.\nExiting.')
    exit (1)

# Write everything to the file.
for i in range(createCount):
    f.write('##\n')
    for domain in domains:
        f.write('\n')
        newLine = createLine('male', domain)
        f.write(newLine + ' \n' )
        newLine = createLine('female', domain)
        f.write(newLine + ' \n')
    f.write('--\n\n\n')
f.close()