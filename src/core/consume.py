from core.models import Grant


def create_grant_to_proccess(*, user_id: int, resource_id: int, application_id: int):
    grant = Grant(
        user_id=user_id, resource_id=resource_id, application_id=application_id
    )
    grant.save()
