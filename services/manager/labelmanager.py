from label_studio_sdk import LabelStudio

from database.boundary.base_boundary import ReadBoundary, WriteBoundary

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.envmanager import EnvManager

class LabelManager:
    def __init__(self, manager: "ManagerHandler" ):
        self.manager            = manager

        # Set connected managers
        self.env                    = self.manager.get_env()
        self.db                     = self.manager.get_db()
        self.log                    = self.manager.create_log_in_folder(["logs", "label_manager"], f"")
        self.log.set_logging_level(2)

        self.read                   = ReadBoundary(self.db)
        self.write                  = WriteBoundary(self.db)

        # Initialize Label Studio Client
        config                      = self.env.get_label_studio()
        self.client                 = LabelStudio(base_url=config["endpoint"], api_key=config["api_token"])

        self.project_label_config   = """
            <View>
                <Relations>
                    <Relation value="org:founded_by"/>
                    <Relation value="org:founded"/>
                </Relations>
                <Labels name="label" toName="text">
                    <Label value="PER" background="#e74c3c"/>        <!-- Red -->
                    <Label value="LOC" background="#9b59b6"/>      <!-- Purple -->
                    <Label value="GRP" background="#f1c40f"/>         <!-- Yellow -->
                    <Label value="PRON" background="#27ae60"/>       <!-- Green -->
                    <Label value="Divine" background="#3498db"/>   <!-- Light Blue -->
                    <Label value="NOUN" background="#16a085"/>          <!-- Teal -->
                    <Label value="APOS" background="#e67e22"/>  <!-- Orange -->
                    <Label value="Q" background="#d35400"/>         <!-- Dark Orange -->
                </Labels>

                <Text name="text" value="$text"/>
            </View>
        """

        self.labelling_projects     = self.update_labelling_projects()

    def init_container(self):
        # Code that can be used to replace the logic in init_label_studio.py
        pass

    def update_labelling_projects(self):

        loaded_db_projects  = self.read.get_all_label_projects()

        temp_projects       = {}

        if not loaded_db_projects:
            return {}

        for project_id, translation_id, project_name, project_description in loaded_db_projects:
            temp_projects[project_id] = {
                "translation_id": translation_id,
                "project_name": project_name,
                "project_description": project_description
            }

        return temp_projects

    def get_labelling_projects(self, translation_id: int=None, project_id: int=None):
        # Either get all projects with translation_id
        if translation_id != None:
            temp_projects = {}
            for project_id, details in self.labelling_projects.items():
                if details["translation_id"] == translation_id:
                    temp_projects[project_id] = details
            return temp_projects
        
        # Get the one project with project_id
        if project_id != None:
            return self.labelling_projects[project_id]
        
        # Get all projects
        return self.labelling_projects
    
    def get_project_id(self, project_id: int):
        # Might modify to 
        return self.client.projects.get(
            id  = project_id,
        )

    def create_new_translation_project(self, 
            translation_id          : int, 
            project_name            : str, 
            project_description     : str
        ):

        translation_project = self.client.projects.create(
            title           = project_name,
            description     = project_description,
            label_config    = self.project_label_config
        )

        traslation_project_id = translation_project.id

        self.labelling_projects[traslation_project_id] = {
            "translation_id"        : translation_id,
            "project_name"          : project_name,
            "project_description"   : project_description
        }

        minio_config        = self.env.get_minio_config()

        # For now not sure how this works
        # export_storage = self.client.export_storage.s3.create(
        #     s3endpoint=f"http://192.168.0.19:8080", #Updated from localhost to hardcoded IP
        #     aws_access_key_id=minio_config["username"],
        #     aws_secret_access_key=minio_config["password"],
        #     project=self.translation_project.id,
        #     bucket="bible-nlp",
        #     prefix=f"{self.translation_title}/exports/",
        #     title="TEST Export"
        # )

        # In Bible Insight DB, update with new project details
        self.write.persist_label_studio_project(
            label_project_id    = traslation_project_id,
            project_name        = project_name,
            project_description = project_description
        )

        # In Bbile Insight DB, link translation to labelling project
        self.write.map_label_studio_project(
            translation_id      = translation_id,
            label_project_id    = traslation_project_id
        )

        self.log.log_to_file(f"Created New Label Studio Project [Project_ID: {traslation_project_id}] [Translation_ID: {translation_id}]", "LABEL", "INFO")

        return traslation_project_id