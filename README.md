## Key Features

- Utilizes AWS Lambda and SAM architecture for serverless deployment.
- Interacts with an EHR service to retrieve patient data.
- Implements error handling to provide informative responses for invalid or non-existent patient IDs.
- Integrates with Slack through a custom slash command for convenient access and data retrieval.

## How to Use

### 1. Set Up Environment Variables

Configure environment variables in the CloudFormation template (`template.yaml`) for EHR service URLs, credentials, and Slack webhook URLs.

### 2. Deploy the Application

Deploy the application using the SAM CLI or AWS Management Console.

### 3. Invoke from Slack

Use the custom Slack command with the specified patient ID to trigger the Lambda function.

### 4. View Results in Slack

Receive patient information in the designated private Slack channel.

## Deployment

This project is intended to be deployed using AWS SAM. Ensure that the CloudFormation template (`template.yaml`) contains the necessary environment variable configurations. Use the SAM CLI or AWS Management Console to deploy the application.

## Environment Variables

Make sure to set the following environment variables in the CloudFormation template (`template.yaml`):

- `EHR_SERVICE_CUSTOMFIELDS_URL`
- `EHR_SERVICE_PRIMESUITE_SITE_ID`
- `EHR_SERVICE_PRIMESUITE_USER_NAME`
- `EHR_SERVICE_PRIMESUITE_USER_PASSWORD`
- `EHR_SERVICE_DESTINATION_SITE_ID`
- `EHR_SERVICE_GENERAL_PRIMESUITE_USER_ID`
- `EHR_SERVICE_DEMOGRAPHICS_URL`
- `EHR_SERVICE_DEMOGRAPHICS_PRIMESUITE_USER_ID`
- `EHR_SERVICE_PATIENT_WEBHOOK_SLACK`

## Slack Integration

To interact with the application through Slack, use the following command:

/slack-command patient_id
