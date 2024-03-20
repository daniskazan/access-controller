from django.db import models


class ApplicationStatusChoice(models.IntegerChoices):
    IN_PROCESS = 0, "In process"
    APPROVED = 1, "Approved"
    RESOLVED = 2, "Resolved"
