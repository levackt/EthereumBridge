abi = """[{'constant': True, 'inputs': [{'name': '', 'type': 'uint256'}], 'name': 'owners', 'outputs': [{'name': '', 'type': 'address'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'owner', 'type': 'address'}], 'name': 'removeOwner', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'transactionId', 'type': 'uint256'}], 'name': 'revokeConfirmation', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [{'name': '', 'type': 'address'}], 'name': 'isOwner', 'outputs': [{'name': '', 'type': 'bool'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': '', 'type': 'uint256'}, {'name': '', 'type': 'address'}], 'name': 'confirmations', 'outputs': [{'name': '', 'type': 'bool'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': 'pending', 'type': 'bool'}, {'name': 'executed', 'type': 'bool'}], 'name': 'getTransactionCount', 'outputs': [{'name': 'count', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'owner', 'type': 'address'}], 'name': 'addOwner', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [{'name': 'transactionId', 'type': 'uint256'}], 'name': 'isConfirmed', 'outputs': [{'name': '', 'type': 'bool'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': 'transactionId', 'type': 'uint256'}], 'name': 'getConfirmationCount', 'outputs': [{'name': 'count', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': '', 'type': 'uint256'}], 'name': 'transactions', 'outputs': [{'name': 'destination', 'type': 'address'}, {'name': 'value', 'type': 'uint256'}, {'name': 'data', 'type': 'bytes'}, {'name': 'executed', 'type': 'bool'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'getOwners', 'outputs': [{'name': '', 'type': 'address[]'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': 'from', 'type': 'uint256'}, {'name': 'to', 'type': 'uint256'}, {'name': 'pending', 'type': 'bool'}, {'name': 'executed', 'type': 'bool'}], 'name': 'getTransactionIds', 'outputs': [{'name': '_transactionIds', 'type': 'uint256[]'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [{'name': 'transactionId', 'type': 'uint256'}], 'name': 'getConfirmations', 'outputs': [{'name': '_confirmations', 'type': 'address[]'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'transactionCount', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': '_required', 'type': 'uint256'}], 'name': 'changeRequirement', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'transactionId', 'type': 'uint256'}], 'name': 'confirmTransaction', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'destination', 'type': 'address'}, {'name': 'value', 'type': 'uint256'}, {'name': 'data', 'type': 'bytes'}], 'name': 'submitTransaction', 'outputs': [{'name': 'transactionId', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'MAX_OWNER_COUNT', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'required', 'outputs': [{'name': '', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'view', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'owner', 'type': 'address'}, {'name': 'newOwner', 'type': 'address'}], 'name': 'replaceOwner', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'constant': False, 'inputs': [{'name': 'transactionId', 'type': 'uint256'}], 'name': 'executeTransaction', 'outputs': [], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'name': '_owners', 'type': 'address[]'}, {'name': '_required', 'type': 'uint256'}], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'constructor', 'name': 'constructor'}, {'payable': True, 'stateMutability': 'payable', 'type': 'fallback'}, {'anonymous': False, 'inputs': [{'indexed': True, 'name': 'sender', 'type': 'address'}, {'indexed': True, 'name': 'transactionId', 'type': 'uint256'}], 'name': 'Confirmation', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'name': 'sender', 'type': 'address'}, {'indexed': True, 'name': 'transactionId', 'type': 'uint256'}], 'name': 'Revocation', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'name': 'transactionId', 'type': 'uint256'}], 'name': 'Submission', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'name': 'transactionId', 'type': 'uint256'}], 'name': 'Withdraw', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'name': 'transactionId', 'type': 'uint256'}], 'name': 'WithdrawFailure', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'name': 'sender', 'type': 'address'}, {'indexed': False, 'name': 'value', 'type': 'uint256'}], 'name': 'Swap', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'name': 'owner', 'type': 'address'}], 'name': 'OwnerAddition', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'name': 'owner', 'type': 'address'}], 'name': 'OwnerRemoval', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'name': 'required', 'type': 'uint256'}], 'name': 'RequirementChange', 'type': 'event'}]"""