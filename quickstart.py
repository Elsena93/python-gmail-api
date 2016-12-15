# Created:
#   2016-12-14
# Author:
#   Chris Brown
# Based on examples from:
#   https://developers.google.com/gmail/api/
# Google API test harness:
#   https://developers.google.com/apis-explorer/?hl=en_GB#p/gmail/v1/


from __future__ import print_function

import base64
import email.mime.text
import mimetypes
import os
import httplib2
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.discovery import build
import urllib.parse

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    # use the --noauth_local_webserver flag so that user can enter credentials manually instead
    # of being redirected to a website in the browser
    flags.noauth_local_webserver=True
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = ['https://mail.google.com/',
          'https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.send']
CLIENT_SECRET_FILE = 'conf/gmail_api_client_secret.json'
APPLICATION_NAME = 'Server Admin'

class SendGmail:

    def __init__(self):
        pass

    def sendgmail(self):
        pass

    def __get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'gmail-api-server-admin.json')
        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def __create_message(self, sender, to, subject, message_text):
      """Create a message for an email.

      Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

      Returns:
        An object containing a base64url encoded email object.
      """
      message = email.mime.text.MIMEText(message_text, 'plain', 'utf-8')
      message['to'] = to
      message['from'] = sender
      message['subject'] = subject
      encoded_message = {'raw': base64.urlsafe_b64encode(message.as_bytes())}
      return encoded_message

    def __create_message_with_attachment(self, sender, to, subject, message_text, file):
      """Create a message for an email.

      Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        file: The path to the file to be attached.

      Returns:
        An object containing a base64url encoded email object.
      """
      message = email.mime.multipart.MIMEMultipart()
      message['to'] = to
      message['from'] = sender
      message['subject'] = subject

      msg = email.mime.text.MIMEText(message_text)
      message.attach(msg)

      content_type, encoding = mimetypes.guess_type(file)

      if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
      main_type, sub_type = content_type.split('/', 1)
      if main_type == 'text':
        fp = open(file, 'rb')
        msg = email.mime.text.MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
      elif main_type == 'image':
        fp = open(file, 'rb')
        msg = email.mime.image.MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
      elif main_type == 'audio':
        fp = open(file, 'rb')
        msg = email.mime.audio.MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
      else:
        fp = open(file, 'rb')
        msg = email.mime.base.MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
      filename = os.path.basename(file)
      msg.add_header('Content-Disposition', 'attachment', filename=filename)
      message.attach(msg)

      return {'raw': base64.urlsafe_b64encode(message.as_string())}

    def __send_message(self, service, user_id, message):
      """Send an email message.

      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

      Returns:
        Sent Message.
      """

      message = (service.users().messages().send(userId=user_id, body=message)
                .execute())
      print('Message Id: %s' % message['id'])
      return message

    def __build_service(self, credentials):
        """Build a Gmail service object.
        Args:
            credentials: OAuth 2.0 credentials.
        Returns:
            Gmail service object.
        """
        http = httplib2.Http()
        http = credentials.authorize(http)
        return build('gmail', 'v1', http=http)

    def main(self):
        print('Sending test message')
        message = self.__create_message('chrisbrown79@gmail.com', 'chrisbrown79@gmail.com', 'Test', 'This is a test message')
        print('Test message: ', message)
        credentials = self.__get_credentials()
        print('Credentials: ', credentials)
        service = self.__build_service(credentials)
        print('Service: ', service)
        raw = message['raw']
        print('raw: ', raw)
        raw_decoded = raw.decode("utf-8")
        print('raw decoded: ', raw_decoded)
        message = {'raw': raw_decoded}
        self.__send_message(service, 'me', message)

if __name__ == '__main__':
    SendGmail().main()

