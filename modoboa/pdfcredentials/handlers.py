"""PDF credentials handlers."""

import os

from django.urls import reverse
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from modoboa.admin import signals as admin_signals
from modoboa.core import models as core_models
from modoboa.core import signals as core_signals
from modoboa.parameters import tools as param_tools

from .documents import credentials
from .lib import init_storage_dir, delete_credentials, get_creds_filename


@receiver(core_signals.account_password_updated)
def password_updated(sender, account, password, created, **kwargs):
    """Create or update document."""
    if not param_tools.get_global_parameter("enabled_pdfcredentials"):
        return
    generate_at_creation = param_tools.get_global_parameter(
        "generate_at_creation")
    if (generate_at_creation and not created) or account.is_superuser:
        return
    init_storage_dir()
    credentials(account, password)


@receiver(signals.pre_delete, sender=core_models.User)
def account_deleted(sender, instance, **kwargs):
    """Remove document."""
    delete_credentials(instance)


@receiver(core_signals.extra_account_actions)
def extra_account_actions(sender, account, **kwargs):
    """Add link to download document."""
    if not param_tools.get_global_parameter("enabled_pdfcredentials"):
        return []
    fname = get_creds_filename(account)
    if not os.path.exists(fname):
        return []
    return [{
        "name": "get_credentials",
        "url": reverse("pdfcredentials:account_credentials",
                       args=[account.id]),
        "img": "fa fa-download",
        "title": _("Retrieve user's credentials as a PDF document")
    }]


@receiver(admin_signals.extra_account_identities_actions)
def extra_identities_actions(sender, account, **kwargs):
    """
    Add download credential action for identity.
    Used for api v2.
    """
    if not param_tools.get_global_parameter("enabled_pdfcredentials"):
        return []
    fname = get_creds_filename(account)
    if not os.path.exists(fname):
        return []
    return {
        "name": "get_credentials",
        "body":  {"type": "pdfcredentials"},
        "icon": "mdi-file-download-outline",
        "label": _("Download PDF credentials")
    }
