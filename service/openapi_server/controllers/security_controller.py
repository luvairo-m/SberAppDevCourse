_DEMO_ROLES = {
    "demo-reader": "reader",
    "demo-editor": "editor",
}


def info_from_WorkshopToken(token):
    role = _DEMO_ROLES.get(token)
    if role is None:
        return None
    return {"sub": role, "role": role}
