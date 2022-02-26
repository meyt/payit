Payit
=====

.. image:: https://travis-ci.org/meyt/payit.svg?branch=master
    :target: https://travis-ci.org/meyt/payit

.. image:: https://coveralls.io/repos/github/meyt/payit/badge.svg?branch=master
    :target: https://coveralls.io/github/meyt/payit?branch=master

.. image:: https://img.shields.io/pypi/pyversions/payit.svg
    :target: https://pypi.python.org/pypi/payit

Online payment gateways wrapper library. 💳


Supported Gateways
------------------

(Iran)

- Aqayepardakht
- AsanPardakht
- Bahamta
- IranKish
- Mellat
- Parsian (PECCO)
- Pay.ir
- Zarinpal


Install
-------

.. code-block:: bash

    pip install payit


Usage
-----

.. code-block:: python

    from payit import (
        GatewayManager,
        gateways,
        Transaction,
        TransactionAlreadyPaidError
    )

    # Configure:
    config = {
        'mellat': {
            'terminal_id': '1234',
            'username': 'demo',
            'password': 'demo',
            'callback_url': 'http://localhost/callback/mellat'
        },
        'zarinpal1': {
            'merchant': '534534534532225234234',
            'description': '',
            'callback_url': 'http://localhost/callback/zarinpal1'
        },
        'zarinpal2': {
            'merchant': '33333333532225234234',
            'description': '',
            'callback_url': 'http://localhost/callback/zarinpal2'
        }
    }
    manager = GatewayManager()
    manager.register('mellat', gateways.MellatGateway)
    manager.register('zarinpal1', gateways.ZarinpalGateway)
    manager.register('zarinpal2', gateways.ZarinpalGateway)
    manager.configure(config)


    # Make Transaction:
    my_database = {}
    selected_gateway = 'zarinpal1'
    try:
        transaction = Transaction(amount=1500, order_id=11002)
        transaction = manager.request(selected_gateway, transaction)
        # Store `transaction.id` on your database
        my_database['transaction_id'] = transaction.id

        # Get redirection details
        redirection = manager.get_redirection(selected_gateway, transaction)

        # Now redirect your client to gateway by redirection details

    except PayitException:
        print('Something wrong on payment')
        raise


    # Callback
    # Now user backs from gateway to complete payment procedure
    selected_gateway = 'zarinpal1'
    try:
        callback_data = {
            'Authority': 101
        }
        transaction = manager.validate(selected_gateway, callback_data)
        if not transaction.validate_status:
            raise RuntimeError('Transaction is not valid')

        # Check `transaction.id` exist on your database
        if transaction.id not in my_database:
            raise RuntimeError('Transaction is not exists')

        # Now verify transaction
        manager.verify(selected_gateway, callback_data)

    except TransactionAlreadyPaidError:
        print('Transaction Already Paid')
        raise

    except PayitException:
        print('Something wrong on payment')
        raise

    # Payment succeed! 🎉

