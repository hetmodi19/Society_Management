"""
SmartSociety 360 - Centralized Role-Based Access Control (RBAC) & Object Permissions.
Follows: Role -> Permission -> Resource -> Action
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

# Matrix defining granular capabilities for each system role
ROLE_PERMISSIONS = {
    'ADMIN': {'*'},  # Super Admin has unrestricted operational and system capabilities

    'SECRETARY': {
        'dashboard.view', 'dashboard.secretary',
        'properties.view_all', 'properties.manage_units', 'properties.directory', 'properties.manage_helpers', 'properties.manage_violations', 'properties.manage_moves',
        'communications.view', 'communications.create_notice', 'communications.manage_notice', 'communications.create_poll', 'communications.manage_docs', 'communications.forum',
        'helpdesk.view_all', 'helpdesk.assign', 'helpdesk.update',
        'amenities.view', 'amenities.manage_approvals', 'amenities.view_ev',
        'gatekeeper.view_logs', 'gatekeeper.view_passes', 'gatekeeper.view_sos', 'gatekeeper.resolve_sos',
        'reports.view_operational', 'billing.view_summary',
    },

    'TREASURER': {
        'dashboard.view', 'dashboard.treasurer',
        'billing.view_all', 'billing.create_batch', 'billing.view_ledger', 'billing.manage_expenses', 'billing.create_expense', 'billing.approve_expense', 'billing.delete_bill', 'billing.delete_expense', 'billing.reconcile',
        'reports.view_financial', 'reports.export_financial',
        'properties.view_summary', 'properties.directory',
        'communications.view',
    },

    'ACCOUNTANT': {
        'dashboard.view', 'dashboard.treasurer',
        'billing.view_all', 'billing.create_batch', 'billing.view_ledger', 'billing.manage_expenses', 'billing.create_expense', 'billing.reconcile',
        'reports.view_financial', 'reports.export_financial',
        'properties.view_summary', 'properties.directory',
        'communications.view',
    },

    'COMMITTEE': {
        'dashboard.view', 'dashboard.committee',
        'properties.view_all', 'properties.directory', 'properties.view_violations',
        'billing.view_ledger',  # Read-only audit access
        'communications.view', 'communications.create_notice', 'communications.create_poll', 'communications.manage_docs', 'communications.forum',
        'helpdesk.view_all',
        'amenities.view', 'amenities.manage_approvals',
        'gatekeeper.view_sos', 'gatekeeper.resolve_sos',
        'reports.view_summary',
    },

    'FACILITY_MGR': {
        'dashboard.view', 'dashboard.facility',
        'amenities.view', 'amenities.manage_approvals', 'amenities.manage_ev',
        'helpdesk.view_all', 'helpdesk.assign', 'helpdesk.update',
        'properties.view_all', 'properties.manage_moves', 'properties.manage_staff', 'properties.directory',
        'gatekeeper.view_logs', 'gatekeeper.view_parcels', 'gatekeeper.view_sos', 'gatekeeper.resolve_sos',
        'reports.view_operational',
        'communications.view', 'communications.create_notice',
    },

    'OWNER': {
        'dashboard.view', 'dashboard.owner',
        'properties.view_own', 'properties.manage_own_vehicles', 'properties.manage_own_helpers', 'properties.directory',
        'billing.view_own', 'billing.pay_own',
        'gatekeeper.create_pass', 'gatekeeper.view_own_visitors', 'gatekeeper.view_own_parcels', 'gatekeeper.trigger_sos',
        'amenities.view', 'amenities.book', 'amenities.use_ev',
        'helpdesk.create', 'helpdesk.view_own',
        'communications.view', 'communications.vote_poll', 'communications.view_docs', 'communications.forum',
    },

    'TENANT': {
        'dashboard.view', 'dashboard.tenant',
        'properties.view_own_rented', 'properties.manage_own_vehicles', 'properties.directory',
        'billing.view_own_rented', 'billing.pay_own_rented',
        'gatekeeper.create_pass', 'gatekeeper.view_own_visitors', 'gatekeeper.view_own_parcels', 'gatekeeper.trigger_sos',
        'amenities.view', 'amenities.book', 'amenities.use_ev',
        'helpdesk.create', 'helpdesk.view_own',
        'communications.view', 'communications.view_docs', 'communications.forum',
    },

    'RESIDENT': {
        'dashboard.view', 'dashboard.owner',
        'properties.view_own', 'properties.manage_own_vehicles', 'properties.manage_own_helpers', 'properties.directory',
        'billing.view_own', 'billing.pay_own',
        'gatekeeper.create_pass', 'gatekeeper.view_own_visitors', 'gatekeeper.view_own_parcels', 'gatekeeper.trigger_sos',
        'amenities.view', 'amenities.book', 'amenities.use_ev',
        'helpdesk.create', 'helpdesk.view_own',
        'communications.view', 'communications.vote_poll', 'communications.view_docs', 'communications.forum',
    },

    'GUARD': {
        'dashboard.view', 'dashboard.guard',
        'gatekeeper.terminal', 'gatekeeper.entry', 'gatekeeper.checkout', 'gatekeeper.verify_pass', 'gatekeeper.manage_parcels', 'gatekeeper.view_sos', 'gatekeeper.resolve_sos',
        'properties.lookup_for_gate',
    },

    'STAFF': {
        'dashboard.view', 'dashboard.staff',
        'helpdesk.view_assigned', 'helpdesk.update_assigned', 'helpdesk.view_unassigned',
        'gatekeeper.view_sos',
    },
}


def has_perm(user, perm_code):
    """Check if user holds the specified permission code."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser or user.role == 'ADMIN':
        return True
    
    perms = ROLE_PERMISSIONS.get(user.role, set())
    if '*' in perms or perm_code in perms:
        return True
        
    return False


# --- Object-Level Security Checkers ---

def can_view_unit(user, unit):
    """Determine if a user can view detailed unit information."""
    if not user or not user.is_authenticated:
        return False
    if user.is_society_admin or user.is_secretary or user.is_committee_member or user.is_facility_manager or user.is_security_guard:
        return True
    # Resident / Tenant object-level check: must be owner or primary resident or mapped resident
    if unit.owner == user or unit.primary_resident == user:
        return True
    return unit.resident_mappings.filter(user=user, is_active=True).exists()


def can_manage_unit(user, unit=None):
    """Determine if user can modify unit architecture, floor, or ownership."""
    if not user or not user.is_authenticated:
        return False
    return user.is_society_admin or user.is_secretary


def can_view_bill(user, bill):
    """Determine if user has permission to view an itemized bill invoice."""
    if not user or not user.is_authenticated:
        return False
    if user.is_society_admin or user.is_financial_manager or user.is_committee_member or user.is_secretary:
        return True
    # Resident isolation
    return (
        bill.resident == user or
        bill.unit.owner == user or
        bill.unit.primary_resident == user or
        bill.unit.resident_mappings.filter(user=user, is_active=True).exists()
    )


def can_pay_bill(user, bill):
    """Determine if user can pay this invoice."""
    if not user or not user.is_authenticated:
        return False
    if user.is_society_admin:
        return True
    return (
        bill.resident == user or
        bill.unit.owner == user or
        bill.unit.primary_resident == user
    )


def can_view_ticket(user, ticket):
    """Determine if user can view a maintenance service ticket."""
    if not user or not user.is_authenticated:
        return False
    if user.is_society_admin or user.is_secretary or user.is_committee_member or user.is_facility_manager:
        return True
    if user.is_facility_staff:
        # Assigned staff or unassigned open ticket
        return ticket.assigned_staff == user or ticket.assigned_staff is None
    # Resident isolation
    return (
        ticket.resident == user or
        ticket.unit.owner == user or
        ticket.unit.primary_resident == user
    )


def can_update_ticket(user, ticket):
    """Determine if user can change ticket status or resolution details."""
    if not user or not user.is_authenticated:
        return False
    if user.is_society_admin or user.is_facility_manager or user.is_secretary:
        return True
    if user.is_facility_staff and ticket.assigned_staff == user:
        return True
    return False


def can_view_expense(user, expense=None):
    """Determine if user can access audited society expenses."""
    if not user or not user.is_authenticated:
        return False
    return user.is_society_admin or user.is_financial_manager or user.is_committee_member or user.is_secretary


def can_manage_expense(user, expense=None):
    """Determine if user can create, approve, or delete financial expenses."""
    if not user or not user.is_authenticated:
        return False
    return user.is_society_admin or user.is_treasurer
