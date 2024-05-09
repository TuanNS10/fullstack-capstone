
from datetime import datetime
from os import environ as env

from jwt import ExpiredSignatureError, InvalidTokenError, PyJWKClient
from dotenv import load_dotenv
from flask import request
from functools import wraps

import jwt



load_dotenv()


AUTH0_DOMAIN = env.get("AUTH0_DOMAIN")
ALGORITHMS = env.get("ALGORITHMS")
API_AUDIENCE = env.get("API_AUDIENCE")


## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header(): 
    auth_header = request.headers.get('Authorization', None)

    if not auth_header:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth_header.split()

    # If the header is not in the correct format or does not contain a token, raise AuthError
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be Bearer token.'
        }, 401)

    
    token = parts[1]
    return token

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    # # Ensure that payload is not None
    if payload is None:
        raise AuthError({
            'code': 'invalid_payload',
            'description': 'Payload is None or invalid.'
        }, 400)
    
    # Check if permissions are included in the payload
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    # Check if the requested permission string is in the payload permissions array
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)

    return True


'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    try:
        # Get the public key from Auth0 JWKS endpoint
        jwks_client = PyJWKClient(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # Decode the JWT and validate its signature
        decoded_token = jwt.decode(
            token,
            signing_key.key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,  # Specify your client ID
            issuer=f'https://{AUTH0_DOMAIN}/'
        )

        # Validate any additional claims (like expiration)
        if 'exp' in decoded_token:
            expiration = datetime.fromtimestamp(decoded_token['exp'])
            if expiration < datetime.now():
                raise ExpiredSignatureError("Token has expired.")

        # Return the decoded payload
        return decoded_token

    except InvalidTokenError as e:
        print(f"Token is invalid: {e}")
        return None
    except Exception as e:
        print(f"An error occurred while verifying the token: {e}")
        return None


'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
