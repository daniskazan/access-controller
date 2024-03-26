from core.models import Application
from core.enums.application import ApplicationStatusChoice


def change_application_status_to_confirm(*, application: Application) -> Application:
    application.status = ApplicationStatusChoice.APPROVED
    application.save()
    return application
