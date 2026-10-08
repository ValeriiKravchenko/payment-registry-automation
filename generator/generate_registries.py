"""Generate fictional payment registries in the "new contract" format.

Every value is invented: contract numbers start with 99, branches, names and
amounts are random but reproducible (fixed seed). Output:
  data/registries/<account ending>_<registry number>.txt  (cp1251, ';', 13 fields)
  data/contracts.csv                                     (contract -> branch lookup)
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 2026
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "registries"
LOOKUP = ROOT / "data" / "contracts.csv"

BRANCHES = ["Северный филиал", "Южный филиал", "Восточный филиал", "Западный филиал"]
ACCOUNT_ENDINGS = ["4417", "7302"]          # two collection accounts
START = date(2026, 3, 2)
DAYS = 10                                   # one registry per account per working day
SURNAMES = ["Иванов", "Петрова", "Смирнов", "Кузнецова", "Попов", "Васильева", "Соколов",
            "Морозова", "Новиков", "Фёдорова", "Волков", "Лебедева", "Козлов", "Егорова"]
SERVICES = ["водоснабжение", "водоотведение", "водоснабжение и водоотведение"]
MONTHS = ["январь", "февраль", "март"]


def money(x: float) -> str:
    return f"{x:.2f}".replace(".", ",")


def main() -> None:
    rnd = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.txt"):
        old.unlink()

    contracts = {f"99{rnd.randint(0, 99_999_999):08d}": rnd.choice(BRANCHES) for _ in range(40)}
    known = list(contracts)
    unknown = [f"99{rnd.randint(0, 99_999_999):08d}" for _ in range(2)]  # not in the lookup on purpose

    with LOOKUP.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Договор", "Филиал"])
        for num, branch in sorted(contracts.items()):
            w.writerow([num, branch])

    registry_no = 1200
    mismatch_done = False
    day = START
    made = 0
    while made < DAYS:
        if day.weekday() < 5:
            for acc in ACCOUNT_ENDINGS:
                registry_no += 1
                rows = []
                for i in range(rnd.randint(8, 15)):
                    num = rnd.choice(unknown) if rnd.random() < 0.03 else rnd.choice(known)
                    accepted = round(rnd.uniform(150, 9000), 2)
                    commission = 0.0 if rnd.random() < 0.2 else round(accepted * 0.01, 2)
                    transferred = round(accepted - commission, 2)
                    if not mismatch_done and made == 3 and i == 2:
                        transferred = round(transferred - 10, 2)   # one deliberate error for the check column
                        mismatch_done = True
                    name = f"{rnd.choice(SURNAMES)} {rnd.choice('АБВГДЕИКЛМНОПС')}.{rnd.choice('АБВГДЕИКЛМНОПС')}."
                    purpose = f"Оплата по договору {num} за {rnd.choice(SERVICES)} {rnd.choice(MONTHS)} 2026"
                    rows.append([
                        day.strftime("%d.%m.%Y"),                 # 1 payment date
                        f"{rnd.randint(10**8, 10**9 - 1)}",       # 2 operation id (unused)
                        f"{rnd.randint(8, 19):02d}:{rnd.randint(0, 59):02d}",  # 3 time (unused)
                        f"{rnd.randint(1000, 9999)}",            # 4 office code (unused)
                        f"T{rnd.randint(100, 999)}",             # 5 terminal (unused)
                        num,                                     # 6 contract / account
                        name,                                    # 7 payer
                        purpose,                                 # 8 payment purpose
                        "032026",                                # 9 period (unused)
                        "01",                                    # 10 service code (unused)
                        money(accepted),                         # 11 accepted
                        money(transferred),                      # 12 transferred
                        money(commission),                       # 13 commission
                    ])
                total_acc = sum(float(r[10].replace(",", ".")) for r in rows)
                total_tr = sum(float(r[11].replace(",", ".")) for r in rows)
                total_com = sum(float(r[12].replace(",", ".")) for r in rows)
                rows.append([f"Итого записей: {len(rows)}"] + [""] * 9 +
                            [money(total_acc), money(total_tr), money(total_com)])
                path = OUT / f"{acc}_{registry_no}.txt"
                with path.open("w", encoding="cp1251", newline="") as f:
                    for r in rows:
                        f.write(";".join(r) + "\r\n")
            made += 1
        day += timedelta(days=1)
    print(f"{len(list(OUT.glob('*.txt')))} registries, {len(contracts)} contracts in lookup, "
          f"{len(unknown)} contracts missing from it")


if __name__ == "__main__":
    main()
