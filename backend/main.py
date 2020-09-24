import logging
from http import HTTPStatus

from fastapi import FastAPI, Depends, HTTPException, Header, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from uuid import UUID
from datetime import datetime, timedelta
from typing import List

from models import BaseAPIResponse, UserPayload, BaseTask, User, Task, TaskComment
from queries import get_task_by_id, create_task, get_tasks_by_user, set_task_complete, set_task_incomplete, add_task_comment, \
    get_task_comments
from authentication import authenticate_user, create_access_token, create_new_user, verify_jwt_token

LOGGER = logging.getLogger(__name__)

app = FastAPI()


async def verify_task(task_id: UUID) -> Task:
    """ Helper function to get the details of a given task for use in API function. If not found, throw 404 Not Found exception."""
    task = get_task_by_id(id=task_id)
    if task is None:
        LOGGER.debug("Task not found for ID %s", task_id)
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Task not found.")
    return Task(**task)

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> BaseAPIResponse:
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Username not found")
    access_token = create_access_token(username=user.username)
    return BaseAPIResponse(data={"access_token": access_token, "token_type": "bearer"}, status=HTTPStatus.OK)

@app.post("/users", status_code=HTTPStatus.CREATED, dependencies=[Depends(verify_jwt_token)])
async def create_user(user: UserPayload):
    username, password, name = user.dict()
    result = await create_new_user(username=username, plain_password=password, name=name)
    return result


@app.get("/tasks/mine", response_model=List[Task])
async def get_my_tasks(user: User = Depends(verify_jwt_token), completed: bool = False):
    """ Get the tasks for a user ordered by their priority """
    return sorted(get_tasks_by_user(username=user.username, completed=completed), key=lambda task: task.priority)


@app.get("/tasks/{task_id}", dependencies=[Depends(verify_jwt_token)], response_model=Task)
async def get_task(task: Task = Depends(verify_task)) -> BaseAPIResponse:
    return get_task_by_id(id=task.id)


@app.post("/tasks", status_code=HTTPStatus.CREATED)
async def create_new_task(task: BaseTask, user = Depends(verify_jwt_token)):
    result = create_task(task_body=task, username=user.username)
    return {"id": result.get('id', None)}


@app.get("/tasks/{task_id}/comments", dependencies=[Depends(verify_jwt_token)], response_model=List[TaskComment])
async def get_comments_for_task(task: Task = Depends(verify_task)):
    return get_task_comments(task_id=task.id)


@app.patch("/tasks/{task_id}/comments", dependencies=[Depends(verify_jwt_token)], response_model=TaskComment)
async def add_new_task_comment(task: Task = Depends(verify_task), contents: str = Body(..., embed=True)): # embed is required as the payload only contains one key.
    """ Append a comment to an existing task """
    return add_task_comment(task_id=task.id, contents=contents)


@app.patch("/tasks/{task_id}/complete", dependencies=[Depends(verify_jwt_token)], status_code=HTTPStatus.NO_CONTENT)
async def complete_task(task: Task = Depends(verify_task)):
    return set_task_complete(task_id=task.id)


@app.delete("/tasks/{task_id}/complete", dependencies=[Depends(verify_jwt_token)], status_code=HTTPStatus.NO_CONTENT)
async def uncomplete_task(task: Task = Depends(verify_task)):
    return set_task_incomplete(task_id=task.id)

