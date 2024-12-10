GRAMSTAIN_TEST2 = {
    "id": 30,
    "order_id": 19,
    "specimen_id": 3,
    "specimen_type": "Blood",
    "test_panel_id": 4,
    "test_panel_name": "MC&S",
    "created_date": "2024-12-06T09:22:05.809Z",
    "request_origin": "In Patient",
    "requesting_ward": "MSS",
    "accession_number": "KCH2400000016",
    "test_type_id": 3,
    "test_type_name": "Gram Stain",
    "tracking_number": "XKCH2400000016",
    "voided": 0,
    "requested_by": "apa",
    "completed_by": {},
    "client": {
        "id": 7,
        "first_name": "Test",
        "middle_name": "",
        "last_name": "Patient",
        "sex": "F",
        "date_of_birth": "1992-07-05",
        "birth_date_estimated": 0,
        "client_history": "test 2"
    },
    "status": "verified",
    "order_status": "specimen-accepted",
    "lab_location": {
        "id": 1,
        "name": "Main Lab"
    },
    "is_machine_oriented": False,
    "result_remarks": {
        "id": 13,
        "tests_id": 30,
        "value": ""
    },
    "indicators": [
        {
            "id": 59,
            "name": "Gram",
            "test_indicator_type": "auto_complete",
            "unit": "",
            "description": "",
            "result": {
                "id": 126,
                "value": "Gram positive cocci (chains)",
                "result_date": "2024-12-06T09:46:53.280Z",
                "machine_name": None
            },
            "indicator_ranges": [
                {
                    "id": 1,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "No organism seen"
                },
                {
                    "id": 2,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram positive cocci (clusters)"
                },
                {
                    "id": 3,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram positive cocci (chains)"
                },
                {
                    "id": 4,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram positive diplococci"
                },
                {
                    "id": 5,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram positive bacilli"
                },
                {
                    "id": 6,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram positive cocco-bacilli"
                },
                {
                    "id": 7,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram negative cocci"
                },
                {
                    "id": 8,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram negative bacilli"
                },
                {
                    "id": 9,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram negative cocco-bacilli"
                },
                {
                    "id": 10,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram negative diplococci"
                },
                {
                    "id": 11,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram variable cocci"
                },
                {
                    "id": 12,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram variable  bacilli"
                },
                {
                    "id": 13,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram variable cocco-bacilli"
                },
                {
                    "id": 14,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Yeast cells seen"
                }
            ]
        }
    ],
    "expected_turn_around_time": {
        "id": 196,
        "test_type_id": 3,
        "value": "1",
        "unit": "Hours"
    },
    "status_trail": [
        {
            "id": 70,
            "test_id": 30,
            "status_id": 3,
            "created_date": "2024-12-06T09:42:39.946Z",
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
            "id": 71,
            "test_id": 30,
            "status_id": 4,
            "created_date": "2024-12-06T09:46:53.325Z",
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
            "id": 72,
            "test_id": 30,
            "status_id": 5,
            "created_date": "2024-12-06T09:47:23.422Z",
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
        },
        {
            "id": 69,
            "test_id": 30,
            "status_id": 2,
            "created_date": "2024-12-06T09:22:05.825Z",
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
            "id": 33,
            "test_id": 19,
            "status_id": 9,
            "created_date": "2024-12-06T09:22:05.635Z",
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
        },
        {
            "id": 34,
            "test_id": 19,
            "status_id": 10,
            "created_date": "2024-12-06T09:29:13.999Z",
            "status": {
                "id": 10,
                "name": "specimen-accepted"
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
        "id": 37,
        "order_id": 19,
        "test_id": 30,
        "npid": "0D6UGE",
        "facility_section_id": 44,
        "requested_by": "apa",
        "doc_id": "c422facc19a58f73985d5d9392000786",
        "test_type_id": 3,
        "sample_collected_at": 1733384963,
        "is_panel": True
    }
}


GRAMSTAIN_TEST1 = {
    "id": 30,
    "order_id": 19,
    "specimen_id": 3,
    "specimen_type": "Blood",
    "test_panel_id": 4,
    "test_panel_name": "MC&S",
    "created_date": "2024-12-06T09:22:05.809Z",
    "request_origin": "In Patient",
    "requesting_ward": "MSS",
    "accession_number": "KCH2400000016",
    "test_type_id": 3,
    "test_type_name": "Gram Stain",
    "tracking_number": "XKCH2400000016",
    "voided": 0,
    "requested_by": "apa",
    "completed_by": {},
    "client": {
        "id": 7,
        "first_name": "Test",
        "middle_name": "",
        "last_name": "Patient",
        "sex": "F",
        "date_of_birth": "1992-07-05",
        "birth_date_estimated": 0,
        "client_history": "test 2"
    },
    "status": "Analysis Complete",
    "order_status": "specimen-accepted",
    "lab_location": {
        "id": 1,
        "name": "Main Lab"
    },
    "is_machine_oriented": False,
    "result_remarks": {
        "id": 13,
        "tests_id": 30,
        "value": ""
    },
    "indicators": [
        {
            "id": 59,
            "name": "Gram",
            "test_indicator_type": "auto_complete",
            "unit": "",
            "description": "",
            "result": {
                "id": 126,
                "value": "Gram positive cocci (chains)",
                "result_date": "2024-12-06T09:46:53.280Z",
                "machine_name": None
            },
            "indicator_ranges": [
                {
                    "id": 1,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "No organism seen"
                },
                {
                    "id": 2,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram positive cocci (clusters)"
                },
                {
                    "id": 3,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram positive cocci (chains)"
                },
                {
                    "id": 4,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram positive diplococci"
                },
                {
                    "id": 5,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram positive bacilli"
                },
                {
                    "id": 6,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram positive cocco-bacilli"
                },
                {
                    "id": 7,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram negative cocci"
                },
                {
                    "id": 8,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram negative bacilli"
                },
                {
                    "id": 9,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram negative cocco-bacilli"
                },
                {
                    "id": 10,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram negative diplococci"
                },
                {
                    "id": 11,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram variable cocci"
                },
                {
                    "id": 12,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram variable  bacilli"
                },
                {
                    "id": 13,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Gram variable cocco-bacilli"
                },
                {
                    "id": 14,
                    "test_indicator_id": 59,
                    "sex": None,
                    "min_age": None,
                    "max_age": None,
                    "lower_range": None,
                    "upper_range": None,
                    "interpretation": "",
                    "value": "Yeast cells seen"
                }
            ]
        }
    ],
    "expected_turn_around_time": {
        "id": 196,
        "test_type_id": 3,
        "value": "1",
        "unit": "Hours"
    },
    "status_trail": [
        {
            "id": 70,
            "test_id": 30,
            "status_id": 3,
            "created_date": "2024-12-06T09:42:39.946Z",
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
            "id": 71,
            "test_id": 30,
            "status_id": 4,
            "created_date": "2024-12-06T09:46:53.325Z",
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
            "id": 72,
            "test_id": 30,
            "status_id": 5,
            "created_date": "2024-12-06T09:47:23.422Z",
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
        },
        {
            "id": 69,
            "test_id": 30,
            "status_id": 2,
            "created_date": "2024-12-06T09:22:05.825Z",
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
            "id": 33,
            "test_id": 19,
            "status_id": 9,
            "created_date": "2024-12-06T09:22:05.635Z",
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
        },
        {
            "id": 34,
            "test_id": 19,
            "status_id": 10,
            "created_date": "2024-12-06T09:29:13.999Z",
            "status": {
                "id": 10,
                "name": "specimen-accepted"
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
        "id": 37,
        "order_id": 19,
        "test_id": 30,
        "npid": "0D6UGE",
        "facility_section_id": 44,
        "requested_by": "apa",
        "doc_id": "c422facc19a58f73985d5d9392000786",
        "test_type_id": 3,
        "sample_collected_at": 1733384963,
        "is_panel": True
    }
}