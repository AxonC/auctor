from authentication import create_access_token, create_new_user

username = 'callumaxon'

# create_new_user(username=username, plain_password='password', name='Callum Axon')

print(create_access_token(username=username, token_lifespan=1440))