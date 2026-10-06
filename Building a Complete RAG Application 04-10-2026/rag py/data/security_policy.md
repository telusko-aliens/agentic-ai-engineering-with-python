# Internal security policy

Customer payment details are never stored in plain text. Card numbers are masked
to the last four digits everywhere, including logs.

Production database access needs an approved ticket and is granted for 8 hours
at a time. Access is logged and reviewed every month.

Employees must not paste customer data into external AI tools. Use the approved
internal assistant, which redacts personal data before the model sees it.

Any suspected data leak must be reported to the security team within 1 hour.
