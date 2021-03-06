#!/usr/bin/env python3

import sys
import csv


# Do not forget to start over && remove all categories


# TODO: all non-transfer txs may be exported into single file with less fields

ZEN_FROM_HOME_FIELDS = {
    'date': 'date',
    'categoryName': 'category',
    'comment': 'description',
    'outcomeAccountName': 'account',
    'outcome': 'total',
}
TRANSFER_FIELDS = ZEN_FROM_HOME_FIELDS.copy()
TRANSFER_FIELDS.update({
    'payee': None,
    'incomeAccountName': 'transfer',
    'income': 'total',
})


def home_to_zen_format(row, fields_map):
    ret = {}

    for zen_key, home_key in fields_map.items():
        home_val = row.get(home_key, '')

        if zen_key == 'payee':
            home_val = 'me'

        if isinstance(home_val, str):
            home_val = home_val.replace(',', '/')

        ret[zen_key] = home_val

    return ret


def dump_transactions(filename, transactions, limit=None):
    import math

    if len(transactions) == 0:
        return

    fields = transactions[0].keys()
    dump_map = {}

    if limit and limit > 1 and len(transactions) > limit-1:
        limit -= 1

        nfiles = math.ceil(len(transactions) / limit)
        for i in range(nfiles):
            fname = '{}-{:03d}.csv'.format(filename, i)
            start = i * limit
            end = start + limit

            dump_map[fname] = transactions[start:end]
    else:
        fname = filename + '.csv'
        dump_map[fname] = transactions

    for fname, txs in dump_map.items():
        with open(fname, 'w', encoding='utf-8') as ofd:
            writer = csv.DictWriter(ofd, fields)
            writer.writeheader()
            writer.writerows(txs)


def main(argv):
    if len(argv) < 2:
        print('specify input file')
        return 1

    prev_transfer = None
    transactions = []
    transfers = []
    accounts = set()

    with open(argv[1], encoding='utf-8-sig') as ifd:
        reader = csv.DictReader(ifd, delimiter=';')

        for row in reader:
            accounts.add(row['account'])

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

                zen_row = home_to_zen_format(row, TRANSFER_FIELDS)
                transfers.append(zen_row)
            else:
                zen_row = home_to_zen_format(row, ZEN_FROM_HOME_FIELDS)
                transactions.append(zen_row)


    print('create the following accounts: {}'.format(accounts))

    dump_transactions('transactions', transactions, limit=1000)
    dump_transactions('transfers', transfers, limit=1000)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
