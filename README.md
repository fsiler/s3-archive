<!--
title: 'Serverless Framework Python SQS Producer-Consumer on AWS'
description: 'This template demonstrates how to develop and deploy a simple SQS-based producer-consumer service running on AWS Lambda using the traditional Serverless Framework.'
layout: Doc
framework: v2
platform: AWS
language: Python
priority: 2
authorLink: 'https://github.com/serverless'
authorName: 'Serverless, inc.'
authorAvatar: 'https://avatars1.githubusercontent.com/u/13742415?s=200&v=4'
-->

## S3-archive: an efficient way to deep archive smaller files
The problem with S3 is that Glacier and Glacier Deep Storage [do not play well with smaller files](https://therub.org/2015/11/18/glacier-costlier-than-s3-for-small-files/).  The idea here is to [hook](https://www.serverless.com/framework/docs/providers/aws/events/s3/) the `s3:ObjectCreated` hook or enumerate objects in S3 in order to process them into deep archive.

## Architecture
- an SQS *handler* which runs on file upload, and immediately archives files larger than THRESHOLD
- a *sweeper* which runs periodically, recursively descends into the directory tree, zips up smaller files up until they reach ARCHIVE\_SIZE, archives the zip, deletes the files, and emails EMAIL\_ADDRESS with the manifest.

## parameters (passed via environment)
- BUCKET\_NAME - self explanatory
- THRESHOLD - how big the file is before it should be uploaded bare, default 200kB.
- ARCHIVE\_SIZE - how big the archive needs to be before left in a folder, default 1MB
- EMAIL\_ADDRESS - who to email the zip archive manifests to

## Task list
- send test email
- transition a single file to Deep Glacier
- add up the sizes of all the files, and send the manifest in an email
- zip up (actually suggest txz- an xz'd tarball) a file from smaller files and archive it
- recursively descend into directory trees, either zipping up when files total >=200kB in size, or returning a reference upstream.

# Serverless Framework Python SQS Producer-Consumer on AWS

This template demonstrates how to develop and deploy a simple SQS-based producer-consumer service running on AWS Lambda using the Serverless Framework and the [Lift](https://github.com/getlift/lift) plugin. It allows to accept messages, for which computation might be time or resource intensive, and offload their processing to an asynchronous background process for a faster and more resilient system.

## Anatomy of the template

This template defines one function `producer` and one Lift construct - `jobs`. The producer function is triggered by `http` event type, accepts JSON payloads and sends it to a SQS queue for asynchronous processing. The SQS queue is created by the `jobs` queue construct of the Lift plugin. The queue is set up with a "dead-letter queue" (to receive failed messages) and a `worker` Lambda function that processes the SQS messages.

To learn more:

- about `http` event configuration options, refer to [http event docs](https://www.serverless.com/framework/docs/providers/aws/events/apigateway/)
- about the `queue` construct, refer to [the `queue` documentation in Lift](https://github.com/getlift/lift/blob/master/docs/queue.md)
- about the Lift plugin in general, refer to [the Lift project](https://github.com/getlift/lift)
- about SQS processing with AWS Lambda, please refer to the official [AWS documentation](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html)

### Deployment

This example is made to work with the Serverless Framework dashboard, which includes advanced features such as CI/CD, monitoring, metrics, etc.

In order to deploy with dashboard, you need to first login with:

```
serverless login
```

and then perform deployment with:

```
serverless deploy
```

After running deploy, you should see output similar to:

```bash
Serverless: Packaging service...
Serverless: Excluding development dependencies...
Serverless: Creating Stack...
Serverless: Checking Stack create progress...
........
Serverless: Stack create finished...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading artifacts...
Serverless: Uploading service aws-python-sqs-worker.zip file to S3 (21.44 MB)...
Serverless: Validating template...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
................................................
Serverless: Stack update finished...
Service Information
service: aws-python-sqs-worker
stage: dev
region: us-east-1
stack: aws-python-sqs-worker-dev
resources: 17
api keys:
  None
endpoints:
  POST - https://xxx.execute-api.us-east-1.amazonaws.com/dev/produce
functions:
  producer: aws-python-sqs-worker-dev-producer
  jobsWorker: aws-python-sqs-worker-dev-jobsWorker
layers:
  None
jobs:
  queueUrl: https://sqs.us-east-1.amazonaws.com/xxxx/aws-python-sqs-worker-dev-jobs
```

_Note_: In current form, after deployment, your API is public and can be invoked by anyone. For production deployments, you might want to configure an authorizer. For details on how to do that, refer to [http event docs](https://www.serverless.com/framework/docs/providers/aws/events/apigateway/).

### Invocation

After successful deployment, you can now call the created API endpoint with `POST` request to invoke `producer` function:

```bash
curl --request POST 'https://xxxxxx.execute-api.us-east-1.amazonaws.com/dev/produce' --header 'Content-Type: application/json' --data-raw '{"name": "John"}'
```

In response, you should see output similar to:

```bash
{"message": "Message accepted!"}
```

### Bundling dependencies

In case you would like to include 3rd party dependencies, you will need to use a plugin called `serverless-python-requirements`. You can set it up by running the following command:

```bash
serverless plugin install -n serverless-python-requirements
```

Running the above will automatically add `serverless-python-requirements` to `plugins` section in your `serverless.yml` file and add it as a `devDependency` to `package.json` file. The `package.json` file will be automatically created if it doesn't exist beforehand. Now you will be able to add your dependencies to `requirements.txt` file (`Pipfile` and `pyproject.toml` is also supported but requires additional configuration) and they will be automatically injected to Lambda package during build process. For more details about the plugin's configuration, please refer to [official documentation](https://github.com/UnitedIncome/serverless-python-requirements).
