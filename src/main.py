from http import HTTPStatus

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from uuid import UUID
from datetime import datetime, timedelta
from typing import List

from models import BaseAPIResponse, UserPayload, BaseTask, User, Task
from queries import get_task_by_id, create_task, get_tasks_by_user, set_task_complete, set_task_incomplete
from authentication import authenticate_user, create_access_token, create_new_user, verify_jwt_token

app = FastAPI()

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> BaseAPIResponse:
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Username not found")
    access_token = create_access_token(username=user.username)
    return BaseAPIResponse(data={"access_token": access_token, "token_type": "bearer"}, status=HTTPStatus.OK)

@app.post("/users", status_code=HTTPStatus.CREATED, dependencies=[Depends(verify_jwt_token)])
async def create_user(user: UserPayload) -> BaseAPIResponse:
    user_dict = user.dict()
    result = await create_new_user(username=user_dict.username, plain_password=user_dict.password, name=user_dict.name)
    return result


@app.get("/tasks/mine", response_model=List[Task])
async def get_my_tasks(user: User = Depends(verify_jwt_token)):
    tasks = get_tasks_by_user(username=user.username)
    return tasks


@app.get("/tasks/{task_id}", dependencies=[Depends(verify_jwt_token)], response_model=Task)
async def get_task(task_id: UUID) -> BaseAPIResponse:
    task = get_task_by_id(id=task_id)
    if task is None:
        return HTTPException(HTTPStatus.NOT_FOUND)
    return task


@app.post("/tasks", status_code=HTTPStatus.CREATED)
async def create_new_task(task: BaseTask, user = Depends(verify_jwt_token)) -> BaseAPIResponse:
    result = create_task(task_body=task, username=user.username)
    return {"task_id": result.get('id', None)}


@app.patch("/tasks/{task_id}/complete", dependencies=[Depends(verify_jwt_token)], status_code=HTTPStatus.NO_CONTENT)
async def complete_task(task_id: UUID):
    completed_task = set_task_complete(task_id=task_id)

    if completed_task is None:
        return HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Task not found.")
    return None


@app.delete("/tasks/{task_id}/complete", dependencies=[Depends(verify_jwt_token)], status_code=HTTPStatus.NO_CONTENT)
async def uncomplete_task(task_id: UUID):
    uncompleted_task = set_task_incomplete(task_id=task_id)

    if uncompleted_task is None:
        return HTTPException(HTTPStatus.NOT_FOUND, detail="Task not found.")
    return None
