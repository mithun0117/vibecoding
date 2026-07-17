"""
Employee Payroll System
========================
A console-based payroll application that:
    - Accepts employee details (name, ID, basic salary, allowances, etc.)
    - Calculates gross salary, tax, and net salary
    - Uses classes, functions, input validation, and formatted output

Tax calculation uses a simple progressive slab system (editable in
PayrollCalculator.TAX_SLABS) so it can be adapted to any jurisdiction.
"""

import re
from datetime import date


# --------------------------------------------------------------------------
# Employee: a simple data-holding class
# --------------------------------------------------------------------------

class Employee:
    """Represents a single employee's payroll-relevant details."""

    def __init__(self, emp_id, name, department, basic_salary,
                 hra=0.0, transport_allowance=0.0, other_allowance=0.0,
                 provident_fund_rate=0.12):
        self.emp_id = emp_id
        self.name = name
        self.department = department
        self.basic_salary = basic_salary
        self.hra = hra                              # House Rent Allowance
        self.transport_allowance = transport_allowance
        self.other_allowance = other_allowance
        self.provident_fund_rate = provident_fund_rate  # fraction of basic salary

    def __repr__(self):
        return f"Employee({self.emp_id}, {self.name!r})"


# --------------------------------------------------------------------------
# PayrollCalculator: performs the actual salary/tax computation
# --------------------------------------------------------------------------

class PayrollCalculator:
    """
    Computes gross salary, tax, deductions, and net salary for an Employee.

    Tax slabs are annual, expressed as (upper_limit, rate). The final
    tuple should have upper_limit = None to represent "and above".
    Adjust these values to match the tax rules you need.
    """

    TAX_SLABS = [
        (250_000, 0.00),
        (500_000, 0.05),
        (1_000_000, 0.20),
        (None, 0.30),
    ]

    def __init__(self, employee):
        self.employee = employee

    # ---- salary components -------------------------------------------

    def monthly_gross(self):
        """Gross monthly salary = basic + all allowances."""
        e = self.employee
        return round(e.basic_salary + e.hra + e.transport_allowance + e.other_allowance, 2)

    def annual_gross(self):
        return round(self.monthly_gross() * 12, 2)

    def provident_fund_deduction(self):
        """Monthly PF deduction, based on basic salary only."""
        e = self.employee
        return round(e.basic_salary * e.provident_fund_rate, 2)

    # ---- tax -----------------------------------------------------------

    def annual_tax(self):
        """
        Progressive slab-based tax calculated on annual gross income.
        Each slab's rate applies only to the income within that slab.
        """
        income = self.annual_gross()
        tax = 0.0
        previous_limit = 0

        for upper_limit, rate in self.TAX_SLABS:
            if upper_limit is None:
                taxable_in_slab = income - previous_limit
            else:
                taxable_in_slab = min(income, upper_limit) - previous_limit

            if taxable_in_slab > 0:
                tax += taxable_in_slab * rate

            if upper_limit is not None and income <= upper_limit:
                break
            previous_limit = upper_limit if upper_limit is not None else previous_limit

        return round(tax, 2)

    def monthly_tax(self):
        return round(self.annual_tax() / 12, 2)

    # ---- net salary ------------------------------------------------------

    def monthly_net_salary(self):
        """Net salary = gross - tax - provident fund deduction."""
        gross = self.monthly_gross()
        deductions = self.monthly_tax() + self.provident_fund_deduction()
        return round(gross - deductions, 2)

    def summary(self):
        """Return a dictionary summarizing all payroll figures."""
        return {
            "monthly_gross": self.monthly_gross(),
            "annual_gross": self.annual_gross(),
            "provident_fund": self.provident_fund_deduction(),
            "monthly_tax": self.monthly_tax(),
            "annual_tax": self.annual_tax(),
            "monthly_net_salary": self.monthly_net_salary(),
        }


# --------------------------------------------------------------------------
# Input validation helpers
# --------------------------------------------------------------------------

def prompt_nonempty(message):
    """Keep asking until a non-empty string is entered."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("  This field cannot be empty. Please try again.")


def prompt_emp_id(message="Employee ID (e.g. EMP001): "):
    """Employee ID must be alphanumeric, 3-10 characters."""
    while True:
        value = input(message).strip().upper()
        if re.fullmatch(r"[A-Z0-9]{3,10}", value):
            return value
        print("  Invalid ID. Use 3-10 letters/digits only (e.g. EMP001).")


def prompt_non_negative_float(message):
    """Keep asking until a valid non-negative number is entered."""
    while True:
        raw = input(message).strip()
        try:
            value = float(raw)
            if value < 0:
                print("  Value cannot be negative. Please try again.")
                continue
            return value
        except ValueError:
            print("  Please enter a valid number.")


def prompt_percentage(message, default_percent):
    """Ask for a percentage (0-100); Enter accepts the default."""
    while True:
        raw = input(f"{message} [default {default_percent}%]: ").strip()
        if raw == "":
            return default_percent / 100.0
        try:
            value = float(raw)
            if 0 <= value <= 100:
                return value / 100.0
            print("  Percentage must be between 0 and 100.")
        except ValueError:
            print("  Please enter a valid number.")


# --------------------------------------------------------------------------
# Formatted output
# --------------------------------------------------------------------------

def print_header(title):
    print("\n" + "=" * 58)
    print(title.center(58))
    print("=" * 58)


def print_payslip(employee, summary):
    """Print a neatly formatted payslip."""
    print_header("PAYSLIP")
    print(f"{'Employee ID':<22}: {employee.emp_id}")
    print(f"{'Name':<22}: {employee.name}")
    print(f"{'Department':<22}: {employee.department}")
    print(f"{'Pay Date':<22}: {date.today().strftime('%Y-%m-%d')}")
    print("-" * 58)

    print(f"{'EARNINGS':<30}{'AMOUNT ($)':>28}")
    print(f"{'  Basic Salary':<30}{employee.basic_salary:>28,.2f}")
    print(f"{'  HRA':<30}{employee.hra:>28,.2f}")
    print(f"{'  Transport Allowance':<30}{employee.transport_allowance:>28,.2f}")
    print(f"{'  Other Allowance':<30}{employee.other_allowance:>28,.2f}")
    print("-" * 58)
    print(f"{'  Monthly Gross Salary':<30}{summary['monthly_gross']:>28,.2f}")
    print()

    print(f"{'DEDUCTIONS':<30}{'AMOUNT ($)':>28}")
    print(f"{'  Income Tax (monthly)':<30}{summary['monthly_tax']:>28,.2f}")
    print(f"{'  Provident Fund':<30}{summary['provident_fund']:>28,.2f}")
    print("-" * 58)
    total_deductions = summary['monthly_tax'] + summary['provident_fund']
    print(f"{'  Total Deductions':<30}{total_deductions:>28,.2f}")
    print()

    print("=" * 58)
    print(f"{'NET SALARY (MONTHLY)':<30}{summary['monthly_net_salary']:>28,.2f}")
    print("=" * 58)
    print(f"(Annual Gross: ${summary['annual_gross']:,.2f}  |  "
          f"Annual Tax: ${summary['annual_tax']:,.2f})")


# --------------------------------------------------------------------------
# Main program flow
# --------------------------------------------------------------------------

def collect_employee_details():
    """Prompt the user for all employee details, with validation."""
    print_header("Enter Employee Details")

    emp_id = prompt_emp_id()
    name = prompt_nonempty("Full name: ")
    department = prompt_nonempty("Department: ")
    basic_salary = prompt_non_negative_float("Basic monthly salary ($): ")
    hra = prompt_non_negative_float("HRA - House Rent Allowance ($): ")
    transport_allowance = prompt_non_negative_float("Transport allowance ($): ")
    other_allowance = prompt_non_negative_float("Other allowance ($): ")
    pf_rate = prompt_percentage("Provident Fund rate (% of basic salary)", default_percent=12)

    return Employee(
        emp_id=emp_id,
        name=name,
        department=department,
        basic_salary=basic_salary,
        hra=hra,
        transport_allowance=transport_allowance,
        other_allowance=other_allowance,
        provident_fund_rate=pf_rate,
    )


def process_one_employee():
    employee = collect_employee_details()
    calculator = PayrollCalculator(employee)
    summary = calculator.summary()
    print_payslip(employee, summary)


def main():
    print_header("EMPLOYEE PAYROLL SYSTEM")
    print("Calculates gross salary, tax, and net salary for employees.")

    while True:
        process_one_employee()

        again = input("\nProcess another employee? (y/n): ").strip().lower()
        if again != "y":
            print("\nPayroll session complete. Goodbye!")
            break


if __name__ == "__main__":
    main()
