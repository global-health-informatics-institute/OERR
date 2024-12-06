oerr_payload = json{
  "id": 12,
  "order_id": 8,
  "specimen_id": 3,
  "specimen_type": "Blood",
  "test_panel_id": null,
  "test_panel_name": null,
  "created_date": "2024-12-02T14:12:07.998Z",
  "request_origin": "In Patient",
  "requesting_ward": "MSS",
  "accession_number": "KCH2400000007",
  "test_type_id": 31,
  "test_type_name": "Transfusion Outcome",
  "tracking_number": "XKCH2400000007",
  "voided": 0,
  "requested_by": "chaliram",
  "completed_by": {},
  "client": {
    "id": 5,
    "first_name": "Hariea",
    "middle_name": "",
    "last_name": "Banda",
    "sex": "0",
    "date_of_birth": "1985-06-16",
    "birth_date_estimated": 0,
    "client_history": "mass"
  },
  "status": "verified",
  "order_status": "specimen-accepted",
  "lab_location": {
    "id": 1,
    "name": "Main Lab"
  },
  "is_machine_oriented": false,
  "result_remarks": {
    "id": 2,
    "tests_id": 12,
    "value": ""
  },
  "indicators": [
    {
      "id": 132,
      "name": "Outcome",
      "test_indicator_type": "auto_complete",
      "unit": "",
      "description": "",
      "result": {
        "id": 2,
        "value": "Suspected Reaction",
        "result_date": "2024-12-03T07:13:48.430Z",
        "machine_name": null
      },
      "indicator_ranges": [
        {
          "id": 404,
          "test_indicator_id": 132,
          "sex": null,
          "min_age": null,
          "max_age": null,
          "lower_range": null,
          "upper_range": null,
          "interpretation": "",
          "value": "No Reaction"
        },
        {
          "id": 405,
          "test_indicator_id": 132,
          "sex": null,
          "min_age": null,
          "max_age": null,
          "lower_range": null,
          "upper_range": null,
          "interpretation": "",
          "value": "Suspected Reaction"
        },
        {
          "id": 406,
          "test_indicator_id": 132,
          "sex": null,
          "min_age": null,
          "max_age": null,
          "lower_range": null,
          "upper_range": null,
          "interpretation": "",
          "value": "Confirmed Reaction"
        }
      ]
    }
  ],
  "expected_turn_around_time": {
    "id": 24,
    "test_type_id": 31,
    "value": "30",
    "unit": "Minutes"
  },
  "status_trail": [
    {
      "id": 14,
      "test_id": 12,
      "status_id": 2,
      "created_date": "2024-12-02T14:12:08.016Z",
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
      "id": 17,
      "test_id": 12,
      "status_id": 3,
      "created_date": "2024-12-03T07:13:44.368Z",
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
      "id": 18,
      "test_id": 12,
      "status_id": 4,
      "created_date": "2024-12-03T07:13:48.456Z",
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
      "id": 19,
      "test_id": 12,
      "status_id": 5,
      "created_date": "2024-12-03T07:13:52.200Z",
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
      "id": 14,
      "test_id": 8,
      "status_id": 9,
      "created_date": "2024-12-02T14:12:07.845Z",
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
      "id": 15,
      "test_id": 8,
      "status_id": 10,
      "created_date": "2024-12-03T07:13:43.495Z",
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
  "suscept_test_result": [],
  "culture_observation": [],
  "oerr_identifiers": {
    "id": 14,
    "order_id": 8,
    "test_id": 12,
    "npid": "DF5U00",
    "facility_section_id": 44,
    "requested_by": "chaliram",
    "sample_collected_time": "2024-12-02T07:04:01.000Z",
   "doc_id": ""
  }
}