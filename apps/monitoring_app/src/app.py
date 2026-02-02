# app.py
# Contains the monitoring dashboard application and handles requests to the service

from evidently.ui.workspace import Workspace, ProjectModel
import fastapi

# Create the evidently workspace
ws = Workspace.create("workspace")

# Create the project (which will store the monitoring reports and runs)
project_spec = ProjectModel(name="Aquaponics Monitoring", 
                            description="Aquaponics ML Model Monitoring dashboard powered by Evidently")
project = ws.add_project(project_spec)

# 