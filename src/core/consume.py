from core.enums.application import ApplicationStatusChoice
from core.models import Grant, Application


def create_grant_to_proccess(*, user_id: int, resource_id: int, application_id: int):
    grant = Grant(
        user_id=user_id, resource_id=resource_id, application_id=application_id
    )
    grant.save()


def update_application_status_after_creating_grant(
    *,
    application_id: int,
) -> None:
    application = Application.objects.filter(pk=application_id).first()
    application.status = ApplicationStatusChoice.RESOLVED
    application.save()
