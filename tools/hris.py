"""HRIS integration tools — leave management and employee data.

Supports multiple HRIS providers (BambooHR, Keka, Darwinbox) via a
provider abstraction. Includes a mock provider for development/testing.
"""

import logging
from datetime import date, datetime
from typing import Optional

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Module-level provider instance — set during initialization.
_provider = None


# ---------------------------------------------------------------------------
# Provider abstraction
# ---------------------------------------------------------------------------

class HRISProvider:
    """Base class for HRIS providers. Subclass and implement for each vendor."""

    def get_leave_balance(self, employee_id: str) -> dict:
        raise NotImplementedError

    def apply_leave(self, employee_id: str, leave_type: str,
                    start_date: str, end_date: str, reason: str) -> dict:
        raise NotImplementedError

    def get_employee_info(self, employee_id: str) -> dict:
        raise NotImplementedError

    def list_team_leaves(self, manager_id: str, month: str) -> list[dict]:
        raise NotImplementedError

    def list_employees(self, department: Optional[str] = None) -> list[dict]:
        raise NotImplementedError


class MockHRISProvider(HRISProvider):
    """Mock HRIS provider for development and testing."""

    _EMPLOYEES = {
        "EMP001": {"name": "Vaishak Bhuvan", "department": "Engineering", "role": "AIML Engineer", "manager": "EMP010"},
        "EMP002": {"name": "Priya Sharma", "department": "HR", "role": "HR Manager", "manager": "EMP010"},
        "EMP003": {"name": "Rahul Verma", "department": "Engineering", "role": "Backend Developer", "manager": "EMP001"},
        "EMP004": {"name": "Ananya Gupta", "department": "Product", "role": "Product Manager", "manager": "EMP010"},
        "EMP010": {"name": "Arjun Patel", "department": "Leadership", "role": "CTO", "manager": None},
    }

    _LEAVE_BALANCES = {
        "EMP001": {"casual": 8, "sick": 5, "earned": 12, "comp_off": 2},
        "EMP002": {"casual": 6, "sick": 5, "earned": 15, "comp_off": 0},
        "EMP003": {"casual": 10, "sick": 5, "earned": 8, "comp_off": 1},
        "EMP004": {"casual": 7, "sick": 4, "earned": 10, "comp_off": 0},
        "EMP010": {"casual": 12, "sick": 5, "earned": 20, "comp_off": 0},
    }

    _LEAVES_APPLIED = []

    def get_leave_balance(self, employee_id: str) -> dict:
        if employee_id not in self._LEAVE_BALANCES:
            return {"error": f"Employee {employee_id} not found"}
        balance = self._LEAVE_BALANCES[employee_id]
        emp = self._EMPLOYEES.get(employee_id, {})
        return {
            "employee_id": employee_id,
            "name": emp.get("name", "Unknown"),
            "balances": balance,
            "total_available": sum(balance.values()),
        }

    def apply_leave(self, employee_id: str, leave_type: str,
                    start_date: str, end_date: str, reason: str) -> dict:
        if employee_id not in self._EMPLOYEES:
            return {"error": f"Employee {employee_id} not found"}
        valid_types = {"casual", "sick", "earned", "comp_off"}
        if leave_type not in valid_types:
            return {"error": f"Invalid leave type. Valid: {', '.join(valid_types)}"}
        balance = self._LEAVE_BALANCES.get(employee_id, {})
        if balance.get(leave_type, 0) <= 0:
            return {"error": f"Insufficient {leave_type} leave balance"}

        leave_record = {
            "employee_id": employee_id,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason,
            "status": "pending_approval",
            "applied_on": date.today().isoformat(),
        }
        self._LEAVES_APPLIED.append(leave_record)
        return {"status": "success", "message": "Leave application submitted", "record": leave_record}

    def get_employee_info(self, employee_id: str) -> dict:
        if employee_id not in self._EMPLOYEES:
            return {"error": f"Employee {employee_id} not found"}
        emp = self._EMPLOYEES[employee_id].copy()
        emp["employee_id"] = employee_id
        return emp

    def list_team_leaves(self, manager_id: str, month: str) -> list[dict]:
        # Find direct reports
        reports = [
            eid for eid, emp in self._EMPLOYEES.items()
            if emp.get("manager") == manager_id
        ]
        # Filter leaves for the given month
        team_leaves = [
            leave for leave in self._LEAVES_APPLIED
            if leave["employee_id"] in reports and leave["start_date"].startswith(month)
        ]
        return team_leaves if team_leaves else [{"message": f"No leaves found for team in {month}"}]

    def list_employees(self, department: Optional[str] = None) -> list[dict]:
        results = []
        for eid, emp in self._EMPLOYEES.items():
            if department and emp["department"].lower() != department.lower():
                continue
            entry = emp.copy()
            entry["employee_id"] = eid
            results.append(entry)
        return results


class BambooHRProvider(HRISProvider):
    """BambooHR API integration. Requires base_url and api_key."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def get_leave_balance(self, employee_id: str) -> dict:
        # TODO: Implement BambooHR API call
        # GET {base_url}/api/gateway.php/{company}/v1/employees/{id}/time_off/calculator
        return {"error": "BambooHR integration not yet implemented. Use mock provider for testing."}

    def apply_leave(self, employee_id: str, leave_type: str,
                    start_date: str, end_date: str, reason: str) -> dict:
        return {"error": "BambooHR integration not yet implemented."}

    def get_employee_info(self, employee_id: str) -> dict:
        return {"error": "BambooHR integration not yet implemented."}

    def list_team_leaves(self, manager_id: str, month: str) -> list[dict]:
        return [{"error": "BambooHR integration not yet implemented."}]

    def list_employees(self, department: Optional[str] = None) -> list[dict]:
        return [{"error": "BambooHR integration not yet implemented."}]


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------

def _create_provider(config) -> HRISProvider:
    """Create the HRIS provider based on config."""
    provider_name = config.hris.provider
    if provider_name == "mock":
        return MockHRISProvider()
    elif provider_name == "bamboohr":
        return BambooHRProvider(config.hris.base_url, config.hris.api_key)
    else:
        logger.warning("HRIS provider '%s' not implemented, falling back to mock", provider_name)
        return MockHRISProvider()


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def get_leave_balance(employee_id: str) -> str:
    """Get the leave balance for an employee.

    Args:
        employee_id: The employee's ID (e.g., EMP001).

    Returns a breakdown of available leave by type (casual, sick, earned, comp-off).
    """
    if _provider is None:
        return "HRIS not configured. Enable it in config.yaml."
    result = _provider.get_leave_balance(employee_id)
    if "error" in result:
        return f"Error: {result['error']}"
    lines = [f"## Leave Balance: {result['name']} ({employee_id})\n"]
    for leave_type, balance in result["balances"].items():
        lines.append(f"- **{leave_type.replace('_', ' ').title()}**: {balance} days")
    lines.append(f"\n**Total available**: {result['total_available']} days")
    return "\n".join(lines)


@tool
def apply_leave(employee_id: str, leave_type: str, start_date: str, end_date: str, reason: str) -> str:
    """Apply for leave on behalf of an employee.

    Args:
        employee_id: The employee's ID.
        leave_type: Type of leave — casual, sick, earned, or comp_off.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        reason: Reason for the leave.

    This action requires approval before execution.
    """
    if _provider is None:
        return "HRIS not configured. Enable it in config.yaml."
    result = _provider.apply_leave(employee_id, leave_type, start_date, end_date, reason)
    if "error" in result:
        return f"Error: {result['error']}"
    record = result["record"]
    return (
        f"Leave application submitted.\n"
        f"- **Type**: {record['leave_type']}\n"
        f"- **Period**: {record['start_date']} to {record['end_date']}\n"
        f"- **Reason**: {record['reason']}\n"
        f"- **Status**: {record['status']}"
    )


@tool
def get_employee_info(employee_id: str) -> str:
    """Get employee information (name, department, role, manager).

    Args:
        employee_id: The employee's ID.
    """
    if _provider is None:
        return "HRIS not configured. Enable it in config.yaml."
    result = _provider.get_employee_info(employee_id)
    if "error" in result:
        return f"Error: {result['error']}"
    lines = [f"## Employee: {result.get('name', 'Unknown')}\n"]
    for key, value in result.items():
        if value is not None:
            lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
    return "\n".join(lines)


@tool
def list_team_leaves(manager_id: str, month: str) -> str:
    """List all leaves for a manager's team in a given month.

    Args:
        manager_id: The manager's employee ID.
        month: Month in YYYY-MM format (e.g., 2026-04).
    """
    if _provider is None:
        return "HRIS not configured. Enable it in config.yaml."
    results = _provider.list_team_leaves(manager_id, month)
    if not results or (len(results) == 1 and "message" in results[0]):
        return results[0].get("message", "No leaves found.") if results else "No leaves found."
    lines = [f"## Team Leaves for {month}\n"]
    for leave in results:
        lines.append(
            f"- **{leave['employee_id']}**: {leave['leave_type']} "
            f"({leave['start_date']} to {leave['end_date']}) — {leave.get('status', 'unknown')}"
        )
    return "\n".join(lines)


@tool
def list_employees(department: Optional[str] = None) -> str:
    """List employees, optionally filtered by department.

    Args:
        department: Optional department name to filter by (e.g., Engineering, HR, Product).
    """
    if _provider is None:
        return "HRIS not configured. Enable it in config.yaml."
    results = _provider.list_employees(department)
    if not results:
        return f"No employees found{f' in {department}' if department else ''}."
    header = f"## Employees{f' — {department}' if department else ''}\n"
    lines = [header]
    for emp in results:
        lines.append(
            f"- **{emp.get('name', 'Unknown')}** ({emp['employee_id']}) — "
            f"{emp.get('role', 'N/A')}, {emp.get('department', 'N/A')}"
        )
    return "\n".join(lines)


def get_hris_tools(config) -> list:
    """Initialize the HRIS provider and return all HRIS tools.

    Called by load_tools.py when hris.enabled is True in config.
    """
    global _provider
    try:
        _provider = _create_provider(config)
        logger.info("HRIS provider initialized: %s", config.hris.provider)
    except Exception as exc:
        logger.warning("HRIS initialization failed: %s", exc)

    return [get_leave_balance, apply_leave, get_employee_info, list_team_leaves, list_employees]
