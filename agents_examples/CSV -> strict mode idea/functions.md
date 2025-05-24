**Other Settings:**
- Response format: `text`
- Temperature: `1.00`
- Top P: `1.00`


**Functions:**

```json
{
  "name": "identify_subscriber",
  "description": "Identifies a subscriber in the PrettyMobile system based on at least three of the following details: phone number, contract holder's name, contract holder's address, date of birth, email address, Personal Numeric Code (CNP), ID card series, client code. This ensures precise and secure identification of the customer, allowing access to specific information and services.",
  "strict": false,
  "parameters": {
    "type": "object",
    "properties": {
      "contract_holder_name": {
        "type": "string",
        "description": "The contract holder's name.",
        "optional": true
      },
      "phone_number": {
        "type": "string",
        "description": "The subscriber's phone number.",
        "optional": true
      },
      "contract_holder_address": {
        "type": "string",
        "description": "The contract holder's address.",
        "optional": true
      },
      "date_of_birth": {
        "type": "string",
        "description": "The subscriber's date of birth, in this format: `yyyy-mm-dd`.",
        "optional": true
      },
      "email_address": {
        "type": "string",
        "description": "The subscriber's email address.",
        "optional": true
      },
      "personal_id_number": {
        "type": "string",
        "description": "The subscriber's Personal Numeric Code.",
        "optional": true
      },
      "id_card_series": {
        "type": "string",
        "description": "The subscriber's ID card series.",
        "optional": true
      },
      "client_code": {
        "type": "string",
        "description": "The subscriber's unique client code.",
        "optional": true
      }
    },
    "required": []
  }
}
```

---


```json
{
  "name": "retrieve_billing_details",
  "description": "Retrieves detailed billing information for a subscriber. This function must be invoked only after the subscriber has been successfully identified using the 'identify_subscriber' function. It provides specific billing details such as total payment due, due dates, and payment status.",
  "strict": false,
  "parameters": {
    "type": "object",
    "properties": {
      "contract_holder_name": {
        "type": "string",
        "description": "The full legal name of the contract holder as registered with PrettyMobile. This name should have been verified through the 'identify_subscriber' function.",
        "optional": false
      }
    },
    "required": [
      "contract_holder_name"
    ]
  }
}
```

---


```json
{
  "name": "manage_services",
  "description": "This function manages subscriber services, including querying current services, activating, deactivating, modifying service packages, and changing service types. It supports various actions such as 'check_services' for querying current service details, 'modify_services' for changing service types or available options, 'activate_deactivate_service' for changing the status of services, and 'modify_package' for updating service packages. The function is designed to be flexible, requiring only the subscriber's name as a mandatory parameter, with other parameters depending on the specific request.",
  "strict": false,
  "parameters": {
    "type": "object",
    "properties": {
      "contract_holder_name": {
        "type": "string",
        "description": "The contract holder's name for whom the service change is requested. This is the only mandatory parameter, used to identify the subscriber's account and apply the requested changes or queries.",
        "optional": false
      },
      "action": {
        "type": "string",
        "description": "The action to be performed. Valid actions include 'check_services', 'modify_services', 'activate_deactivate_service', and 'modify_package'.",
        "optional": false
      },
      "service_type": {
        "type": "string",
        "description": "The new type of service to be managed, applicable for 'modify_services', 'activate_deactivate_service', and 'modify_package'. Valid options include 'Internet', 'TV', or 'Internet + TV'. This parameter is optional but required for specific actions other than 'check_services'.",
        "optional": true
      },
      "service_status": {
        "type": "string",
        "description": "The desired status of the service for activation or deactivation. Valid options are 'Active' for activation and 'Inactive' for deactivation. This parameter is optional and used only with the 'activate_deactivate_service' action.",
        "optional": true
      },
      "current_package": {
        "type": "string",
        "description": "The current service package. This parameter is optional and used only with the 'modify_package' action.",
        "optional": true
      },
      "new_package": {
        "type": "string",
        "description": "The new desired package for modifying an existing service package. Valid options are 'Pretty250', 'Pretty500', and 'Pretty1000'. Required only for the 'modify_package' action to change the service package.",
        "optional": true
      },
      "current_service_type": {
        "type": "string",
        "description": "The current service type that needs to be changed. Required when modifying the service type to a new one.",
        "optional": true
      }
    },
    "required": [
      "contract_holder_name",
      "action"
    ]
  }
}
```

---
