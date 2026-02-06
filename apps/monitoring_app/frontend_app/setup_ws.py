from evidently.ui.workspace import Workspace, ProjectModel

import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# setup.py
# Creates the evidently workspace for monitoring reports and dashboards

# Create the evidently workspace
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR")
ws = Workspace.create(WORKSPACE_DIR)
logger.debug(f"Workspace created: {WORKSPACE_DIR}")

# If the project does not exist yet, create the project (which will store the monitoring reports and runs)
if len(ws.search_project("Aquaponics Monitoring")) == 0:
    project_spec = ProjectModel(name="Aquaponics Monitoring", 
                                description="Aquaponics ML Model Monitoring dashboard powered by Evidently")
    project = ws.add_project(project_spec)
    logger.debug(f"Project created: {project}")    