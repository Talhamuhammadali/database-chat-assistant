EXAMPLES = [
    {
        "question": "What is my name",
        "query": "Talha"
    },
    {
        "question": "What is role",
        "query": "AI engineer"
    },
    {
        "question": "What is my current project",
        "query": "Developement of chat bot"
    },
    {
        "question": "What is the expected ETA",
        "query": "Approximately 100hrs of work"
    },
]

REDMINE_TABLES = {
    "projects": {
        "description": """This table stores information about each project in Redmine.
Each project has a unique identifier (id) and fields for attributes such as the project name,
description, identifier (a short name used in URLs), parent project (if any), and more.""",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each project."},
            {"name": "name", "description": "Name of the project."},
            {"name": "description", "description": "Description of the project."},
            {"name": "identifier", "description": "Short name used in URLs for the project."}
        ]
    },
    "issues": {
        "description": """The issues table is where information about individual tasks, bugs, or features (referred to as issues) is stored. Each issue has a unique identifier (id) and fields for attributes such as the project it belongs to (project_id),
the issue's subject, description, status, priority, assigned user (assigned_to_id), and more.""",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each issue."},
            {"name": "project_id", "description": "ID of the project the issue belongs to."},
            {"name": "subject", "description": "Subject or title of the issue."},
            {"name": "description", "description": "Description of the issue."},
            {"name": "status_id", "description": "ID of the status of the issue."},
            {"name": "assigned_to_id", "description": "ID of the user assigned to the issue."}
        ]
    },
    "users": {
        "description": "Stores information about users in Redmine.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each user."},
            {"name": "login", "description": "User's login name."},
            {"name": "mail", "description": "User's email address."},
            {"name": "firstname", "description": "User's first name."},
            {"name": "lastname", "description": "User's last name."}
        ]
    },
    "roles": {
        "description": "Defines roles with specific permissions that can be assigned to users within projects.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each role."},
            {"name": "name", "description": "Name of the role."},
            {"name": "permissions", "description": "Permissions assigned to the role."},
            {"name": "assignable", "description": "Indicates if the role is assignable."}
        ]
    },
    "members": {
        "description": "Associates users with projects and roles by storing membership information.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each membership."},
            {"name": "user_id", "description": "ID of the user."},
            {"name": "project_id", "description": "ID of the project."},
            {"name": "role_id", "description": "ID of the role within the project."}
        ]
    },
    "trackers": {
        "description": "Categorizes different types of issues in Redmine.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each tracker."},
            {"name": "name", "description": "Name of the tracker."},
            {"name": "is_in_chlog", "description": "Indicates if the tracker should be shown in the changelog."}
        ]
    },
    "issue_statuses": {
        "description": "Defines the possible statuses that issues can have.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each status."},
            {"name": "name", "description": "Name of the status."},
            {"name": "is_closed", "description": "Indicates if the status represents a closed state."}
        ]
    },
    "custom_fields": {
        "description": "Stores information about custom fields that can be added to projects or issues.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each custom field."},
            {"name": "name", "description": "Name of the custom field."},
            {"name": "field_format", "description": "Format of the custom field."},
            {"name": "is_required", "description": "Indicates if the custom field is required."}
        ]
    },
    "time_entries": {
        "description": "Records time entries for work done on issues by users.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each time entry."},
            {"name": "user_id", "description": "ID of the user who logged the time entry."},
            {"name": "issue_id", "description": "ID of the issue the time entry is related to."},
            {"name": "hours", "description": "Amount of time spent on the issue (in hours)."},
            {"name": "activity_id", "description": "ID of the activity associated with the time entry."},
            {"name": "spent_on", "description": "Date when the time was logged."},
            {"name": "comments", "description": "Additional comments or description for the time entry."}
        ]
    },
    "attachments": {
        "description": "Stores file attachments associated with issues or other entities.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each attachment."},
            {"name": "container_id", "description": "ID of the entity the attachment belongs to."},
            {"name": "container_type", "description": "Type of the entity the attachment belongs to."},
            {"name": "filename", "description": "Name of the attached file."},
            {"name": "disk_filename", "description": "Name of the file on disk."},
            {"name": "filesize", "description": "Size of the attached file."}
        ]
    },
    "enumerations": {
        "description": "Contains various enumerations used throughout Redmine.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each enumeration."},
            {"name": "name", "description": "Name of the enumeration."},
            {"name": "position", "description": "Position of the enumeration."},
            {"name": "is_default", "description": "Indicates if the enumeration is a default option."}
        ]
    },
    "member_roles": {
        "description": "Associates roles with members within projects, defining the roles each member holds.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each member role."},
            {"name": "member_id", "description": "ID of the member associated with the role."},
            {"name": "role_id", "description": "ID of the role assigned to the member."},
            {"name": "inherited_from", "description": "Indicates if the role is inherited from a parent project."}
        ]
    },
    "projects_trackers": {
        "description": "Defines which trackers are available for each project.",
        "important_columns": [
            {"name": "id", "description": "Unique identifier for each project-tracker association."},
            {"name": "project_id", "description": "ID of the project."},
            {"name": "tracker_id", "description": "ID of the tracker associated with the project."}
        ]
    }
}
