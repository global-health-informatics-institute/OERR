from models.database import DataAccess
from utils.couchdb_indexes import find_with_index
from werkzeug.security import check_password_hash, generate_password_hash


class User:
    def __init__(
            self,
            username,
            name,
            role,
            designation,
            password="",
            status="Active",
            department=None,
            ward=None,
            team=None,
            unit=None,
            password_hash="",
            rev=""
        ):
        self.database = DataAccess("users").db
        self.username = username
        self.name = name
        self.role = role
        self.designation = designation
        self.password = password
        self.status = status
        self.department = department
        self.ward = ward
        self.team = team
        self.unit = unit
        self.password_hash = password_hash
        self.rev = rev

    @staticmethod
    def get(username):
        user = DataAccess("users").db.get(username)
        if user is not None:
            user = User(
                username=user.get('_id'),
                name=user.get('name', "Unknown"),
                role=user.get('role'),
                designation=user.get('designation', 'Unassigned'),
                status=user.get('status', "Active"),
                department=user.get('department', "Medical"),
                ward=user.get('ward', ""),
                team=user.get('team', ""),
                unit=user.get('unit', ""),
                password_hash=user.get("password_hash"),
                rev=user.get("_rev")
            )
        return user

    @staticmethod
    def get_team_members(team):
        users = []
        user_results = find_with_index(
            DataAccess("users").db,
            {"selector": {"team": team}, "fields": ["_id"], "limit": 5000},
            "idx_users_by_team",
        )
        for provider in user_results:
            users.append(provider["_id"])
        return users

    
    
    @staticmethod
    def all():
        return DataAccess("users").db.find({"selector": {"_id": {"$gt": None}}, "limit": 2000})
        

    @staticmethod
    def get_spesific_user(username):
        return DataAccess("users").db.find({"selector":{"_id":{"$gt": username}}, "limit":1})
    
    @staticmethod
    def get_active_prescribers():
        return find_with_index(
            DataAccess("users").db,
            {"selector": {"role": "Doctor", "status": "Active"}, "limit": 5000},
            "idx_users_by_role_status",
        )

    def save(self):
        user = self.to_dict()
        if self.rev == "":
            user.pop("_rev")
        if not self.password == "":
            user["password_hash"] = generate_password_hash(self.password)
        elif not self.password_hash == "":
            user["password_hash"] = self.password_hash
        self.database.save(user)

    def is_active(self):
        return False if self.status == "Inactive" else True
    
    def to_dict(self):
        return {
            "_id": self.username,
            "username": self.username,
            "name": self.name,
            "role": self.role,
            "designation": self.designation,
            "status": self.status,
            "department": self.department,
            "ward": self.ward,
            "team": self.team,
            "unit": self.unit,
            "type": "user",
            "_rev": self.rev
        }


    def __str__(self):
        return f"User(username: {self.username}, name: {self.name}, role: {self.role}, designation: {self.designation}, status: {self.status}, department: {self.department}, ward: {self.ward}, team: {self.team}, unit: {self.unit})"

    def __repr__(self):
        """String representation for logging and debugging purposes."""
        return f"User(username: {self.username}, name: {self.name}, role: {self.role}, designation: {self.designation}, status: {self.status}, department: {self.department}, ward: {self.ward}, team: {self.team}, unit: {self.unit})"

 # Define get_user_by_id 
    @staticmethod
    def get_user_by_id(username):
        user_data = DataAccess("users").db.get(username)
        if user_data is not None:
            user = User(
                username=user_data.get('_id'),
                name=user_data.get('name', "Unknown"),
                role=user_data.get('role'),
                designation=user_data.get('designation', ""),
                status=user_data.get('status', "Active"),
                department=user_data.get('department', ""),
                ward=user_data.get('ward', ""),
                team=user_data.get('team', ""),
                unit=user_data.get('unit', ""),
                password_hash=user_data.get("password_hash"),
                rev=user_data.get("_rev")
            )
            return user
        return None
