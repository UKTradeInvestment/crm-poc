from migrator.managers import CDMSQuerySet


class CRMQuerySet(CDMSQuerySet):
    """
    This extends CDMSQuerySet, when it's time to get rid of CDMS,
    just extend models.Managers instead of CDMSQuerySet and all the
    related logic goes away.

    NOTE: to be used with core.models.CRMBaseModel.
    """
    pass
