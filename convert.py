#!/usr/bin/env python3

import sys
import csv


# Do not forget to start over && remove all categories


# TODO: all non-transfer txs may be exported into single file with less fields

ZEN_FROM_HOME_FIELDS = {
    'date': 'date',                                     # single-acct version
    'categoryName': 'category',                         # single-acct version
    'payee': None,
    'comment': 'description',                           # single-acct version
    'outcomeAccountName': 'account',                    # single-acct version
    'outcome': 'total',                                 # single-acct version
    'outcomeCurrencyShortTitle': 'currency',
    'incomeAccountName': 'transfer',
    'income': 'total',
    'incomeCurrencyShortTitle': 'currency',
    'createdDate': 'date',
    'changedDate': 'date',
}
TRANSFER_ACCT = '_transfers'


def home_to_zen_format(row):
    ret = {}

    for zen_key, home_key in ZEN_FROM_HOME_FIELDS.items():
        home_val = row.get(home_key, '')

        # TODO: debt-transfers must have payee
        if zen_key == 'payee':
            home_val = 'me'

        ret[zen_key] = home_val

    return ret


def write_account_transactions(account, account_txs):
    if len(account_txs) == 0:
        return

    fields = account_txs[0].keys()
    filename = account + '.csv'

    with open(filename, 'w', encoding='utf-8') as ofd:
        writer = csv.DictWriter(ofd, fields)
        writer.writeheader()
        writer.writerows(account_txs)


def main(argv):
    if len(argv) < 2:
        print('specify input file')
        return 1

    prev_transfer = None
    transactions = {}           # map account -> transactions[]

    with open(argv[1], encoding='utf-8-sig') as ifd:
        reader = csv.DictReader(ifd, delimiter=';')

        for row in reader:
            account = row['account']

            # assume we are processing 2nd record
            transfer_from = row['transfer']

            if transfer_from:
                if prev_transfer:
                    same = True

                    same = same and prev_transfer['account'] == transfer_from
                    same = same and prev_transfer['transfer'] == row['account']
                    same = same and float(prev_transfer['total']) == float(row['total'])
                    same = same and prev_transfer['date'] == row['date']

                    if not same:
                        print('transfer discrepancy found: {}'.format(row))

                    prev_transfer = None
                    continue
                else:
                    row['total'] = -1 * float(row['total'])
                    prev_transfer = row.copy()

            zen_row = home_to_zen_format(row)

            key = TRANSFER_ACCT if transfer_from else account

            account_txs = transactions.get(key, [])
            account_txs.append(zen_row)
            transactions[key] = account_txs


    accounts = list(transactions.keys())
    accounts.remove(TRANSFER_ACCT)
    print('create the following accounts: {}'.format(accounts))

    for account, account_txs in transactions.items():
        write_account_transactions(account, account_txs)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
