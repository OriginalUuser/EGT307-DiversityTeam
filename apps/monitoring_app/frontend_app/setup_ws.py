from evidently.ui.workspace import Workspace, ProjectModel
from evidently.ui.workspace import RemoteWorkspace
from evidently.sdk.models import PanelMetric
from evidently.sdk.panels import line_plot_panel

import os

# setup.py
# Creates the evidently workspace for monitoring reports and dashboards

# Create the evidently workspace
# WORKSPACE_DIR = os.getenv("WORKSPACE_DIR")
ws = Workspace.create("workspace")

# If the project does not exist yet, create the project (which will store the monitoring reports and runs)
if len(ws.search_project("Aquaponics Monitoring")) == 0:
    project_spec = ProjectModel(name="Aquaponics Monitoring", 
                                description="Aquaponics ML Model Monitoring dashboard powered by Evidently")
    project = ws.add_project(project_spec)

    # TODO: Add the dashboard panels on startup
    
