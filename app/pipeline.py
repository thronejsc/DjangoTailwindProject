from app.models import MyUser

def set_user_type(strategy, details, user=None, *args, **kwargs):
    if user and not user.user_type:
        user.user_type = 'student'
        user.save()

def pipeline(*args, **kwargs):
    return {
        'social_auth.pipeline.social_auth.social_user': {
            'kwargs': {
                'pipeline': set_user_type,
            },
            'args': args,
            'result': None,
        },
    }