# Written by Timothy Mtonga
# This is the main thread for the application
# !/usr/bin/python

import json
import os
import random
import re
from datetime import datetime
from couchdb import Server
from flask import Flask, render_template, redirect, session, flash, request, url_for, Response, send_file
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from models.laboratory_test_panel import LaboratoryTestPanel
from models.laboratory_test_type import LaboratoryTestType
from models.patient import Patient
from models.user import User
from utils import misc

app = Flask(__name__, template_folder="views", static_folder="assets")
app.secret_key = os.urandom(25)

# Generate hashed password
# password = "thatgirl"
# hashed_password = generate_password_hash(password)
# print(hashed_password)

# Main application configuration
global db
settings = misc.initialize_settings()

# optional configuration when running on rpi
if settings["using_rpi"] == "True":
    from utils.led_control import led_control
    from utils.charging_checker import CheckChargeState
    from utils.voltage_checker import CheckVoltage


# Root page of application
@app.route("/")
def index():
    # Turn on LEDs for QR-Scanning
    if settings["using_rpi"] == "True" and request.path != "/get_charge_state":
        if request.path == "/":
            led_control().turn_led_on()
        else:
            led_control().turn_led_off()

    records = []
    my_team_recs = []

    # Based on role, pull the required information from the database
    if session["user"]["role"] in ['Nurse','Doctor','Student']:
        main_index_query = {
            "selector": {
                "ward": session.get('location'),
                "status": {"$in": ["Ordered", "Specimen Collected", "Analysis Complete", "Rejected"]}
            }, "limit": 100
        }
    else:
        main_index_query = {
            "selector": {
                "ordered_by": session["user"]['username'],
                "status": {"$in": ["Ordered", "Specimen Collected", "Analysis Complete", "Rejected"]}
            }, "limit": 100
        }
        '''
        # Get my team members and then all tests requested by members of my team
        my_team = User.get_team_members(session.get('user').get('team'))

        # Get all records for my team that require attention
        team_records_query = {
            "selector": {
                "ordered_by": {"$in": my_team},
                "status": {"$in": ["Ordered", "Specimen Collected", "Analysis Complete", "Rejected"]}
            }, "limit": 100
        }
        team_query_results = db.find(team_records_query)
        for item in team_query_results:
            team_test_detail = {'status': item.get('status'), 'date': float(item.get('date_ordered')),
                                'name': Patient.get(item.get('patient_id')).get('name').title(),
                                'ordered_by': User.get(item.get("ordered_by")).name.title(),
                                'ordered_on': datetime.fromtimestamp(float(item.get('date_ordered'))).strftime(
                                    '%d %b %Y %H:%S'),
                                "id": item["_id"], 'patient_id': item.get('patient_id')}

            if item.get("type") == "test":
                team_test_detail['test'] = LaboratoryTestType.find_by_test_type(item.get('test_type')).test_name
            else:
                team_test_detail['test'] = item.get('panel_type')
            my_team_recs.append(team_test_detail)
    '''
    # query for records to display on the main page
    main_results = db.find(main_index_query)
    for item in main_results:
        try:
            test_detail = {'status': item.get('status'), "date": float(item.get('date_ordered')),
                           'name': Patient.get(item.get('patient_id')).get('name').title(),
                           'ordered_on': datetime.fromtimestamp(float(item.get('date_ordered'))).strftime(
                               '%d %b %Y %H:%M'),
                           "id": item["_id"], 'patient_id': item.get('patient_id')}

            if item.get("type") == "test":
                test_detail['test'] = LaboratoryTestType.find_by_test_type(item.get('test_type')).test_name
            else:
                test_detail['test'] = item.get('panel_type')
            records.append(test_detail)
        except:
            pass

    # sort by date descending
    records = sorted(records, key=lambda e: e["date"], reverse=True)
    # my_team_recs = sorted(my_team_recs, key=lambda e: e["date"], reverse=True)
    return render_template('main/index.html', orders=records, current_facility=misc.current_facility())

# process barcode from the main index page
@app.route("/process_barcode", methods=["POST"])
def barcode():
    # write function to handle different types of barcodes that we expect
    barcode_segments = request.form['barcode'].split("~")
    # Case where a 1D barcode has been scanned
    if len(barcode_segments) == 1:
        var_patient = Patient.get(barcode_segments[0].strip())
        if var_patient is None:
            flash("No patient with this record", 'error')
            return redirect(url_for("index"))
        else:
            return redirect(url_for('patient', patient_id=barcode_segments[0].strip()))

    elif len(barcode_segments) == 5:
        # This section is for the npid qr code
        npid = barcode_segments[1].strip()
        var_patient = Patient.get(npid)
        print(var_patient)
        if var_patient is None:

            # Checking different date Format
            if barcode_segments[2].find('-') != -1:
                barcode_segments[2] = datetime.strptime(barcode_segments[2], '%Y-%m-%d').strftime('%d/%b/%Y')

            dob_format = "%d/%b/%Y"
            if "??" == barcode_segments[2].split("/")[0] and "???" == barcode_segments[2].split("/")[1]:
                dob_format = "??/???/%Y"
            elif "??" == barcode_segments[2].split("/")[0] and "???" != barcode_segments[2].split("/")[1]:
                dob_format = "??/%b/%Y"
            elif "??" != barcode_segments[2].split("/")[0] and "???" == barcode_segments[2].split("/")[1]:
                dob_format = "%d/???/%Y"

            var_patient = Patient(npid, barcode_segments[0].replace(npid, ""),
                                  datetime.strptime(barcode_segments[2], dob_format).strftime("%d-%m-%Y"),
                                  barcode_segments[3])
            var_patient.save()
            flash("New patient record created", 'success')
            return redirect(url_for('patient', patient_id=npid))

        else:
            # Extract and store the new name from the QR code
            updated_name = barcode_segments[0].replace(npid, "").strip()

            # Update patient name if it differs
            if var_patient['name'] != updated_name:
                var_patient['name'] = updated_name

                # Keep existing DOB and gender
                var_patient['dob'] = var_patient['dob']

                var_patient['gender'] = var_patient['gender']

                # Save updated patient using Patient object
                patient_obj = Patient(

                    npid=var_patient['id'],

                    name=var_patient['name'],

                    dob=var_patient['dob'],

                    gender=var_patient['gender'],

                    archived=var_patient.get('archived', False),

                    rev=var_patient.get('_rev', '')

                )

                patient_obj.save()

                flash("Patient record updated", 'success')

            return redirect(url_for('patient', patient_id=npid))
    else:
            flash("Wrong format for patient identifier. Please use the National patient Identifier", "error")
            return redirect(url_for("index"))


###### PATIENT ROUTES ##########
@app.route("/patient/<patient_id>", methods=['GET'])
def patient(patient_id):
    # Turn off LEDs
    if settings["using_rpi"] == "True":
        led_control().turn_led_off()

    draw_sample = False
    pending_sample = []
    records = []
    details_of_test = {}
    grouped_samples = {}
    if request.args.get("sample_draw") == "True":
        draw_sample = True

    # get patient details and arrange them in a way that is needed
    var_patient = Patient.get(patient_id)

    # get tests for patient
    test_query_result = db.find({"selector": {"patient_id": patient_id}, "limit": 100})
    for test in test_query_result:
        record = {"date_ordered": datetime.fromtimestamp(float(test["date_ordered"])).strftime('%d %b %Y %H:%M'),
                  "id": test.get("_id"), "type": test.get("type"), "status": test.get("status"),
                  "priority": test.get("Priority"), "date": float(test["date_ordered"]),
                  "collection_id": test.get("collection_id", ""), "history": test.get("clinical_history"),
                  "ordered_by": test.get("ordered_by"), "rejection_reason": test.get("rejection_reason"),
                  "test_type": "test" if test.get("type") == "test" else "test panel"}

        if test.get('panel_type') is not None:
            record["test_name"] = test.get('panel_type')
            record["panel_test_details"] = get_panel_details(test)
            if test["status"] == "Ordered":
                pending_sample.append(get_pending_panel_details(test))
        else:
            detail = LaboratoryTestType.find_by_test_type(test.get('test_type'))
            record["test_name"] = detail.test_name
            record["measures"] = get_test_measures(test, detail)
            if test["status"] == "Ordered":
                pending_details = get_pending_test_details(test, detail)
                # pending_sample.append( get_pending_test_details(test, detail))

                # Group tests by department, container
                group_key = (pending_details["department"], pending_details["container"])
                grouped_samples.setdefault(group_key, []).append(pending_details)

            elif test["status"] == "Analysis Complete" or test["status"] == "Reviewed":
                get_test_measures(test, detail)

        records.append(record)

    for group, samples in grouped_samples.items():
        if len(samples) > 1:
            test_names = ", ".join([sample["test_name"] for sample in samples])
            samples[0]["test_name"] = test_names
            test_ids = "^".join([sample["test_id"] for sample in samples])
            samples[0]["test_id"] = test_ids  # Store concatenated IDs

            pending_sample.append(samples[0])
        else:
            samples[0]["test_id"] = str(samples[0]["test_id"])  # Single test case
            pending_sample.append(samples[0])
            # For single tests, use the existing ID as the grouped ID


    records = sorted(records, key=lambda e: e["date"], reverse=True)
    permitted_length = 85 - 50 - len(var_patient['name']) - len(var_patient['id'])
    # print(f"Permitted length: {permitted_length}")  # Debugging line

    return render_template('patient/show.html', pt_details=var_patient, tests=records, pending_orders=pending_sample,
                           containers=misc.container_options(),
                           collect_samples=draw_sample, doctors=prescribers(), ch_length=permitted_length,
                           requires_keyboard=True,
                           test_options=inject_tests(), specimen_types=inject_specimen_types(),
                           panel_options=inject_panels())



# USER ROUTES

# route to login page
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        # username = request.form.get('username')
        # password = request.form.get('password')
         
        # print(f"Username: {username}")
        # print(f"Password: {password}")

        # user = User.get(username)
        user = User.get(request.form['username'])
        if user is None:
            error = "Invalid username. Please try again."
            # print("User not found.")
        else:
            # print("User found:", user)  # Debugging
            if not check_password_hash(user.password_hash, request.form['password']):
                # print("Password check failed")  # Debugging
                error = "Wrong password. Please try again."
            else:
                session.permanent = True
                session["user"] = {'username': user.username,
                                   'role': user.role,
                                   'current_user': user.name,
                                   'team': user.team,
                                   'rank': user.designation}
                if not user.is_active():
                    user.status = "Active"
                    user.save()
                return redirect(url_for('select_location'))
    else:
        pass
    session["user"] = None
    return render_template('user/login.html', error=error, requires_keyboard=True)


# Route to handle logging out
@app.route("/logout")
def logout():
    # Turn off LEDs
    if settings["using_rpi"] == "True":
        led_control().turn_led_off()

    session["user"] = None
    session["location"] = None
    return render_template('user/login.html', requires_keyboard=True)


# route to main user management page
@app.route("/users")
def users():
    current_users = User.all()
    return render_template("user/index.html", requires_keyboard=True, users=current_users)


@app.route("/user/create", methods=["POST"])
def create_user():
    user = User.get(request.form['username'])
    if user is None:
        provider = User(request.form['username'], request.form["name"], request.form['role'],
                        request.form['designation'], request.form["password"], "Active")

        if request.form['designation'] in ['Consultant', 'Intern', 'Registrar', 'Medical Student',
                                           'Student Clinical Officer', "Clinical Officer", "Visiting Doctor"]:
            provider.team = request.form["team"]
        else:
            provider.ward = request.form["wardAllocation"]
        provider.save()
    else:
        current_users = User.all()
        flash("Username already exists", 'error')
        return render_template("user/index.html", requires_keyboard=True, users=current_users)
    flash("New user created", "success")
    return redirect(url_for("users"))


#edit route
@app.route('/user/<username>/edit', methods=['GET', 'POST'])
def edit_user(username=None):
    user = User.get(username)

    if user is None:
            flash('User not found', 'error')
            return redirect(url_for('index'))
    else:

        if request.method == 'POST':
                user.name = request.form['name']
                user.username = request.form['username']
                user.role = request.form['role']
                user.designation = request.form['designation']
                user.save()
                flash("user updated successfully")
                return redirect(url_for("users"))
        else:
            return render_template("user/edit_user.html", requires_keyboard=True, user=user)




#update password query
@app.route("/user/<user_id>/update_password", methods=["GET", "POST"])
def change_password(user_id=None):
    if request.method == "POST":
        user = User.get(user_id)
        if user is None:
            flash("User not found", 'error')
            return redirect(url_for("index"))
        else:
            user.password = request.form["password"]
            user.save()
            return redirect(url_for("index"))
    else:
        return render_template("user/update_password.html", requires_keyboard=True, username=user_id)

#reset password

@app.route("/user/<user_id>/reset_password")
def reset_password(user_id=None):
    user = User.get(user_id)
    if user is None:
        flash("User not found", 'error')
        return redirect(url_for("index"))
    else:
        user.password = user.name.split(" ")[1].lower()
        user.save()
        return redirect(url_for("index"))


@app.route("/user/<user_id>/deactivate")
def deactivate_user(user_id=None):
    user = User.get(user_id)
    if user is None:
        flash("User not found", 'error')
        return redirect(url_for("index"))
    else:
        user.status = "Deactivated"
        user.save()
        return redirect(url_for("users"))


@app.route("/user/<user_id>/activate")
def activate_user(user_id=None):
    user = User.get(user_id)
    if user is None:
        flash("User not found", 'error')
        return redirect(url_for("index"))
    else:
        user.status = "Active"
        user.save()
        return redirect(url_for("users"))


@app.route("/select_location", methods=["GET", "POST"])
def select_location():
    # Turn off LEDs
    if settings["using_rpi"] == "True":
        led_control().turn_led_off()

    error = None
    departments = []

    # Load departments data from department.config
    with open('config/department.config') as json_file:
        config_data = json.load(json_file)
        departments = config_data.get('departments', [])

    if request.method == "POST":
        selected_department = request.form.get('department')
        selected_ward = request.form.get('ward')

        if selected_department == '' or selected_ward == '':
            flash("Please select both department and ward.", 'error')
            error = "Please select both department and ward."
        else:
            session["location"] = selected_ward
            return redirect(url_for('index'))

    session["ward"] = None
    return render_template('user/select_location.html', error=error, departments=departments)

###### LAB ORDER ROUTES ###########
# create a new lab test order
@app.route("/test/create", methods=['POST'])
def create_lab_order():
    for test in request.form.getlist('test_type[]'):
        new_test = {
            'ordered_by': request.form['ordered_by'],
            'date_ordered': int(datetime.now().strftime('%s')),
            'status': 'Ordered',
            'sample_type': request.form['specimen_type'],
            'clinical_history': (request.form['clinical_history']).lower(),
            'Priority': request.form['priority'],
            'ward': session["location"],
            'patient_id':
                request.form['patient_id']
        }
        if len(test.split("|")) > 1:
            new_test['tests'] = {}
            new_test['type'] = "test panel"
            new_test["panel_type"] = test.replace("|", "")
            panel_details = LaboratoryTestPanel.get(new_test["panel_type"])
            if panel_details is not None:
                for test_in_panel in panel_details.tests:
                    new_test['tests'][LaboratoryTestType.get(test_in_panel).test_type_id] = {}
        else:
            new_test['type'] = 'test'
            new_test['test_type'] = test
        db.save(new_test)
       
        flash("New test ordered.", 'success')
    return redirect(url_for('patient', patient_id=request.form['patient_id'],
                            sample_draw=(request.form["sampleCollection"] == "Collect Now")))


# Load wards mapping from wards.config file
with open('config/wards.config') as json_file:
    wards_mapping = json.load(json_file)

# update lab test orders to specimen collected
@app.route("/test/<test_id>/collect_specimen")
def collect_specimens(test_id):
    tests = list(db.find({"selector": {"type": {"$in": ["test", "test panel"]}, "_id": {"$in": test_id.split("^")}}}))
    grouped_ids = []
    test_ids = []
    test_names = []
    if tests is None or tests == []:
        return redirect(url_for("index", error="Tests not found"))
    var_patient = Patient.get(tests[0]["patient_id"])
    dr = tests[0]["ordered_by"]
    wards = wards_mapping
    collected_at = int(datetime.now().strftime('%s'))
    collection_id = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(2)) + str(collected_at)

    #Converting gender
    if var_patient["gender"][0] == "m":
        conv_gender = "0"
    else:
        conv_gender = "1"

    for test in tests:
        test["status"] = "Specimen Collected"
        test["collected_by"] = session["user"]['username']
        test["collected_at"] = collected_at
        test["collection_id"] = collection_id
        if test["type"] == "test":
            test_ids.append(test["test_type"])
            test_names.append(LaboratoryTestType.find_by_test_type(test["test_type"]).printable_name())
            test_string = [var_patient["name"].replace(" ", "^"), var_patient["_id"], conv_gender,
                           datetime.strptime(var_patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                           wards[tests[0]["ward"]], dr, (tests[0]["clinical_history"]).lower(), tests[0]["sample_type"],
                           datetime.now().strftime("%s"), '^'.join(test_ids), tests[0]["Priority"][0]]
        else:
            panel = LaboratoryTestPanel.get(test["panel_type"])
            test_names.append(panel.short_name)
            if panel.orderable:
                test_ids.append(panel.panel_id)
                test_string = [var_patient["name"].replace(" ", "^"), var_patient["_id"], conv_gender,
                               datetime.strptime(var_patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                               wards[tests[0]["ward"]], dr, (tests[0]["clinical_history"]).lower(), tests[0]["sample_type"],
                               datetime.now().strftime("%s"), '^'.join(test_ids), tests[0]["Priority"][0], "P"]
            else:
                for test_type in panel.tests:
                    test_id = LaboratoryTestType.get(test_type).test_type_id
                    test_ids.append(test_id)

                test_string = [var_patient["name"].replace(" ", "^"), var_patient["_id"], conv_gender,
                               datetime.strptime(var_patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                               wards[tests[0]["ward"]], dr, (tests[0]["clinical_history"]).lower(), tests[0]["sample_type"],
                               datetime.now().strftime("%s"), '^'.join(test_ids), tests[0]["Priority"][0]]
        db.save(test)

    if len('~'.join(test_string)) > 86:
        chars_subtract = len('~'.join(test_string)) - 86
        test_string[6] = test_string[6][0:(len(test_string[6]) - chars_subtract)]

    label_file = open("/tmp/test_order.lbl", "w+")
    label_file.write("N\nq406\nQ203,027\nZT\n")
    label_file.write('A5,10,0,1,1,2,N,"%s"\n' % var_patient["name"])
    label_file.write('A5,40,0,1,1,2,N,"%s (%s)"\n' % (
        datetime.strptime(var_patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y"), var_patient["gender"][0]))
    label_file.write('b5,70,P,386,80,"%s$"\n' % '~'.join(test_string))
    label_file.write('A20,170,0,1,1,2,N,"%s"\n' % ','.join(test_names))
    label_file.write('A260,170,0,1,1,2,N,"%s" \n' % datetime.now().strftime("%d-%b %H:%M"))
    label_file.write("P1\n")
    label_file.close()
    #os.system('sudo sh ~/print.sh /tmp/test_order.lbl')
    #redirect(url_for('patient', patient_id=var_patient.get("_id")))

    flash("Specimen collected.", 'success')
    return render_template("download.html", patient_id=var_patient["_id"])

    #return redirect(url_for("download_file"))


@app.route("/download")
def download_file():
    return send_file("/tmp/test_order.lbl",as_attachment = True)

# update lab test orders to specimen ++collected
@app.route("/test/<test_id>/reprint")
def reprint_barcode(test_id):
    print(test_id)
    print("Point 0")
    tests = list(db.find({"selector": {"type": {"$in": ["test", "test panel"]}, "_id": {"$in": test_id.split("^")}}}))
    print(tests)
    if tests is None or tests == []:
        print("Point 1")
        tests = list(db.find({"selector": {"collection_id": test_id}}))
        # tests = db.find({"selector": {"_id": test_id}})
        print(tests)

    test_ids = []
    test_names = []
    if tests is None or tests == []:
        print("Point 2")
        return redirect(url_for("index", error="Tests not found"))
    var_patient = Patient.get(tests[0]["patient_id"])
    dr = tests[0]["ordered_by"]
    wards = wards_mapping
    print("Point 3")

    if var_patient["gender"][0] == "m":
        print("Point 4")
        conv_gender = "0"
    else:
        print("Point 5")
        conv_gender = "1"

    for test in tests:
        print("Point 6")
        if test["type"] == "test":
            print("Point 7")
            test_ids.append(test["test_type"])
            test_names.append(LaboratoryTestType.find_by_test_type(test["test_type"]).printable_name())
            test_string = [var_patient["name"].replace(" ", "^"), var_patient["_id"], conv_gender,
                           datetime.strptime(var_patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                           wards[tests[0]["ward"]], dr, (tests[0]["clinical_history"]).lower(), tests[0]["sample_type"],
                           datetime.now().strftime("%s"), "^".join(test_ids), tests[0]["Priority"][0]]
        else:
            print("Point 8")
            panel = LaboratoryTestPanel.get(test["panel_type"])
            test_names.append(panel.short_name)
            if panel.orderable:
                test_ids.append(panel.panel_id)
                test_string = [var_patient["name"].replace(" ", "^"), var_patient["_id"], conv_gender,
                               datetime.strptime(var_patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                               wards[tests[0]["ward"]], dr, (tests[0]["clinical_history"]).lower(), tests[0]["sample_type"],
                               datetime.now().strftime("%s"), "^".join(test_ids), tests[0]["Priority"][0], "P"]
                print("Point 9")
                
            else:
                print("Point 10")
                for test_type in panel.tests:
                    print("Point 11")
                    test_id = LaboratoryTestType.get(test_type).test_type_id
                    test_ids.append(test_id)

                test_string = [var_patient["name"].replace(" ", "^"), var_patient["_id"], conv_gender,
                               datetime.strptime(var_patient.get('dob'), "%d-%m-%Y").strftime("%s"),
                               wards[tests[0]["ward"]], dr, (tests[0]["clinical_history"]).lower(), tests[0]["sample_type"],
                               datetime.now().strftime("%s"), "^".join(test_ids), tests[0]["Priority"][0]]
                print("Point 12")
                


    label_file = open("/tmp/test_order.lbl", "w+")
    label_file.write("N\nq406\nQ203,027\nZT\n")
    label_file.write('A5,10,0,1,1,2,N,"%s"\n' % var_patient["name"])
    label_file.write('A5,40,0,1,1,2,N,"%s (%s)"\n' % (
        datetime.strptime(var_patient.get('dob'), "%d-%m-%Y").strftime("%d-%b-%Y"), var_patient["gender"][0]))
    label_file.write('b5,70,P,386,80,"%s$"\n' % "~".join(test_string))
    label_file.write('A20,170,0,1,1,2,N,"%s"\n' % ",".join(test_names))
    label_file.write('A260,170,0,1,1,2,N,"%s" \n' % datetime.now().strftime("%d-%b %H:%M"))
    label_file.write("P1\n")
    label_file.close()
    #os.system('sudo sh ~/print.sh /tmp/test_order.lbl')

    return render_template("download.html", patient_id=var_patient["_id"])

@app.route("/test/<test_id>/review_ajax")
@app.route("/test/<test_id>/review")
def review_test(test_id):
    test = db.get(test_id)
    if test.get("status") == "Analysis Complete":
        test["status"] = "Reviewed"
    else:
        test["status"] = "Specimen Rejected"
    test["reviewed_by"] = session["user"]['username']
    test["reviewed_at"] = int(datetime.now().strftime('%s'))
    db.save(test)
    if "review_ajax" in request.path.split("/"):
        return "Success"
    else:
        return redirect(url_for('patient', patient_id=test['patient_id']))

@app.route("/get_charge_state")
def get_charge_state():
    return Response(json.dumps(inject_power()), mimetype='application/json')


@app.route("/low_voltage")
def low_voltage():
    return render_template('main/low_voltage.html')


# MISC Functions
def get_test_measures(test, test_details):
    results = {}
    for measure in test.get("measures", []):
        if test_details.measures.get(measure) is None:
            results[measure] = {"range": "", "interpretation": "Normal", "value": test["measures"][measure]}
        else:
            if test_details.measures[measure].get("minimum") is not None:
                results[measure] = {
                    "range": test_details.measures[measure].get("minimum") + " - " + test_details.measures[
                        measure].get("maximum")}
                results[measure]["value"] = re.sub(r'[^0-9\.]', '', test["measures"][measure])
                if results[measure]["value"] == "":
                    results[measure]["value"] = "Not Done"
                    results[measure]["interpretation"] = "Normal"
                elif float(results[measure]["value"]) < float(test_details.measures[measure].get("minimum")):
                    results[measure]["interpretation"] = "Low"
                elif float(results[measure]["value"]) > float(test_details.measures[measure].get("maximum")):
                    results[measure]["interpretation"] = "High"
                else:
                    results[measure]["interpretation"] = "Normal"
            else:
                results[measure] = {"range": "", "interpretation": "Normal", "value": test["measures"][measure]}

    return results


def get_panel_details(panel):
    details = {}
    for panel_test in panel.get("tests").keys():
        if details.get(panel_test) is None:
            test = LaboratoryTestType.find_by_test_type(panel_test)
        details[panel_test] = {"test_name": test.test_name}
        details[panel_test]['measures'] = get_test_measures(panel.get("tests")[panel_test], test)
    return details


def get_pending_panel_details(test):
    panel_details = {"test_id": test["_id"], "specimen_type": specimen_type_map(test['sample_type']),
                     "test_name": test["panel_type"]
                     }
    if panel_details["specimen_type"] == "Urine":
        panel_details["container"] = 'Conical container'
        panel_details["volume"] = "15 "
        panel_details["units"] = "ml"
    elif panel_details["specimen_type"] == "Blood" and panel_details["test_name"] == "MC&S":
        panel_details["container"] = 'Baktech'
        panel_details["volume"] = "5 "
        panel_details["units"] = "ml"
    elif panel_details["specimen_type"] == "Blood" and panel_details["test_name"] == "PBF":
        panel_details["container"] = 'EDTA'
        panel_details["volume"] = "3 "
        panel_details["units"] = "ml"
    else:
        panel_details["container"] = 'Red top'
        panel_details["volume"] = "4"
        panel_details["units"] = "ml"

    return panel_details


def get_pending_test_details(test, detail):
    return {"test_id": test["_id"], "test_type": detail.test_name, "department": detail.department,
            "specimen_type": detail.specimen_requirements[test["sample_type"]]["type_of_specimen"],
            "test_name": detail.test_name, "container": detail.specimen_requirements[test["sample_type"]]["container"],
            "volume": detail.specimen_requirements[test["sample_type"]]["volume"],
            "units": detail.specimen_requirements[test["sample_type"]]["units"]}


# DB CALLS
def prescribers():
    providers = []
    var_users = User.get_active_prescribers()
    # db.find({"selector": {"type": "user", "role": "Doctor", "status": {"$exists": False}}, "fields": ["_id", "name"]})

    for user in var_users:
        if len(user['name'].split(" ")) > 1:
            name = user['name'].split(" ")[0] + ". " + user['name'].split(" ")[1]
        else:
            name = user['name']
        providers.append([name, user['_id']])
    providers.sort()
    return providers


def locations_options():
    return [["MSS", "Medical Short Stay"], ["4A", "Medical Female Ward"], ["4B", "Medical Male Ward"],
            ["MHDU", "Medical HDU"]]
#
#     locations = {
#         "Medical": ["4A", "4B", "Short Stay", "OPD1", "OPD2"],
#         "Pediatrics": ["Ward A", "Ward B", "Ward C", "HDU"]
#     }
#     options = []
#     for location, wards in locations.items():
#         options.append([location, wards])
#     return options



def specimen_type_map(specimen_type):
    spec_type = LaboratoryTestType.match_specimen_types(specimen_type)
    return spec_type


def inject_tests():
    options = {}
    tests = LaboratoryTestType.get_available()
    for test in tests:
        options[test["test_type_id"]] = {"name": test["_id"], "specimen_types": test["specimen_types"].keys()}

    options = sorted(options.items(), key=lambda e: e[1]["name"])
    return options


def inject_specimen_types():
    options = LaboratoryTestType.get_specimen_types()
    options.sort()

    return [options[i * 2:(i + 1) * 2] for i in range((len(options) + 2 - 1) // 2)]


def inject_panels():
    options = {}
    panels = LaboratoryTestPanel.get_available()
    for panel in panels:
        options[panel["_id"]] = {"name": panel["_id"], "specimen_types": panel["specimen_types"].keys()}
    options = sorted(options.items(), key=lambda e: e[1]["name"])
    return options


###### APPLICATION CALLBACKS ###########
def initialize_connection():
    # Connect to a couchdb instance
    couchConnection = Server("http://%s:%s@%s:%s/" %
                             (settings["couch"]["user"], settings["couch"]["passwd"],
                              settings["couch"]["host"], settings["couch"]["port"]))
    global db
    # Connect to a database or Create a Database
    try:
        db = couchConnection[settings["couch"]["database"]]
    except:
        db = couchConnection.create(settings["couch"]["database"])


@app.before_request
def check_authentication():
    if not re.search("asset", request.path):
        initialize_connection()

        if request.path not in ["/login", "/logout", "/get_charge_state", "/low_voltage"]:
            if session.get("user") is None:
                return redirect(url_for('login'))
            else:
                if session.get("location") is None and request.path != "/select_location":
                    return redirect(url_for('select_location'))

###### APPLICATION CONTEXT PROCESSORS ###########
# Used to get data in views
@app.context_processor
def inject_now():
    return {'now': datetime.now().strftime("%H:%M%p")}

@app.context_processor
def inject_user():
    return {'current_user': session.get("user")}


@app.context_processor
def inject_message_category():
    return {'message_category': {"info": "#004085", "success": "#28a745", "error": "#dc3545", "warning": "#ffc107"}}


@app.context_processor
def inject_power():
    if settings["using_rpi"] == "True":
        check_charging = CheckChargeState().getState()
        voltage = CheckVoltage().get_voltage()
        raw_voltage = (voltage / 40.0) + 14

        # if raw_voltage < 12:
        # shutdown
        # os.system('sudo shutdown now')

        if voltage > 70:
            rating = "high"
            if voltage == 100 and check_charging:
                led_control().charger_led_green()
            elif voltage < 100 and check_charging:
                led_control().charger_led_red()
            else:
                led_control().charger_led_off()
        elif 30 < voltage < 70:
            rating = "medium"
            if check_charging:
                led_control().charger_led_red()
            else:
                led_control().charger_led_off()
        else:
            rating = "low"
            if check_charging:
                led_control().charger_led_red()
            else:
                led_control().charger_led_off()
    else:
        check_charging = True
        voltage = 100
        rating = "high"
    return {"current_power": voltage, "power_class": rating, "checkCharging": check_charging}


# Error handling pages
@app.errorhandler(404)
def not_found_error(error):
    return render_template('main/404.html'), 404


@app.errorhandler(422)
def not_found_error(error):
    return render_template('main/422.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('main/500.html'), 500

@app.errorhandler(502)
def internal_error(error):
    return render_template('main/502.html'), 502

if __name__ == '__main__':
    app.run(port="4500", debug=True, host='0.0.0.0')
