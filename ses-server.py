# See AWS API: https://docs.aws.amazon.com/ses/latest/DeveloperGuide/query-interface-requests.html

# This stub should be able to receive Action=SendEmail calls and should store the messages as files on the file system

# There should also be an endpoint that allows the retrieval of the latest N messages

import time
import BaseHTTPServer
import os
import glob

from __builtin__ import list
from urlparse import parse_qs
from urlparse import urlparse

HOST_NAME = 'localhost' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 9555 # Maybe set this to 9000.

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

CONFIG_SET_NOT_ALLOWED_RESPONSE = """
                            <ErrorResponse xmlns="http://ses.amazonaws.com/doc/2010-12-01/">
                               <Error>
                                   <Type>Sender</Type>
                                       <Code>ConfigurationSetDoesNotExist</Code>
                                       <Message>Configuration set &lt;ConfigSet&gt; does not exist.</Message>
                               </Error>
                               <RequestId>659dd3aa-f235-11e7-8e98-893a4841b6c6</RequestId>
                            </ErrorResponse>
                       """

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_DELETE(request):
        """Respond to a DELETE request."""
        displayRawRequestDetailsOnTheConsole(request)

        parsedURL = urlparse(request.path)
        if parsedURL.path == "/deleteAllEmails":
            logInfo("Attempting to delete all emails...")

            logInfo("Fetching all emails.")
            allEmailsAsFiles = glob.glob(CACHE_FOLDER + '/*')

            logInfo("Deleting all emails.")
            emailIds=list()
            for emailAsFile in allEmailsAsFiles:
                os.remove(emailAsFile)
                emailId = os.path.splitext(os.path.basename(emailAsFile))[0]
                emailIds.append(emailId)

            if len(emailIds) == 0:
                logInfo("No emails to delete.")
            else:
                logInfo("Deleted emails: " + str(emailIds))

            sendSuccessfulResponse(request)

            logInfo("...finished deleting all emails.")

    def do_GET(request):
        """Respond to a GET request."""
        displayRawRequestDetailsOnTheConsole(request)

        parsedURL = urlparse(request.path)

        if parsedURL.path == "/mails":
            sendListOfEmailIdsToClient(request)

        if parsedURL.path == "/get/mail":
            sendEmailByIdToClient(request, parsedURL)


    def do_POST(request):
        """Respond to a POST request."""
        displayRawRequestDetailsOnTheConsole(request)

        emailRequestRawContent = convertRawHttpRequestDataToString(request)
        emailRequestContentAsDictionary = parse_qs(emailRequestRawContent)

        logDebug("You have sent this stream of data to the server (rfile - inputstream): {0}' \n"
                 .format(emailRequestContentAsDictionary))

        displayReleventEmailDetailsOnTheConsole(emailRequestContentAsDictionary)

        writeEmailReceivedToDisk(getUniqueRecordId(emailRequestContentAsDictionary), emailRequestRawContent)

        sendBackResponseToClient(request, emailRequestContentAsDictionary.get('ConfigurationSetName'))


def sendBackResponseToClient(request, configureSetsOption):
    if configureSetsOption is not None and configureSetsOption != "":
        sendFailureDueToConfigSetNotAllowed(request)
    else:
        sendSuccessfulResponse(request)
        request.wfile.write(SENT_EMAIL_RESPONSE)
        logInfo("Finished sending.")


def displayReleventEmailDetailsOnTheConsole(emailRequestContentAsDictionary):
    emailFrom = emailRequestContentAsDictionary.get('Source')
    emailTo = emailRequestContentAsDictionary.get('Destination.ToAddresses.member.1')
    emailSubject = emailRequestContentAsDictionary.get('Message.Subject.Data')
    emailBodyAsHtml = emailRequestContentAsDictionary.get('Message.Body.Html.Data')
    emailBodyAsText = emailRequestContentAsDictionary.get('Message.Body.Text.Data')

    logInfo("Email info:")
    logInfo("   from: %s" % emailFrom)
    logInfo("   to: %s" % emailTo)
    logInfo("   subject: %s" % emailSubject)
    logInfo("   body (html): %s" % emailBodyAsHtml)
    logInfo("   body (text): %s" % emailBodyAsText)


def getEmailContentFor(emailId):
    global file

    logInfo("Converting emailId to filename")
    emailFilename = "{0}/{1}{2}".format(CACHE_FOLDER, emailId, ".eml")

    try:
        file = open(emailFilename, 'r')
    except IOError as error:
        logError("Error reading file {0}: {1}".format(emailFilename, error))
        logError("Closing file and aborting...")
        file.close()

        return None
    else:
        emailContent = file.read()
        logInfo("Fetching email content from file: " + emailFilename)
        logDebug("Email contains: " + emailContent)
        file.close()
        logInfo("...finished sending email content.")
        return emailContent


def getListOfEmailIdsFromRespository():
    logInfo("Fetching all emails.")
    allEmailsAsFiles = glob.glob(CACHE_FOLDER + '/*')

    logInfo("Building list a list of emaild ids.")
    emailIds=list()
    for emailAsFile in allEmailsAsFiles:
        emailId = os.path.splitext(os.path.basename(emailAsFile))[0].strip(" ")
        emailIds.append(emailId)

    return emailIds


def sendListOfEmailIdsToClient(request):
    sendSuccessfulResponse(request)
    emailIds = getListOfEmailIdsFromRespository()
    logInfo("Sending client list of email ids " + str(emailIds))
    request.wfile.write(emailIds)
    logInfo("Finished sending.")


def sendEmailByIdToClient(request, parsedURL):
    sendSuccessfulResponse(request)
    queryString = parse_qs(parsedURL.query)
    emailId = queryString.get('emailId')[0]
    emailContent = getEmailContentFor(emailId)
    if emailContent is None:
        logInfo("No email contents sent for emailId" + emailId)
    else:
        logInfo("Sending client email contents for emailId: " + emailId)
        logDebug("Email content: " + str(emailContent))
        request.wfile.write("[{0}]".format(emailContent))
        logInfo("Finished sending.")

def writeEmailReceivedToDisk(uniqueRecordId, emailRequestContent):
    logInfo("Writing email to disk")
    logInfo("Unique record id: " + uniqueRecordId)

    emailFileName = '{0}/{1}.eml'.format(CACHE_FOLDER, uniqueRecordId)
    emailFile = open(emailFileName, 'w')
    emailFile.write(emailRequestContent)
    emailFile.close()

    logInfo("Email has been successfully saved at " + emailFileName)


def getUniqueRecordId(emailRequestContentAsDictionary):
    emailFrom = emailRequestContentAsDictionary.get('Source')
    emailTo = emailRequestContentAsDictionary.get('Destination.ToAddresses.member.1')

    newIndex = len(os.listdir(CACHE_FOLDER)) + 1
    return "{0: #04d}-{1}-{2}".format(newIndex, emailFrom[0], emailTo[0])


def displayRawRequestDetailsOnTheConsole(request):
    logDebug("Your request looks like: %s" % request)
    
    parsedURL = urlparse(request.path)
    logDebug("You accessed path: %s" % parsedURL.path)
    logDebug("You have sent this query string: %s" % parsedURL.query)
    logDebug("You have sent these headers: \n%s" % request.headers)


def convertRawHttpRequestDataToString(request):
    contentLength = int(request.headers.getheader('content-length'))
    return request.rfile.read(contentLength)


def sendSuccessfulResponse(request):
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

def logError(message):
    log("[ERROR] " + message)

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
    logInfo("Kill process using: ")
    logInfo("     $ python ses-server-wrapper.py stop")
    logInfo("In case, unsuccessful, use this to find out process id: ")
    logInfo("     $ netstat -tulpn | grep :9555")
    logInfo("...and kill it manually: ")
    logInfo("     $ kill -9 <pid>")

    try:
            httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logInfo("Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
