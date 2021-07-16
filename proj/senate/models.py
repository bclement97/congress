from django.db import models


# class Party(models.Model):
#     code = models.CharField(max_length=1, primary_key=True)
#     name = models.CharField(max_length=50)


class PercentField(models.DecimalField):
    description = 'A percentage with 2 decimal places'

    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 4
        kwargs['decimal_places'] = 2
        super().__init__(*args, **kwargs)


class Senator(models.Model):
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50)
    suffix = models.CharField(max_length=20, null=True)
    date_of_birth = models.DateField()
    in_office = models.BooleanField()
    party = models.CharField(max_length=1)
    # party = models.ForeignKey(Party, on_delete=models.PROTECT)
    state = models.CharField(max_length=2)
    # leadership_role =
    # next_election may be better as an IntegerField (year),
    # but we're given a string
    next_election = models.CharField(max_length=50)
    total_votes = models.IntegerField()
    missed_votes = models.IntegerField()
    total_present = models.IntegerField()
    missed_votes_pct = PercentField()
    votes_with_party_pct = PercentField()
    votes_against_party_pct = PercentField()
    office = models.CharField(max_length=255)
    phone = models.CharField(max_length=12)
    fax = models.CharField(max_length=12)
    url = models.URLField()
    contact_form = models.URLField()
    source_id = models.CharField(max_length=7)
    source_uri = models.URLField()
    source_last_updated = models.DateTimeField()
    source_last_checked = models.DateTimeField()
    added_on = models.DateTimeField(auto_now_add=True)
