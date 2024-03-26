from django.db import models


class ApplicationStatusChoice(models.IntegerChoices):
    IN_PROCESS = 0, "In process"
    APPROVED = 1, "Approved"
    RESOLVED = 2, "Resolved"


class ApplicationScopeChoice(models.IntegerChoices):
    READ_SCOPE = 0, "Read Scope"
    READ_AND_WRITE_SCOPE = 1, "Read and write scopes"
