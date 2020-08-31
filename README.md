# Auctor

Generic todo app written in Python using the FastAPI framework. Project is to explore FastAPI and hopefully use a sprinkling of maths to determine which tasks should be done first.

## Development
Opens the unicorn web server on port 8000.
```
cd src/ && unicorn main:app --port 8000 --reload
```

## Deployment
Deployment can be performed by building a docker container.
```docker
cd src/ && docker build -t auctor-api .

docker run -d --name {NAME} -p 80:{DESIRED_PORT} \
-e POSTGRES_HOST={POSTGRES_HOST} \
-e POSTGRES_PORT={POSTGRES_PORT} \
-e POSTGRES_USER={POSTGRES_USER} \
-e POSTGRES_PASSWORD={POSTGRES_PASSWORD} \ 
-e POSTGRES_DATABASE={POSTGRES_DATABASE} \
-e SECRET_KEY_AUTH={SECRET_KEY_AUTH}
auctor-api
```


### Environment Variables
All generally self-explanatory. Host must generally be on the same docker network if run in conjunction with other containers.

Secret key is used for password hashing & JWT generation.