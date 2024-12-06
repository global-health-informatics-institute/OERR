import json


BASE_URL = "http://3.137.191.90:8005"
LOGIN_ENDPOINT = "/api/v1/auth/application_login"
auth_payload = {
    "username": "administrator",
    "password": "kchlims"
}
REFRESH_ENDPOINT = "/api/v1/auth/refresh_token"
TEST_TYPE_ENDPOINT = "/api/v1/test_types/"
TEST_PANEL_ENDPOINT = "/api/v1/test_panels/"
WARD_ENDPOINT = "/api/v1/facility_sections"
DEPARTMENT_ENDPOINT = "/api/v1/departments"
SPECIMEN_ENDPOINT = "/api/v1/specimen"
SYNC_RESPONSE_ENDPOINT = "/api/v1/sync"

VALID_USER = "oerr_user"
VALID_PASSWORD = "oerr"


# Load Configurations
config_file = "config/application.config"

settings = {}
with open(config_file) as json_file:
    settings = json.load(json_file)
couch_config = settings.get("couch", {})

FACILITY_SECTIONS =  {
    "UNDER 5": "27",
    "CWA": "7",
    "CWB": "3",
    "CWC": "1",
    "CW HDU": "2",

    "OPD2": "4",
    "MSS": "44",
    "4A": "19",
    "4B": "20",
    "MHDU": "56",
    "DIALYSIS UNIT": "10",


    "CASUALTY": "34",
    "1A": "12",
    "1B": "13",
    "3A": "17",
    "3B": "18",
    "SHDU": "57",
    "THEATRE": "9",


    "LABOUR": "36",
    "POSTNATAL WARD":"42",
    "ANTENATAL WARD": "64",
    "EM OPD": "35",
    "EMHDU" : "37",
    "EM NURSERY": "39",
    "GYNAE": "40",

    "ICU": "11",
    "OPD1": "60",
    "EYE WARD": "59",
    "DENTAL" : "25",
    "ENT": "61" 
}

SPECIMEN_STATUSES = {
  "specimen-not-collected" :"Specimen Received",
  "specimen-accepted" : "Specimen Received",
  "specimen-rejected" : "Rejected"
}

TEST_STATUSES = {
  "pending": "Specimen Received",
  "started": "Being Analyzed",
  "completed": "Pending Verification",
  "verified": "Analysis Complete",
  "voided": "Not Done",
  "not-done": "Not Done",
  "rejected": "Rejected"
}

TEST_PAYLOAD = {
    "id": 19,
    "order_id": 13,
    "specimen_id": 3,
    "specimen_type": "Blood",
    "test_panel_id": 4,
    "test_panel_name": "MC\u0026S",
    "created_date": "2024-12-03T09:32:43.480Z",
    "request_origin": "Out Patient",
    "requesting_ward": "7C",
    "accession_number": "KCH2400000010",
    "test_type_id": 4,
    "test_type_name": "Culture \u0026 Sensitivity",
    "tracking_number": "XKCH2400000010",
    "voided": 0,
    "requested_by": "dtr",
    "completed_by": {},
    "client": {
      "id": 6,
      "first_name": "rr",
      "middle_name": "",
      "last_name": "rr",
      "sex": "M",
      "date_of_birth": "2024-11-26",
      "birth_date_estimated": 0,
      "client_history": None
    },
    "status": "verified",
    "order_status": "specimen-accepted",
    "lab_location": {
      "id": 1,
      "name": "Main Lab"
    },
    "is_machine_oriented": False,
    "result_remarks": {
      "id": 5,
      "tests_id": 19,
      "value": None
    },
    "indicators": [
        {
            "id": 60,
            "name": "Culture",
            "test_indicator_type": "auto_complete",
            "unit": "",
            "description": "",
            "result": {
              "id": 35,
              "value": "Growth",
              "result_date": "2024-12-03T13:15:19.028Z",
              "machine_name": None
            },
            "indicator_ranges": [
                {
                    "id": 29,
                    "test_indicator_id": 60,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "POSITIVE",
                    "value": "Growth"
                },
                {
                    "id": 30,
                    "test_indicator_id": 60,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "No growth"
                },
                {
                    "id": 31,
                    "test_indicator_id": 60,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Mixed growth; no predominant organism"
                },
                {
                    "id": 32,
                    "test_indicator_id": 60,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Growth of normal flora; no pathogens isolated"
                },
                {
                    "id": 33,
                    "test_indicator_id": 60,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Growth of contaminants"
                }
            ]
        },
        {
            "id": 60,
            "name": "Love",
            "test_indicator_type": "auto_complete",
            "unit": "",
            "description": "",
            "result": {
              "id": 35,
              "value": "100",
              "result_date": "2024-12-03T13:15:19.028Z",
              "machine_name": None
            },
            "indicator_ranges": [
                {
                    "id": 29,
                    "test_indicator_id": 60,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "POSITIVE",
                    "value": "Growth"
                },
                {
                    "id": 30,
                    "test_indicator_id": 60,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "No growth"
                },
                {
                    "id": 31,
                    "test_indicator_id": 60,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Mixed growth; no predominant organism"
                },
                {
                    "id": 32,
                    "test_indicator_id": 60,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Growth of normal flora; no pathogens isolated"
                },
                {
                    "id": 33,
                    "test_indicator_id": 60,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Growth of contaminants"
                }
            ]
        },
        
        {
            "id": 450,
            "name": "Lab Tech. Name:",
            "test_indicator_type": "free_text",
            "unit": "",
            "description": "",
            "result": {},
            "indicator_ranges": []
        }
    ],
    
    "expected_turn_around_time": {
        "id": 197,
        "test_type_id": 4,
        "value": "7",
        "unit": "Days"
    },
    "status_trail": [
      {
          "id": 35,
          "test_id": 19,
          "status_id": 2,
          "created_date": "2024-12-03T09:32:43.493Z",
          "status": {
            "id": 2,
            "name": "pending"
          },
          "initiator": {
            "username": "administrator",
            "first_name": "LIMS",
            "last_name": "Administrator"
          },
          "status_reason": {}
      },
        {
            "id": 39,
            "test_id": 19,
            "status_id": 3,
            "created_date": "2024-12-03T13:14:54.290Z",
            "status": {
                "id": 3,
                "name": "started"
            },
            "initiator": {
                "username": "administrator",
                "first_name": "LIMS",
                "last_name": "Administrator"
            },
            "status_reason": {}
        },
        {
            "id": 40,
            "test_id": 19,
            "status_id": 4,
            "created_date": "2024-12-03T13:15:19.057Z",
            "status": {
                "id": 4,
                "name": "completed"
            },
            "initiator": {
                "username": "administrator",
                "first_name": "LIMS",
                "last_name": "Administrator"
            },
            "status_reason": {}
        },
        {
            "id": 41,
            "test_id": 19,
            "status_id": 5,
            "created_date": "2024-12-03T13:15:23.591Z",
            "status": {
                "id": 5,
                "name": "verified"
            },
            "initiator": {
                "username": "administrator",
                "first_name": "LIMS",
                "last_name": "Administrator"
            },
            "status_reason": {}
        }
    ],
    "order_status_trail": [
        {
            "id": 22,
            "test_id": 13,
            "status_id": 9,
            "created_date": "2024-12-03T09:32:43.375Z",
            "status": {
                "id": 9,
                "name": "specimen-not-collected"
            },
            "initiator": {
                "username": "administrator",
                "first_name": "LIMS",
                "last_name": "Administrator"
            },
            "status_reason": {}
        },
        {
            "id": 23,
            "test_id": 13,
            "status_id": 10,
            "created_date": "2024-12-03T13:14:53.559Z",
            "status": {
                "id": 10,
                "name": "specimen-accepted"
            },
            "initiator": {
                "username": "administrator",
                "first_name": "LIMS",
                "last_name": "Administrator"
            },
            "status_reason": {}
        }
    ],
    "suscept_test_result": [
        {
            "test_id": 19,
            "organism_id": 1,
            "name": "Haemophilus influenza",
            "drugs": [
                {
                    "test_id": 19,
                    "organism_id": 1,
                    "drug_id": 1,
                    "zone": "1",
                    "interpretation": "S - Sensitive",
                    "name": "Amoxicillin/Clavulanate"
                },
                {
                    "test_id": 19,
                    "organism_id": 1,
                    "drug_id": 2,
                    "zone": "2",
                    "interpretation": "R - Resistant",
                    "name": "Ampicillin"
                }
            ]
        }
    ],
    "culture_observation": [],
    "oerr_identifiers": {
      "id": 14,
      "order_id": 8,
      "test_id": 12,
      "npid": "DF5U00",
      "facility_section_id": 44,
      "requested_by": "chaliram",
      "sample_collected_time": "2024-12-02T07:04:01.000Z",
      "doc_id": "123testid",
      "test_type_id": 31
    }
}



# TEST_PAYLOAD = {
#     "id": 12,
#     "order_id": 8,
#     "specimen_id": 3,
#     "specimen_type": "Blood",
#     "test_panel_id": None,
#     "test_panel_name": None,
#     "created_date": "2024-12-02T14:12:07.998Z",
#     "request_origin": "In Patient",
#     "requesting_ward": "MSS",
#     "accession_number": "KCH2400000007",
#     "test_type_id": 31,
#     "test_type_name": "Transfusion Outcome",
#     "tracking_number": "XKCH2400000007",
#     "voided": 0,
#     "requested_by": "chaliram",
#     "completed_by": {},

#     "client": {
#         "id": 5,
#         "first_name": "Hariea",
#         "middle_name": "",
#         "last_name": "Banda",
#         "sex": "0",
#         "date_of_birth": "1985-06-16",
#         "birth_date_estimated": 0,
#         "client_history": "mass"
#     },

#     "status": "verified",
#     "order_status": "specimen-accepted",
#     "lab_location": {
#         "id": 1,
#         "name": "Main Lab"
#     },
#     "is_machine_oriented": False,
#     "result_remarks": {
#         "id": 2,
#         "tests_id": 12,
#         "value": ""
#     },
#     "indicators": [
#         {
#         "id": 132,
#         "name": "Outcome",
#         "test_indicator_type": "auto_complete",
#         "unit": "",
#         "description": "",
#         "result": {
#             "id": 2,
#             "value": "Suspected Reaction",
#             "result_date": "2024-12-03T07:13:48.430Z",
#             "machine_name": None
#         },
#         "indicator_ranges": [
#             {
#             "id": 404,
#             "test_indicator_id": 132,
#             "sex": None,
#             "min_age": None,
#             "max_age": None,
#             "lower_range": None,
#             "upper_range": None,
#             "interpretation": "",
#             "value": "No Reaction"
#             },
#             {
#             "id": 405,
#             "test_indicator_id": 132,
#             "sex": None,
#             "min_age": None,
#             "max_age": None,
#             "lower_range": None,
#             "upper_range": None,
#             "interpretation": "",
#             "value": "Suspected Reaction"
#             },
#             {
#             "id": 406,
#             "test_indicator_id": 132,
#             "sex": None,
#             "min_age": None,
#             "max_age": None,
#             "lower_range": None,
#             "upper_range": None,
#             "interpretation": "",
#             "value": "Confirmed Reaction"
#             }
#         ]
#         }
#     ],
#     "expected_turn_around_time": {
#         "id": 24,
#         "test_type_id": 31,
#         "value": "30",
#         "unit": "Minutes"
#     },
#     "status_trail": [
#         {
#         "id": 14,
#         "test_id": 12,
#         "status_id": 2,
#         "created_date": "2024-12-02T14:12:08.016Z",
#         "status": {
#             "id": 2,
#             "name": "pending"
#         },
#         "initiator": {
#             "username": "administrator",
#             "first_name": "LIMS",
#             "last_name": "Administrator"
#         },
#         "status_reason": {}
#         },
#         {
#         "id": 17,
#         "test_id": 12,
#         "status_id": 3,
#         "created_date": "2024-12-03T07:13:44.368Z",
#         "status": {
#             "id": 3,
#             "name": "started"
#         },
#         "initiator": {
#             "username": "administrator",
#             "first_name": "LIMS",
#             "last_name": "Administrator"
#         },
#         "status_reason": {}
#         },
#         {
#         "id": 18,
#         "test_id": 12,
#         "status_id": 4,
#         "created_date": "2024-12-03T07:13:48.456Z",
#         "status": {
#             "id": 4,
#             "name": "completed"
#         },
#         "initiator": {
#             "username": "administrator",
#             "first_name": "LIMS",
#             "last_name": "Administrator"
#         },
#         "status_reason": {}
#         },
#         {
#         "id": 19,
#         "test_id": 12,
#         "status_id": 5,
#         "created_date": "2024-12-03T07:13:52.200Z",
#         "status": {
#             "id": 5,
#             "name": "verified"
#         },
#         "initiator": {
#             "username": "administrator",
#             "first_name": "LIMS",
#             "last_name": "Administrator"
#         },
#         "status_reason": {}
#         }
#     ],
#     "order_status_trail": [
#         {
#         "id": 14,
#         "test_id": 8,
#         "status_id": 9,
#         "created_date": "2024-12-02T14:12:07.845Z",
#         "status": {
#             "id": 9,
#             "name": "specimen-not-collected"
#         },
#         "initiator": {
#             "username": "administrator",
#             "first_name": "LIMS",
#             "last_name": "Administrator"
#         },
#         "status_reason": {}
#         },
#         {
#         "id": 15,
#         "test_id": 8,
#         "status_id": 10,
#         "created_date": "2024-12-03T07:13:43.495Z",
#         "status": {
#             "id": 10,
#             "name": "specimen-accepted"
#         },
#         "initiator": {
#             "username": "administrator",
#             "first_name": "LIMS",
#             "last_name": "Administrator"
#         },
#         "status_reason": {}
#         }
#     ],
#     "suscept_test_result": [],
#     "culture_observation": [],
#     "oerr_identifiers": {
#       "id": 14,
#       "order_id": 8,
#       "test_id": 12,
#       "npid": "DF5U00",
#       "facility_section_id": 44,
#       "requested_by": "chaliram",
#       "sample_collected_time": "2024-12-02T07:04:01.000Z",
#       "doc_id": None,
#       "test_type_id": 31
#     }
# }



TEST_PAYLOAD = {
    "id": 25,
    "order_id": 15,
    "specimen_id": 3,
    "specimen_type": "Blood",
    "test_panel_id": None,
    "test_panel_name": None,
    "created_date": "2024-12-06T06:42:09.310Z",
    "request_origin": "In Patient",
    "requesting_ward": "MSS",
    "accession_number": "KCH2400000012",
    "test_type_id": 35,
    "test_type_name": "FBC",
    "tracking_number": "XKCH2400000012",
    "voided": 0,
    "requested_by": "maganga",
    "completed_by": {},
    "client": {
        "id": 7,
        "first_name": "Test",
        "middle_name": "",
        "last_name": "Patient",
        "sex": "F",
        "date_of_birth": "1992-07-05",
        "birth_date_estimated": 0,
        "client_history": "identical 2"
    },
    "status": "pending",
    "order_status": "specimen-not-collected",
    "lab_location": {
        "id": 1,
        "name": "Main Lab"
    },
    "is_machine_oriented": True,
    "result_remarks": None,
    "indicators": [
        {
            "id": 169,
            "name": "WBC",
            "test_indicator_type": "numeric",
            "unit": "10^3/uL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 764,
                    "test_indicator_id": 169,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "4.0",
                    "upper_range": "10.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 147,
            "name": "RBC",
            "test_indicator_type": "numeric",
            "unit": "10^6/uL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 710,
                    "test_indicator_id": 147,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "4.0",
                    "upper_range": "6.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 148,
            "name": "HGB",
            "test_indicator_type": "numeric",
            "unit": "g/dL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 714,
                    "test_indicator_id": 148,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "10.9",
                    "upper_range": "17.3",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 149,
            "name": "HCT",
            "test_indicator_type": "numeric",
            "unit": "%",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 718,
                    "test_indicator_id": 149,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "32.0",
                    "upper_range": "50.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 150,
            "name": "MCV",
            "test_indicator_type": "numeric",
            "unit": "fL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 722,
                    "test_indicator_id": 150,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "71.0",
                    "upper_range": "95.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 151,
            "name": "MCH",
            "test_indicator_type": "numeric",
            "unit": "pg",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 726,
                    "test_indicator_id": 151,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "23.0",
                    "upper_range": "34.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 152,
            "name": "MCHC",
            "test_indicator_type": "numeric",
            "unit": "g/dL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 728,
                    "test_indicator_id": 152,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "33.0",
                    "upper_range": "36.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 153,
            "name": "PLT",
            "test_indicator_type": "numeric",
            "unit": "10^3/uL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 730,
                    "test_indicator_id": 153,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "122.0",
                    "upper_range": "330.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 154,
            "name": "RDW-SD",
            "test_indicator_type": "numeric",
            "unit": "fL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 732,
                    "test_indicator_id": 154,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "37.0",
                    "upper_range": "54.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 155,
            "name": "RDW-CV",
            "test_indicator_type": "numeric",
            "unit": "%",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 734,
                    "test_indicator_id": 155,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "10.0",
                    "upper_range": "16.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 156,
            "name": "PDW",
            "test_indicator_type": "numeric",
            "unit": "fL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 736,
                    "test_indicator_id": 156,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "9.0",
                    "upper_range": "17.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 157,
            "name": "MPV",
            "test_indicator_type": "numeric",
            "unit": "fL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 738,
                    "test_indicator_id": 157,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "6.0",
                    "upper_range": "10.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 158,
            "name": "PCT",
            "test_indicator_type": "numeric",
            "unit": "%",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 740,
                    "test_indicator_id": 158,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "0.17",
                    "upper_range": "0.35",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 159,
            "name": "NEUT%",
            "test_indicator_type": "numeric",
            "unit": "%",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 742,
                    "test_indicator_id": 159,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "27.0",
                    "upper_range": "60.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 160,
            "name": "LYMPH%",
            "test_indicator_type": "numeric",
            "unit": "%",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 744,
                    "test_indicator_id": 160,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "29.0",
                    "upper_range": "59.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 161,
            "name": "MONO%",
            "test_indicator_type": "numeric",
            "unit": "%",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 748,
                    "test_indicator_id": 161,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "2.0",
                    "upper_range": "10.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 162,
            "name": "EO%",
            "test_indicator_type": "numeric",
            "unit": "%",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 750,
                    "test_indicator_id": 162,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "0.0",
                    "upper_range": "12.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 163,
            "name": "BASO%",
            "test_indicator_type": "numeric",
            "unit": "%",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 752,
                    "test_indicator_id": 163,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "0.0",
                    "upper_range": "1.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 164,
            "name": "NEUT#",
            "test_indicator_type": "numeric",
            "unit": "10^3/uL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 754,
                    "test_indicator_id": 164,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "0.82",
                    "upper_range": "4.1",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 165,
            "name": "LYMPH#",
            "test_indicator_type": "numeric",
            "unit": "10^3/uL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 756,
                    "test_indicator_id": 165,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "1.26",
                    "upper_range": "3.62",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 166,
            "name": "MONO#",
            "test_indicator_type": "numeric",
            "unit": "10^3/uL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 758,
                    "test_indicator_id": 166,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "0.12",
                    "upper_range": "0.56",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 167,
            "name": "EO#",
            "test_indicator_type": "numeric",
            "unit": "10^3/uL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 760,
                    "test_indicator_id": 167,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "0.0",
                    "upper_range": "0.78",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 168,
            "name": "BASO#",
            "test_indicator_type": "numeric",
            "unit": "10^3/uL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 762,
                    "test_indicator_id": 168,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "0.0",
                    "upper_range": "0.07",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 175,
            "name": "P-LCC",
            "test_indicator_type": "numeric",
            "unit": "10^9/L",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 770,
                    "test_indicator_id": 175,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "30.0",
                    "upper_range": "90.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 431,
            "name": "NRBC#",
            "test_indicator_type": "numeric",
            "unit": "10^3/uL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 1076,
                    "test_indicator_id": 431,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "0.21",
                    "upper_range": "0.63",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 430,
            "name": "NRBC%",
            "test_indicator_type": "numeric",
            "unit": "%",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 1074,
                    "test_indicator_id": 430,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "3.0",
                    "upper_range": "9.2",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 429,
            "name": "RET#",
            "test_indicator_type": "numeric",
            "unit": "10^6/uL",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 1072,
                    "test_indicator_id": 429,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "0.07",
                    "upper_range": "0.131",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 176,
            "name": "P-LCR",
            "test_indicator_type": "numeric",
            "unit": "%",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 772,
                    "test_indicator_id": 176,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "11.0",
                    "upper_range": "45.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 428,
            "name": "RET %",
            "test_indicator_type": "numeric",
            "unit": "%",
            "description": "",
            "result": {},
            "indicator_ranges": [
                {
                    "id": 1070,
                    "test_indicator_id": 428,
                    "sex": "Both",
                    "min_age": 0,
                    "max_age": 120,
                    "lower_range": "0.4",
                    "upper_range": "3.0",
                    "interpretation": "Normal",
                    "value": None
                }
            ]
        },
        {
            "id": 457,
            "name": "Lab Tech. Name:",
            "test_indicator_type": "free_text",
            "unit": "",
            "description": "",
            "result": {},
            "indicator_ranges": []
        }
    ],
    "expected_turn_around_time": {
        "id": 138,
        "test_type_id": 35,
        "value": "2",
        "unit": "Hours"
    },
    "status_trail": [
        {
            "id": 55,
            "test_id": 25,
            "status_id": 2,
            "created_date": "2024-12-06T06:42:09.321Z",
            "status": {
                "id": 2,
                "name": "pending"
            },
            "initiator": {
                "username": "hop",
                "first_name": "hop",
                "last_name": "hop"
            },
            "status_reason": {}
        }
    ],
    "order_status_trail": [
        {
            "id": 26,
            "test_id": 15,
            "status_id": 9,
            "created_date": "2024-12-06T06:42:09.256Z",
            "status": {
                "id": 9,
                "name": "specimen-not-collected"
            },
            "initiator": {
                "username": "hop",
                "first_name": "hop",
                "last_name": "hop"
            },
            "status_reason": {}
        }
    ],
    "suscept_test_result": [],
    "culture_observation": [],
    "oerr_identifiers": {
        "id": 15,
        "order_id": 15,
        "test_id": 25,
        "npid": "0D6UGE",
        "facility_section_id": 44,
        "requested_by": "maganga",
        "doc_id": None,
        "test_type_id": 35,
        "sample_collected_at": 1733385222
    }
}