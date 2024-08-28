# Main Thread

## Imports
- **json**: Provides functions to work with JSON data, such as parsing JSON strings into Python dictionaries and vice versa.
- **os**: Allows interaction with the operating system, such as accessing environment variables, reading/writing files, and generating random bytes.
- **random**: Generates random numbers, selects random elements from lists, and performs other randomization functions.
- **re**: Provides regular expression matching operations, useful for searching, splitting, and manipulating strings.
- **datetime**: Supplies classes for manipulating dates and times, allowing you to work with timestamps, time intervals, etc.
- **couchdb.Server**: Connects to a CouchDB server, allowing operations on databases, documents, and design documents.
- **flask**:
  - **Flask**: The main class used to create a Flask web application.
  - **render_template**: Renders HTML templates with provided data.
  - **redirect**: Redirects the client to a different URL.
  - **session**: Manages session data, which is stored on the server-side.
  - **flash**: Provides a way to show messages to the user across requests.
  - **request**: Contains the data of the HTTP request, such as form data, query parameters, etc.
  - **url_for**: Generates URLs for the specified endpoint.
  - **Response**: Represents the HTTP response returned to the client.
  - **send_file**: Sends a file to the client as a response.
- **werkzeug.security.check_password_hash**: Verifies that a given password matches a hashed password stored in the database.
- **models.laboratory_test_panel.LaboratoryTestPanel**: Likely represents a model for managing laboratory test panels in the application.
- **models.laboratory_test_type.LaboratoryTestType**: Manages different types of laboratory tests.
- **models.patient.Patient**: Represents a patient model, likely handling patient data and operations.
- **models.user.User**: Manages user-related data and operations, such as authentication and user roles.
- **utils.misc**: A custom utility module, possibly containing miscellaneous functions used throughout the application.


## Route 1: `index()`
- **Purpose**: 
    - The `index()` route serves as the root page of the application. It dynamically retrieves and displays information based on the user's role within the system, such as a nurse, doctor, or student.

- **Functionality**:
    - **LED Control for QR Scanning**: 
        - If the application is running on a Raspberry Pi (`using_rpi` is `True`), the LEDs used for QR scanning are turned on when accessing the root path (`"/"`). LEDs are turned off for other routes.
    - **Database Queries**: 
        - Based on the user’s role, the application queries the CouchDB database for records. For users in roles like Nurse, Doctor, or Student, it pulls relevant medical records from the database that match their assigned ward and specific statuses like "Ordered" or "Specimen Collected."
        - If the user is not in these roles, the query instead focuses on records ordered by the user, reflecting statuses that require their attention.
    - **Team-Based Query (Commented Out)**:
        - The code also hints at a commented-out feature to pull records for a user’s team members, enabling team collaboration by fetching orders made by any team member.

- **When It’s Called**:
    - This route is called whenever the root URL (`"/"`) is accessed. It's typically the first page a user sees after logging in or accessing the application, providing an overview of pertinent data based on their role.
