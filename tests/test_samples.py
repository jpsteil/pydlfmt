import csv
import os
import sys
from dataclasses import dataclass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pydlfmt import DataFormatter, Column


@dataclass
class Olympian:
    id: int
    name: str
    sex: str
    age: int
    height: str
    weight: str
    team: str
    noc: str
    games: str
    year: str
    season: str
    city: str
    sport: str
    event: str
    medal: str


def load_data():
    data = []

    with open(os.path.join("input", "data.csv"), "r") as csv_file:
        rdr = csv.DictReader(
            csv_file,
        )
        for row in rdr:
            record = Olympian(
                id=row["ID"],
                name=row["Name"],
                sex=row["Sex"],
                age=row["Age"],
                height=row["Height"],
                weight=row["Weight"],
                team=row["Team"],
                noc=row["NOC"],
                games=row["Games"],
                year=row["Year"],
                season=row["Season"],
                city=row["City"],
                sport=row["Sport"],
                event=row["Event"],
                medal=row["Medal"],
            )
            data.append(record)

    return data


class ReportBuilder(DataFormatter):
    def __init__(self, data=None, filename=None, user_id=None):
        super().__init__(data=data, filename=filename, user_id=user_id)

        self.columns = [
            Column("id"),
            Column("name"),
            Column("sex"),
            Column("age"),
            Column("year"),
            Column("team"),
        ]


def test_samples():
    data = load_data()

    rb = ReportBuilder(data=data)
    rb.to_pdf(filename=os.path.join("output", "sample.pdf"))
    rb.to_excel(
        filename=os.path.join("output", "sample.xlsx"),
        format_table=True,
    )

    df = DataFormatter(data=data)
    df.columns = [
        Column("id"),
        Column("name"),
        Column("sex"),
        Column("age"),
        Column("year"),
        Column("team"),
        Column("sport"),
    ]
    df.to_pdf(filename=os.path.join("output", "sample2.pdf"))
    df.to_excel(
        filename=os.path.join("output", "sample2.xlsx"),
        format_table=True,
    )


#
# if __name__ == "__main__":
#     data = load_data()
#
#     rb = ReportBuilder(data=data)
#     rb.to_pdf(filename=os.path.join("output", "sample.pdf"))
#     rb.to_excel(
#         filename=os.path.join("output", "sample.xlsx"),
#         format_table=True,
#     )
#
#     df = DataFormatter(data=data)
#     df.columns = [
#         Column("id"),
#         Column("name"),
#         Column("sex"),
#         Column("age"),
#         Column("year"),
#         Column("team"),
#         Column("sport"),
#     ]
#     df.to_pdf(filename=os.path.join("output", "sample2.pdf"))
#     df.to_excel(
#         filename=os.path.join("output", "sample2.xlsx"),
#         format_table=True,
#     )
