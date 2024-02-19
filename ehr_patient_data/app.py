import json
import urllib.request
import os
from urllib.parse import parse_qs, unquote

def get_patient_data(patient_id):
    customfields_url = os.environ["EHR_SERVICE_CUSTOMFIELDS_URL" ]
    customfields_request_body = {
        "Credentials": {
            "PrimeSuiteCredential": {
                "PrimeSuiteSiteId": os.environ["EHR_SERVICE_PRIMESUITE_SITE_ID"],
                "PrimeSuiteUserAlias": "",
                "PrimeSuiteUserName": os.environ["EHR_SERVICE_PRIMESUITE_USER_NAME"], 
                "PrimeSuiteUserPassword": os.environ["EHR_SERVICE_PRIMESUITE_USER_PASSWORD"] 
            },
            "VendorCredential": {
                "VendorLogin": "",
                "VendorPassword": ""
            }
        },
        "Header": {
            "DestinationSiteID": os.environ["EHR_SERVICE_DESTINATION_SITE_ID"], 
            "PrimeSuiteUserID": os.environ["EHR_SERVICE_GENERAL_PRIMESUITE_USER_ID"],
            "SourceSiteID": ""
        },
        "PatientID": patient_id
    }

    insurance_url = os.environ["EHR_SERVICE_DEMOGRAPHICS_URL"] 
    insurance_request_body = {
        "Credentials": {
            "PrimeSuiteCredential": {
                "PrimeSuiteSiteId": os.environ["EHR_SERVICE_PRIMESUITE_SITE_ID"],
                "PrimeSuiteUserAlias": "",
                "PrimeSuiteUserName": os.environ["EHR_SERVICE_PRIMESUITE_USER_NAME"],
                "PrimeSuiteUserPassword": os.environ["EHR_SERVICE_PRIMESUITE_USER_PASSWORD"]
            },
            "VendorCredential": {
                "VendorLogin": "",
                "VendorPassword": ""
            }
        },
        "Header": {
            "DestinationSiteID": os.environ["EHR_SERVICE_DESTINATION_SITE_ID"],
            "PrimeSuiteUserID": os.environ["EHR_SERVICE_DEMOGRAPHICS_PRIMESUITE_USER_ID"],
            "SourceSiteID": ""
        },
        "PatientId": patient_id
    }
    
    headers = {
        "Content-Type": "application/json",
    }
    
    customfields_request = urllib.request.Request(
        customfields_url,
        data=json.dumps(customfields_request_body).encode('utf-8'),
        headers=headers
    )
    
    insurance_request = urllib.request.Request(
        insurance_url,
        data=json.dumps(insurance_request_body).encode('utf-8'),
        headers=headers
    )
    
    customfields_response = urllib.request.urlopen(customfields_request)
    customfields_content = customfields_response.read().decode('utf-8')
    customfields_data = json.loads(customfields_content)
    
    insurance_response = urllib.request.urlopen(insurance_request)
    insurance_content = insurance_response.read().decode('utf-8')
    insurance_data = json.loads(insurance_content)

    patient_full_name = customfields_data['Patient']['FullName']
    patient_pharmacy_name = customfields_data['Patient']['PharmacyName']

    output = f"Patient ID: {patient_id}\nPatient Full Name: {patient_full_name}\nPharmacy Name: {patient_pharmacy_name}\n"

    for field in customfields_data.get('CustomFields', []):
        field_description = field.get('Description')
        field_value = field.get('FieldValue')
        if field_description in ['Emergency Contact', 'Responsible Party']:
            output += f"{field_description}: {field_value}\n"
    
    if insurance_data:
        for idx, insurance in enumerate(insurance_data['Insurance'], start=1):
            insurance_name = insurance["InsurancePlan"]["InsuranceName"]
            policy_number = insurance["PolicyNumber"]
            policy_holder = insurance["PolicyHolder"]["FullName"]
            output += f"Insurance {idx}: {insurance_name}, {policy_number}, {policy_holder}\n"
    else:
        output += "No insurance information found for the patient."
    return output

def lambda_handler(event, context):
    # Decode the base64-encoded body content
    event_body = event['body']
    decoded_body = unquote(event_body)
    
    # Print the decoded content for debugging
    print("Decoded Body:")
    print(decoded_body)
    # Parse the URL-encoded data into a dictionary
    parsed_data = parse_qs(decoded_body)
    
    # Extract the relevant values from the parsed data
    user_id = parsed_data["user_id"][0]
    team_id = parsed_data['team_id'][0] #Not actually used in the output
    user_name = parsed_data['user_name'][0] #Not actually used in the output
    patient_id = parsed_data['text'][0] 
    
    hdr = {
        'Content-Type': 'application/json; charset=utf-8'
    }

    try:
        # Check if the patient ID is a valid integer
        patient_id = int(patient_id)
        
        # Call the get_patient_data function to get patient information
        patient_data_output = get_patient_data(patient_id)
        
        # Add the additional line
        additional_line = f"Here's your request <@{user_id}> !\n"
        
        # Combine the additional line and patient data into the message
        message = additional_line + patient_data_output
        
        req = urllib.request.Request(
            os.environ["EHR_SERVICE_PATIENT_WEBHOOK_SLACK"],
            json.dumps({"text": message}).encode('utf-8'),
            hdr
        )
    
        slack_response = urllib.request.urlopen(req)
        slack_response_content = slack_response.read().decode('utf-8')
        
        return {
            'statusCode': 200,
        }
        
    except ValueError:
        # Handle the case where the 'patient_id' parameter is not a valid integer
        error_message = f"<@{user_id}> please provide a valid patient ID. Your request '{patient_id}' is not a valid ID."
        req = urllib.request.Request(
            os.environ["EHR_SERVICE_PATIENT_WEBHOOK_SLACK"],
            json.dumps({"text": error_message}).encode('utf-8'),
            hdr
        )
        slack_response = urllib.request.urlopen(req)
        slack_response_content = slack_response.read().decode('utf-8')
        
        return {
            'statusCode': 400,
            'body': json.dumps(slack_response_content)
        }

    except Exception as e:
        # Handle other exceptions (e.g., network error, unexpected errors)
        error_message = f"<@{user_id}>, {str(e)}, this patient id probably does not exist"
        print(f"Error: {e}")
        req = urllib.request.Request(
            os.environ["EHR_SERVICE_PATIENT_WEBHOOK_SLACK"],
            json.dumps({"text": error_message}).encode('utf-8'),
            hdr
        )
        slack_response = urllib.request.urlopen(req)
        slack_response_content = slack_response.read().decode('utf-8')
        
        return {
            'statusCode': 500,
            'body': json.dumps(slack_response_content)
        }    
