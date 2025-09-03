import random
import copy
from prettytable import PrettyTable
import os

# ---------------- GLOBAL SETTINGS ----------------
ALL_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
OFF_DAYS = ["Sunday", "Saturday"]   # ✅ fixed off-days
DAYS = [d for d in ALL_DAYS if d not in OFF_DAYS]

PERIOD_TIMES = {
    1: "7:00 - 8:00",
    2: "8:00 - 9:00",
    3: "9:00 - 10:00",
    4: "10:00 - 11:00",
    5: "11:00 - 12:00",
    6: "12:00 - 1:00",
    7: "1:00 - 2:00",
    8: "2:00 - 3:00",
    9: "3:00 - 4:00",
    10: "4:00 - 5:00",
    11: "5:00 - 6:00",
    12: "6:00 - 7:00"
}


class GeneticScheduler:
    def __init__(self, subjects, faculties, batches, classrooms, days, periods_per_day, population_size=10):
        # Core "ingredients"
        self.subjects = subjects
        self.faculties = faculties
        self.batches = batches
        self.classrooms = classrooms
        self.days = days
        self.periods_per_day = periods_per_day
        self.population_size = population_size

        # Store generated candidate timetables
        self.population = []

    # ---------- POPULATION SETUP ----------
    def initialize_population(self):
        """Create initial random population."""
        self.population = [self.generate_random_timetable() for _ in range(self.population_size)]

    def generate_random_timetable(self):
        """Generate a timetable PER BATCH."""
        timetable = {}

        for batch in self.batches:
            timetable[batch] = {}
            for day in self.days:
                slots = []
                break_slot = random.choice([2, 3])
                for p in range(self.periods_per_day):
                    if p == break_slot:
                        slots.append({"subject": "BREAK", "faculty": None, "batch": batch, "classroom": None})
                    else:
                        subj = random.choice(self.subjects)
                        slots.append({
                            "subject": subj,
                            "faculty": subj.faculty,
                            "batch": batch,   # ✅ fixed: timetable belongs to this batch only
                            "classroom": random.choice(self.classrooms)
                        })
                timetable[batch][day] = slots
        return timetable


    # ---------- FITNESS FUNCTION ----------
    def fitness(self, timetable, debug=False):
        score = 100
        issues = []
        hard_violation = False

        for batch, days in timetable.items():
            for day, slots in days.items():
                subjects_seen = set()
                break_count = 0

                for i, slot in enumerate(slots):
                    if slot["subject"] == "BREAK":
                        break_count += 1
                        if i not in [2, 3]:
                            issues.append(f"Break in wrong slot for {batch.name} on {day}")
                            score -= 5
                        continue

                    subj, fac, bat, room = slot["subject"], slot["faculty"], slot["batch"], slot["classroom"]

                    # ❌ Hard constraint: No same subject twice in a day
                    if subj in subjects_seen:
                        issues.append(f"{batch.name}: Subject {subj.name} repeats on {day}")
                        hard_violation = True
                    subjects_seen.add(subj)

                    # ❌ Hard constraint: No faculty/room clash
                    for j, other_slot in enumerate(slots):
                        if j == i or other_slot["subject"] == "BREAK":
                            continue
                        if fac == other_slot["faculty"] or room == other_slot["classroom"]:
                            issues.append(f"{batch.name}: Clash at {day} slot {i+1}")
                            hard_violation = True

                # ❌ Hard constraint: exactly 1 break
                if break_count != 1:
                    issues.append(f"{batch.name}: {day} has {break_count} breaks instead of 1")
                    hard_violation = True

        if hard_violation:
            return 0, issues   # 🚨 reject this timetable completely
        return score, issues


    # ---------- GENETIC OPERATORS ----------
    def crossover(self, parent1, parent2):
        """Batch + day-wise crossover between two parents (safe across batches)."""
        child = {}

        # union of all batches across both parents
        all_batches = set(parent1.keys()) | set(parent2.keys())

        for batch in all_batches:
            child[batch] = {}
            for day in self.days:
                if batch in parent1 and batch in parent2:
                    # pick randomly from either parent
                    if random.random() < 0.5:
                        child[batch][day] = copy.deepcopy(parent1[batch][day])
                    else:
                        child[batch][day] = copy.deepcopy(parent2[batch][day])
                elif batch in parent1:
                    child[batch][day] = copy.deepcopy(parent1[batch][day])
                else:
                    child[batch][day] = copy.deepcopy(parent2[batch][day])

        return child

    def mutate(self, timetable):
        """Randomly change one slot in one batch (preserving break rules)."""
        mutated = copy.deepcopy(timetable)

        # pick a random batch first
        batch = random.choice(list(mutated.keys()))
        day = random.choice(self.days)

        period_index = random.randint(0, self.periods_per_day - 1)
        slot = mutated[batch][day][period_index]

        if slot["subject"] == "BREAK":
            return mutated  # don’t mutate breaks

        subj = random.choice(self.subjects)
        mutated[batch][day][period_index] = {
            "subject": subj,
            "faculty": subj.faculty,
            "batch": batch,  # ✅ keep consistent
            "classroom": random.choice(self.classrooms)
        }
        return mutated


    def mutate(self, timetable):
        """Randomly change one slot in one batch (preserving break rules)."""
        mutated = copy.deepcopy(timetable)

        # pick a random batch first
        batch = random.choice(list(mutated.keys()))
        day = random.choice(self.days)

        period_index = random.randint(0, self.periods_per_day - 1)
        slot = mutated[batch][day][period_index]

        if slot["subject"] == "BREAK":
            return mutated  # don’t mutate breaks

        subj = random.choice(self.subjects)
        mutated[batch][day][period_index] = {
            "subject": subj,
            "faculty": subj.faculty,
            "batch": batch,  # ✅ keep the same batch, don’t randomize
            "classroom": random.choice(self.classrooms)
        }
        return mutated


    # ---------- EVOLUTION LOOP ----------
    def evolve(self, generations=50):
        """Run the genetic algorithm for given generations."""
        for _ in range(generations):
            ranked = sorted(self.population, key=lambda t: self.fitness(t)[0], reverse=True)

            # Survivors: top 25% + random 25%
            survivors = ranked[:len(ranked)//4]
            survivors += random.sample(ranked[len(ranked)//4:], len(ranked)//4)

            # Generate children
            children = []
            while len(children) + len(survivors) < self.population_size:
                p1, p2 = random.sample(survivors, 2)
                child = self.crossover(p1, p2)
                if random.random() < 0.2:
                    child = self.mutate(child)
                children.append(child)

            self.population = survivors + children

    def run(self, generations=50):
        """Initialize + evolve, return best timetable."""
        self.initialize_population()
        self.evolve(generations)
        return max(self.population, key=lambda t: self.fitness(t)[0])

    # Print population report in terminal
    from prettytable import PrettyTable

    # ---------- TERMINAL REPORT ----------
    def print_population_report(self, best_only=False):
        """
        Print timetables, fitness scores, and issues in the terminal.
        :param best_only: if True, prints only the best timetable
        """
        timetables = (
            [max(self.population, key=lambda t: self.fitness(t)[0])]
            if best_only else self.population
        )

        for idx, timetable in enumerate(timetables, 1):
            score, issues = self.fitness(timetable)
            print(f"\n{'='*60}")
            print(f"Timetable #{idx} | Fitness Score: {score}")
            print(f"{'='*60}")

            # Pretty print per batch
            for batch, days in timetable.items():
                print(f"\nBatch: {batch.name}")
                table = PrettyTable()
                table.field_names = ["Day"] + [f"Period {i+1}" for i in range(self.periods_per_day)]

                for day in ALL_DAYS:   # also show OFF days
                    if day in OFF_DAYS:
                        table.add_row([day] + ["OFF"] * self.periods_per_day)
                    else:
                        row = [day]
                        for slot in days[day]:
                            if slot["subject"] == "BREAK":
                                row.append("BREAK")
                            else:
                                subj, fac, room = slot["subject"], slot["faculty"], slot["classroom"]
                                row.append(f"{subj.course_code} {subj.name}\n{fac.name}\n{room.name}")
                        table.add_row(row)

                print(table)

            # Print issues
            if issues:
                print("\n⚠ Issues:")
                for issue in issues:
                    print(f" - {issue}")
            else:
                print("\n✅ No issues found.")


    # ---------- PRETTY PRINT (HTML + Save to Project Folder) ----------
    def pretty_table(self, timetable):
        """Format multiple batch timetables as HTML tables (styled)."""
        full_html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #2c3e50; }
                h2 { margin-top: 30px; color: #8e44ad; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 40px; }
                th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
                th { background-color: #27ae60; color: white; }
                td.break { background-color: #f9e79f; font-weight: bold; }
                td.off { background-color: #d5d8dc; font-style: italic; }
            </style>
        </head>
        <body>
        <h1>Timetables</h1>
        """

        for batch, days in timetable.items():
            full_html += f"<h2> Batch: {batch.name}</h2>"
            full_html += "<table><tr><th>Day</th>"

            # Period headers
            for i in range(self.periods_per_day):
                full_html += f"<th>Period {i+1}<br>{PERIOD_TIMES[i+1]}</th>"
            full_html += "</tr>"

            # Day rows
            for day in ALL_DAYS:   # include off-days
                if day in OFF_DAYS:
                    full_html += f"<tr><td>{day}</td>" + "".join("<td class='off'>OFF</td>" for _ in range(self.periods_per_day)) + "</tr>"
                else:
                    full_html += f"<tr><td>{day}</td>"
                    for slot in days[day]:
                        if slot["subject"] == "BREAK":
                            full_html += "<td class='break'> BREAK</td>"
                        else:
                            subj, fac, room = slot["subject"], slot["faculty"], slot["classroom"]
                            full_html += f"<td><b>{subj.course_code} {subj.name}</b><br> {fac.name}<br>{room.name}</td>"
                    full_html += "</tr>"

            full_html += "</table>"

        full_html += """
        <br><a href='/download_timetable'>Download Timetable as HTML</a>
        </body></html>
        """

        # Save once to timetable.html
        file_path = os.path.join(os.path.dirname(__file__), "timetable.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        return full_html
