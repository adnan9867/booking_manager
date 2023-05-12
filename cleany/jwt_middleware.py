from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            try:
                token = headers[b'authorization'].decode()
                validated_token = JWTAuthentication().get_validated_token(token)
                user = await sync_to_async(JWTAuthentication().get_user)(validated_token)
                scope['user'] = user
            except Exception as e:
                pass
        return await self.app(scope, receive, send)
