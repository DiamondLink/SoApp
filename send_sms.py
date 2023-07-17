import ovh

client = ovh.Client(
    endpoint='ovh-eu',               # Endpoint of API OVH Europe (List of available endpoints)
    application_key='90d62556831e52e8',  # Your application key
    application_secret='8ad3696c8502e04ddb47cf5e7ee741ac',  # Your application secret key
    consumer_key='63d2872b2bb62af0f7e02f277990943c',  # Your consumer key
)


def send(content, receivers):
# Specify the SMS service you're using and the content of the message
    sms_service = 'sms-ps662103-1'


# Create a dictionary to hold the parameters
    params = {
        'message': content, 
        'charset': 'UTF-8',
        'class': 'flash',
        'coding': '7bit',
        'priority': 'high',
        'sender' : 'S O AUTOS',
        'receivers': receivers, # The receiver's phone number
        'senderForResponse': False,    # The sender will be chosen according to available senders and a random selection
        'noStopClause': True  # Add this line
    }

# Create a new job to send a message
    result = client.post('/sms/' + sms_service + '/jobs', **params)

    print(result)  # Print the API response
