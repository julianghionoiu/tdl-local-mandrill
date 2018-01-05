# See AWS API: https://docs.aws.amazon.com/ses/latest/DeveloperGuide/query-interface-requests.html

# This stub should be able to receive Action=SendEmail calls and should store the messages as files on the file system

# There should also be an endpoint that allows the retrieval of the latest N messages

import time
import BaseHTTPServer
import os
from urlparse import parse_qs

HOST_NAME = 'localhost' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8080 # Maybe set this to 9000.

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
CACHE_FOLDER = os.path.join(SCRIPT_FOLDER, ".emailRepository")

SENT_EMAIL_RESPONSE = """
                        <SendEmailResponse xmlns='https://email.amazonaws.com/doc/2010-03-31/'>
                           <SendEmailResult>
                               <MessageId>000001271b15238a-fd3ae762-2563-11df-8cd4-6d4e828a9ae8-000000</MessageId>
                           </SendEmailResult>
                           <ResponseMetadata>
                               <RequestId>fd3ae762-2563-11df-8cd4-6d4e828a9ae8</RequestId>
                           </ResponseMetadata>
                        </SendEmailResponse>
                      """

CONFIG_SET_NOT_ALLOWED_RESPONSE = """<ErrorResponse xmlns="http://ses.amazonaws.com/doc/2010-12-01/">
           <Error>
               <Type>Sender</Type>
                   <Code>ConfigurationSetDoesNotExist</Code>
                   <Message>Configuration set &lt;ConfigSet&gt; does not exist.</Message>
           </Error>
           <RequestId>659dd3aa-f235-11e7-8e98-893a4841b6c6</RequestId>
       </ErrorResponse>"""

# Delete all emails API
# Retrieve all emails API = list of emails/names of files (name of file = email id)
# Retrieve content of email by email id

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_POST(request):
        """Respond to a POST request."""
        # If someone went to "http://something.somewhere.net/foo/bar/",#
        # then s.path equals "/foo/bar/".
        logInfo("You accessed path: %s" % request.path)
        logDebug("Your request looks like: %s" % request)
        logDebug("You have sent these headers: \n %s" % request.headers)
        emailRequestContent = convertRawHttpRequestDataToString(request)
        emailRequestContentAsDictionary = parse_qs(emailRequestContent)
        logDebug("You have sent this stream of data to the server (rfile - inputstream): {0}' \n".format(emailRequestContentAsDictionary))

        emailFrom = emailRequestContentAsDictionary.get('Source')
        emailTo = emailRequestContentAsDictionary.get('Destination.ToAddresses.member.1')
        emailSubject = emailRequestContentAsDictionary.get('Message.Subject.Data')
        emailBodyAsHtml = emailRequestContentAsDictionary.get('Message.Body.Html.Data')
        emailBodyAsText = emailRequestContentAsDictionary.get('Message.Body.Text.Data')
        configureSetsOption = emailRequestContentAsDictionary.get('ConfigurationSetName')

        logInfo("Email info:")
        logInfo("   from: %s" % emailFrom)
        logInfo("   to: %s" % emailTo)
        logInfo("   subject: %s" % emailSubject)
        logInfo("   body (html): %s" % emailBodyAsHtml)
        logInfo("   body (text): %s" % emailBodyAsText)

        if configureSetsOption is not None and configureSetsOption != "":
            sendFailureDueToConfigSetNotAllowed(request)
        else:
            sendSuccessEmailSentResponse(request)
            request.wfile.write(SENT_EMAIL_RESPONSE)

def convertRawHttpRequestDataToString(request):
    contentLength = int(request.headers.getheader('content-length'))
    return request.rfile.read(contentLength)

def sendSuccessEmailSentResponse(request):
    request.send_response(200)
    request.send_header('Content-type', 'text/xml')
    request.end_headers()

def sendFailureDueToConfigSetNotAllowed(request):
    request.send_response(400)
    request.send_header('Content-type', 'text/xml')
    request.send_header('x-amzn-RequestId', '707ad34a-f237-11e7-8d01-bd95e22571c1')
    request.send_header('Content-Length', '310')
    request.end_headers()

    request.wfile.write(CONFIG_SET_NOT_ALLOWED_RESPONSE)

def logDebug(message):
    log("[DEBUG] " + message)

def logInfo(message):
    log("[INFO] " + message)

def log(message):
    print time.asctime(), message

if __name__ == '__main__':
    if not os.path.exists(CACHE_FOLDER):
        os.mkdir(CACHE_FOLDER)

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    logInfo("Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
            httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logInfo("Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
