# Checkout error codes

ERR-4010 means the payment gateway timed out. Ask the customer to retry after
five minutes. The amount, if deducted, is auto reversed within 48 hours.

ERR-4022 means the card was declined by the issuing bank. We cannot fix this,
the customer must contact their bank.

ERR-5021 means our inventory service did not respond while reserving stock. The
order is not created. Retrying usually works.

ERR-5090 means the address could not be validated for that pin code. Ask for a
nearby serviceable pin code.
