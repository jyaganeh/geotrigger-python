from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from geotrigger import GeotriggerClient

CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR CLIENT_SECRET'
TAG = "testing123"

def application_example():
    # Create the GeotriggerClient using a client_id and client_secret.
    # This will allow you to use the full Geotrigger API to administer your
    # application.
    print 'Creating GeotriggerClient as an application.'
    gt = GeotriggerClient(CLIENT_ID, CLIENT_SECRET)

    # Fetch a list of all triggers in this application.
    triggers = gt.request('trigger/list')

    # Print all the triggers and any tags applied to them.
    print "\nFound %d triggers:" % len(triggers['triggers'])
    for t in triggers['triggers']:
        print "- %s (%s)" % (t['triggerId'], ",".join(t['tags']))

    # Add "testing123" tag to all of the triggers that we just fetched.
    triggers_updated = gt.request('trigger/update', {
        'triggerIds': [t['triggerId'] for t in triggers['triggers']],
        'addTags': TAG
    })

    # Print the updated triggers.
    print "\nUpdated %d triggers:" % len(triggers_updated['triggers'])
    for t in triggers_updated['triggers']:
        print "- %s (%s)" % (t['triggerId'], ",".join(t['tags']))

    # Delete the "testing123" tag from the application.
    tags_deleted = gt.request('tag/delete', {'tags': TAG})
    print '\nDeleted tags: "%s"' % ", ".join(tags_deleted.keys())

if __name__ == '__main__':
    application_example()