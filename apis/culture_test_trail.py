CULTURE_TEST_PAYLOAD = {
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
      "requested_by": "apa",
      "sample_collected_time": 1733384963,
      "doc_id": "c422facc19a58f73985d5d9392000786",
      "test_type_id": 4,
    "is_panel": True
    }
}

