{
    'name': "estate_account",

    'summary': "Generate a customer invoice when a real estate property is sold",

    'description': """
Interaction between the real_estate module and Odoo's Invoicing (account)
module: when a property is marked as Sold, an invoice is automatically
created for the buyer for 6% of the selling price plus a 100 admin fee.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Real Estate',
    'version': '0.1',

    # This module only makes sense if BOTH real_estate and the Invoicing
    # app (account) are installed.
    'depends': ['real_estate', 'account'],

    'data': [],

    'installable': True,
    'application': False,
}