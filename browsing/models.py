from django.db import models


class BrowsConf(models.Model):
    """ stores config-info used for browsing views """
    model_name = models.CharField(
        max_length=255, blank=True,
        help_text="The name of the model class you like to analyse."
    )
    label = models.CharField(
        max_length=255, blank=True, help_text="The label of the value of interest."
    )
    field_path = models.CharField(
        max_length=255, blank=True, help_text="The constructor of to the value of interest."
    )

    def __str__(self):
        return "{}.{} ({})".format(self.model_name, self.field_path, self.label)
