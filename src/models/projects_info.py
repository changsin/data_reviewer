import datetime
import json
import os.path
from abc import ABC

import attr

import src.common.utils as utils
from src.common.constants import ADQ_WORKING_FOLDER, PROJECTS, JSON_EXT


@attr.s(slots=True, frozen=False)
class Project(ABC):
    name = attr.ib(validator=attr.validators.instance_of(str))
    id = attr.ib(default=-1, validator=attr.validators.instance_of(int))

    dir_name = attr.ib(default=None)

    description = attr.ib(default=None)

    created_at = attr.ib(default=str(datetime.datetime.now()), validator=attr.validators.instance_of(str))
    updated_at = attr.ib(default=str(datetime.datetime.now()), validator=attr.validators.instance_of(str))

    task_total_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    task_done_count = attr.ib(default=0, validator=attr.validators.instance_of(int))

    data_total_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    data_sample_count = attr.ib(default=0, validator=attr.validators.instance_of(int))
    annotation_errors = attr.ib(default=0, validator=attr.validators.instance_of(int))

    domain_id = attr.ib(default=None)

    company_info = attr.ib(default=None)
    extended_properties = attr.ib(default=None)

    def __iter__(self):
        yield from {
            "id": self.id,
            "name": self.name,

            "dir_name": self.dir_name,

            "created_at": self.created_at,
            "updated_at": self.updated_at,

            "description": self.description,

            "task_total_count": self.task_total_count,
            "task_done_count": self.task_done_count,

            "data_total_count": self.data_total_count,
            "data_sample_count": self.data_sample_count,
            "annotation_errors": self.annotation_errors,

            "domain_id": self.domain_id,

            "company_info": self.company_info,
            "extended_properties": self.extended_properties
        }.items()

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,

            "description": self.description,

            "dir_name": self.dir_name,

            "created_at": self.created_at,
            "updated_at": self.updated_at,


            "task_total_count": self.task_total_count,
            "task_done_count": self.task_done_count,

            "data_total_count": self.data_total_count,
            "data_sample_count": self.data_sample_count,
            "annotation_errors": self.annotation_errors,


            "domain_id": self.domain_id,

            "company_info": self.company_info,
            "extended_properties": self.extended_properties
        }

    @staticmethod
    def from_json(json_dict: dict):
        return Project(
            id=json_dict.get("id", -1),
            name=json_dict["name"],

            dir_name=json_dict["dir_name"],

            created_at=json_dict["created_at"],
            updated_at=json_dict["updated_at"],

            description=json_dict["description"],

            task_total_count=json_dict.get("task_total_count", 0),
            task_done_count=json_dict.get("task_done_count", 0),

            data_total_count=json_dict.get("data_total_count", 0),
            data_sample_count=json_dict.get("data_sample_count", 0),
            annotation_errors=json_dict.get("annotation_errors", 0),

            domain_id=json_dict.get("domain_id", 1),

            company_info=json_dict.get("company_info", None),
            extended_properties=json_dict.get("extended_properties", None)
        )


@attr.s(slots=True, frozen=True)
class ModelProject:
    model_type = attr.ib(default="", validator=attr.validators.instance_of(str))
    models_used = attr.ib(default="", validator=attr.validators.instance_of(str))

    data_type = attr.ib(default="", validator=attr.validators.instance_of(str))
    data_format = attr.ib(default="", validator=attr.validators.instance_of(str))
    domain = attr.ib(default="", validator=attr.validators.instance_of(str))

    cost = attr.ib(default=0, validator=attr.validators.instance_of(int))

    def to_json(self):
        return {
            "model_type": self.model_type,
            "models_used": self.models_used,
            "data_type": self.data_type,
            "data_format": self.data_format,
            "domain": self.domain,
            "cost": self.cost
        }

    @staticmethod
    def from_json(json_dict: dict):
        return ModelProject(
            model_type=json_dict["model_type"] if json_dict.get("model_type") else "",
            models_used=json_dict["models_used"] if json_dict.get("models_used") else "",
            data_type=json_dict["data_type"] if json_dict.get("data_type") else "",
            data_format=json_dict["data_format"] if json_dict.get("data_format") else "",
            domain=json_dict["domain"] if json_dict.get("domain") else "",
            cost=json_dict["cost"] if json_dict.get("cost") else 0
        )


@attr.s(slots=True, frozen=False)
class ProjectsInfo:
    num_count = attr.ib(validator=attr.validators.instance_of(int))
    # NB: add as a json dict to make manipulating in pandas dataframe easier
    projects = attr.ib(validator=attr.validators.instance_of(list))

    def add(self, project: Project):
        self.projects.append(project)
        self.num_count = len(self.projects)

    def to_json(self):
        return {
            "num_count": self.num_count,
            "projects": [project.to_json() for project in self.projects]
        }

    def get_next_project_id(self) -> int:
        if len(self.projects) == 0:
            return 0

        project_idx = []
        for project in self.projects:
            project_idx.append(project.id)

        return max(project_idx) + 1

    def get_project_by_id(self, project_id: int) -> Project:
        if len(self.projects) > 0:
            for project in self.projects:
                if project.id == project_id:
                    return project

    def update_project(self, project_to_update: Project):
        if len(self.projects) > 0:
            index_to_update = None
            for index, project in enumerate(self.projects):
                if project.id == project_to_update.id:
                    index_to_update = index
                    break

            self.projects[index_to_update] = project_to_update

    def save(self):
        if not os.path.exists(ADQ_WORKING_FOLDER):
            os.mkdir(ADQ_WORKING_FOLDER)
        filename = os.path.join(ADQ_WORKING_FOLDER, PROJECTS + JSON_EXT)
        utils.to_file(json.dumps(self,
                                 default=utils.default, indent=2),
                      filename)

    @staticmethod
    def from_json(json_dict):
        return ProjectsInfo(num_count=json_dict['num_count'],
                            projects=[Project.from_json(json_project) for json_project in json_dict['projects']])
