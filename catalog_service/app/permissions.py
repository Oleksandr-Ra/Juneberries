def permission_required(permission: str):
    def decorator(func):
        setattr(func, 'required_permission', permission)
        return func
    return decorator
