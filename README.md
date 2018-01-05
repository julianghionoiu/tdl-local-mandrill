# tdl-local-ses

A Local SES Server Stub that stores the messages

## Running 

```bash
    $ python ses-server.py 
```

Typical output on the console looks like:

```bash
   Thu Jan  4 18:44:51 2018 [INFO] Server Starts - localhost:8080
```

After sending emails will look like:

```bash
   Thu Jan  4 18:44:51 2018 [INFO] Server Starts - localhost:8080
   127.0.0.1 - - [04/Jan/2018 18:44:58] "POST / HTTP/1.1" 200 -
   Thu Jan  4 18:44:58 2018 [INFO] You accessed path: /
   Thu Jan  4 18:44:58 2018 [DEBUG] Your request looks like: <__main__.MyHandler instance at 0x7f462bdd4b00>
   Thu Jan  4 18:44:58 2018 [INFO] You have sent these headers: 
   Host: localhost:8080
   Authorization: AWS4-HMAC-SHA256 Credential=x/20180104/eu-west-2/ses/aws4_request, SignedHeaders=amz-sdk-invocation-id;amz-sdk-retry;host;user-agent;x-amz-date, Signature=50c702afb91b465e3d08cb705d556f6b216d07961635ede3c19ac05cc8f1f1de
   X-Amz-Date: 20180104T184458Z
   User-Agent: aws-sdk-java/1.11.253 Linux/4.4.0-104-generic Java_HotSpot(TM)_64-Bit_Server_VM/25.144-b01 java/1.8.0_144
   amz-sdk-invocation-id: 9da56350-b020-e81f-0244-4727a5504a73
   amz-sdk-retry: 0/0/500
   Content-Type: application/x-www-form-urlencoded; charset=utf-8
   Content-Length: 690
   Connection: Keep-Alive
   
   Thu Jan  4 18:54:14 2018 [INFO] You have sent this stream of data to the server (rfile - inputstream): {'Message.Subject.Data': ['Amazon SES test (AWS SDK for Java)'], 'Message.Body.Html.Charset': ['UTF-8'], 'Message.Body.Text.Data': ['This email was sent through Amazon SES using the AWS SDK for Java.'], 'Message.Body.Html.Data': ["<h1>Amazon SES test (AWS SDK for Java)</h1><p>This email was sent with <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the <a href='https://aws.amazon.com/sdk-for-java/'>AWS SDK for Java</a>"], 'Message.Subject.Charset': ['UTF-8'], 'Source': ['sender@example.com'], 'Version': ['2010-12-01'], 'ConfigurationSetName': ['ConfigSet'], 'Action': ['SendEmail'], 'Message.Body.Text.Charset': ['UTF-8'], 'Destination.ToAddresses.member.1': ['recipient@example.com']}' 
   
   Thu Jan  4 18:54:14 2018 [INFO] Email info:
   Thu Jan  4 18:54:14 2018 [INFO]    from: ['sender@example.com']
   Thu Jan  4 18:54:14 2018 [INFO]    to: ['recipient@example.com']
   Thu Jan  4 18:54:14 2018 [INFO]    subject: ['Amazon SES test (AWS SDK for Java)']
   Thu Jan  4 18:54:14 2018 [INFO]    body (html): ["<h1>Amazon SES test (AWS SDK for Java)</h1><p>This email was sent with <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the <a href='https://aws.amazon.com/sdk-for-java/'>AWS SDK for Java</a>"]
   Thu Jan  4 18:54:14 2018 [INFO]    body (text): ['This email was sent through Amazon SES using the AWS SDK for Java.']
```
