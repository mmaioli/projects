# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.object_storage import BUCKET_NAME

EXPERIMENT_ID = str(uuid_alpha())
NAME = "foo"
POSITION = 0
EXPERIMENT_ID_2 = str(uuid_alpha())
NAME_2 = "foo 2"
POSITION_2 = 1
PROJECT_ID = str(uuid_alpha())
TEMPLATE_ID = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
OPERATOR_ID_2 = str(uuid_alpha())
OPERATOR_ID_3 = str(uuid_alpha())
OPERATOR_ID_4 = str(uuid_alpha())
DEPENDENCY_ID = str(uuid_alpha())
IS_ACTIVE = True
PARAMETERS = {"coef": 0.1}
PARAMETERS_JSON = dumps(PARAMETERS)
DESCRIPTION = "long foo"
IMAGE = "platiagro/platiagro-notebook-image-test:0.1.0"
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
ARGUMENTS = ["ARG"]
ARGUMENTS_JSON = dumps(ARGUMENTS)
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
TASKS_JSON = dumps([TASK_ID])
EXPERIMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Deployment.ipynb"
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"
NAME_COPYFROM = "TEST_COPY"


class TestExperiments(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{TASK_ID}', '{NAME}', '{DESCRIPTION}', '{IMAGE}', '{COMMANDS_JSON}', '{ARGUMENTS_JSON}', '{TAGS_JSON}', '{EXPERIMENT_NOTEBOOK_PATH}', '{DEPLOYMENT_NOTEBOOK_PATH}', 0, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)
        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at) "
            f"VALUES ('{PROJECT_ID}', '{NAME}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES ('{EXPERIMENT_ID}', '{NAME}', '{PROJECT_ID}', '{POSITION}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES ('{EXPERIMENT_ID_2}', '{NAME_2}', '{PROJECT_ID}', '{POSITION_2}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID_2}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO templates (uuid, name, tasks, created_at, updated_at) "
            f"VALUES ('{TEMPLATE_ID}', '{NAME}', '{TASKS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO dependencies (uuid, operator_id, dependency) "
            f"VALUES ('{DEPENDENCY_ID}', '{OPERATOR_ID_2}', '{OPERATOR_ID}')"
        )
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()

        text = f"DELETE FROM templates WHERE uuid = '{TEMPLATE_ID}'"
        conn.execute(text)

        text = f"DELETE FROM dependencies WHERE operator_id in" \
               f" (SELECT uuid FROM operators WHERE task_id = '{TASK_ID}')"
        conn.execute(text)

        text = f"DELETE FROM operators WHERE experiment_id = '{EXPERIMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM operators WHERE experiment_id =" \
               f" (SELECT uuid FROM experiments where name = '{NAME_COPYFROM}')"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id in ('{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid = '{TASK_ID}'"
        conn.execute(text)

        conn.close()

    def test_list_experiments(self):
        with app.test_client() as c:
            rv = c.get("/projects/unk/experiments")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_experiment(self):
        with app.test_client() as c:
            rv = c.post("/projects/unk/experiments", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments", json={})
            result = rv.get_json()
            expected = {"message": "name is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments", json={
                "name": NAME,
            })
            result = rv.get_json()
            expected = {"message": "an experiment with that name already exists"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments", json={
                "name": "test",
            })
            result = rv.get_json()
            expected = {
                "name": "test",
                "projectId": PROJECT_ID,
                "position": 2,
                "isActive": IS_ACTIVE,
                "operators": [],
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

        """Copy operators for a given experiment"""
        with app.test_client() as c:
            rv = c.post(f"/projects/{PROJECT_ID}/experiments", json={
                "name": f"{NAME_COPYFROM}",
                "copy_from": f"{EXPERIMENT_ID}"
            })
            self.assertEqual(rv.status_code, 200)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments", json={
                "name": f"TESCOPY",
                "copy_from": f"4555"
            })
            self.assertEqual(rv.status_code, 400)

    def test_get_experiment(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/foo/experiments/{EXPERIMENT_ID}")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/foo")
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}")
            result = rv.get_json()
            expected = {
                "uuid": EXPERIMENT_ID,
                "name": NAME,
                "projectId": PROJECT_ID,
                "position": POSITION,
                "isActive": IS_ACTIVE,
                "operators": result['operators'],
                "createdAt": CREATED_AT_ISO,
                "updatedAt": UPDATED_AT_ISO,
            }
            self.assertDictEqual(expected, result)

    def test_update_experiment(self):
        with app.test_client() as c:
            rv = c.patch(f"/projects/foo/experiments/{EXPERIMENT_ID}", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}", json={
                "name": NAME_2,
            })
            result = rv.get_json()
            expected = {"message": "an experiment with that name already exists"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}", json={
                "templateId": "unk",
            })
            result = rv.get_json()
            expected = {"message": "The specified template does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}", json={
                "unk": "bar",
            })
            self.assertEqual(rv.status_code, 400)

            # update experiment using the same name
            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}", json={
                "name": NAME,
            })
            self.assertEqual(rv.status_code, 200)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}", json={
                "name": "bar",
            })
            result = rv.get_json()
            expected = {
                "uuid": EXPERIMENT_ID,
                "name": "bar",
                "projectId": PROJECT_ID,
                "position": POSITION,
                "isActive": IS_ACTIVE,
                "operators": result['operators'],
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 200)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}", json={
                "templateId": TEMPLATE_ID,
            })
            result = rv.get_json()
            expected = {
                "uuid": EXPERIMENT_ID,
                "name": "bar",
                "projectId": PROJECT_ID,
                "position": POSITION,
                "isActive": IS_ACTIVE,
                "createdAt": CREATED_AT_ISO,
            }
            result_operators = result["operators"]
            machine_generated = ["updatedAt", "operators"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)
            expected = [{
                "taskId": TASK_ID,
                "experimentId": EXPERIMENT_ID,
                "parameters": {},
                "dependencies": [],
                "positionX": None,
                "positionY": None
            }]
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                for operator in result_operators:
                    self.assertIn(attr, operator)
                    del operator[attr]
            self.assertListEqual(expected, result_operators)

    def test_delete_experiment(self):
        with app.test_client() as c:
            rv = c.delete(f"/projects/foo/experiments/{EXPERIMENT_ID}")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/experiments/unk")
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}")
            result = rv.get_json()
            expected = {"message": "Experiment deleted"}
            self.assertDictEqual(expected, result)
