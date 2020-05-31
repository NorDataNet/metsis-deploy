try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import datetime as dt

class UserData(object):

    def __init__(self, userid):
        ''' Initiate a user info object from XML, or create new.'''

        self.userid = userid
        
        try:
            self.tree = ET.parse('user_{}.xml'.format(self.userid))
        except IOError:
            # TODO: make file for user id
            pass 

    def add_request(self, request_info):
        ''' Add information about a request to the tree.'''

        new_request_id = str(self.get_new_request_id())

        requests = self.tree.getroot().find('requests')
        new_request = ET.SubElement(requests, 'request')

        new_request.set('id', new_request_id)

        date = ET.SubElement(new_request, 'date')
        date.text = '{:%Y%m%d%H%M%S}'.format(dt.datetime.now())

        process = ET.SubElement(new_request, 'process')
        process.text = request_info['process']

    def write_to_xml(self):
        ''' Write user's request data to user's XML file.'''

        filename = 'user_{}.xml'.format(self.userid)
        # Set encoding to UTF-8 in part to trigger the xml_declaration to actually print
        self.tree.write(filename, xml_declaration=True, encoding='UTF-8')

    def get_new_request_id(self):
        ''' Return an id number (int) higher than all previous id numbers. '''

        ids = []
        for request in self.tree.iter('request'):
            ids.append(int(request.get('id')))

        return max(ids) + 1 

def send_email(receivers, body):
    """Send an email to someone."""
    import smtplib
    from email.mime.text import MIMEText
    
    sender = 'noreply@met.no'

    msg = MIMEText(body)
    msg['From'] = sender
    msg['To'] = receivers
    msg['Subject'] = 'Your file request is ready'

    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, msg.as_string())         
    except:
       print "Error: unable to send email"

# Unused for now
# Adopted from: http://pymotw.com/2/xml/etree/ElementTree/create.html
def prettify(elem):
    '''Return a pretty-printed XML string for the Element.'''

    from xml.etree import ElementTree
    from xml.dom import minidom

    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
