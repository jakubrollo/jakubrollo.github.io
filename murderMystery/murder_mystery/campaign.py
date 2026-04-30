import random
import os
import re
from murder_mystery.game import MysteryGame
import clingo

class MysteryCampaign:


    CURSED_ROOM_STAY_PROBABILITY = 0.35

    def __init__(self, total_iterations=3):
        self.total_iterations = total_iterations
        self.solved_cases = 0
        self.meta_outcome = None

        self.random = random.Random()
        self.used_names = set()
        self.previous_youngest = []
        self.previous_cursed_room = None

        self.__load_domain_from_asp()

        available_weapons = list(MysteryGame.WEAPON_TEXTS.keys())
        self.random.shuffle(available_weapons)
        self.weapon_plan = available_weapons[:self.total_iterations]

        self.cursed_heirloom = self.random.choice(self.ITEM_POOL)
        self.meta_candidate_sets = self.__build_meta_candidate_sets()

    def __load_domain_from_asp(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        lp_path = os.path.join(base_dir, "3_murder_mystery.lp")
        
        ctl = clingo.Control(["--warn=none"])
        ctl.load(lp_path)
        ctl.ground([("base", [])])
        
        self.ROOM_POOL = []
        self.ITEM_POOL = []
        self.LETTERS = []
        self.LETTER_NAME_POOLS = {}
        
        for atom in ctl.symbolic_atoms:
            if not atom.is_fact:
                continue
            
            sym = atom.symbol
            if sym.name == "room_pool" and len(sym.arguments) == 1:
                self.ROOM_POOL.append(str(sym.arguments[0]))
            elif sym.name == "item_pool" and len(sym.arguments) == 1:
                self.ITEM_POOL.append(str(sym.arguments[0]))
            elif sym.name == "letter_pool" and len(sym.arguments) == 1:
                self.LETTERS.append(str(sym.arguments[0]))
            elif sym.name == "name_pool" and len(sym.arguments) == 3:
                letter = str(sym.arguments[0])
                gender = str(sym.arguments[1])
                name = str(sym.arguments[2])
                if letter not in self.LETTER_NAME_POOLS:
                    self.LETTER_NAME_POOLS[letter] = {"boy": [], "girl": []}
                self.LETTER_NAME_POOLS[letter][gender].append(name)
        
        self.LETTERS.sort()

    def start(self):
        print("=" * 60)
        print(" THE BLACKWOOD ESTATE CHRONICLES ")
        print("=" * 60)

        for iteration in range(1, self.total_iterations + 1):
            scenario = self.__build_scenario(iteration)
            player_role = self.random.choice([person["id"] for person in scenario["people"]])
            game = MysteryGame(scenario, player_role, self.total_iterations)
            game.start()

            if game.case_solved:
                self.solved_cases += 1

            if iteration == self.total_iterations:
                self.meta_outcome = game.meta_outcome

            self.previous_youngest = self.__select_next_youngest(scenario["people"])

            if iteration < self.total_iterations:
                print("\n--- Decades pass. A new generation inherits Blackwood Manor. ---\n")

        print("\n" + "=" * 60)
        print("Campaign complete.")
        print(f"Solved cases: {self.solved_cases}/{self.total_iterations}.")

        if self.meta_outcome == "win":
            print("The cursed heirloom was destroyed. Blackwood Manor is finally free.")
        elif self.meta_outcome == "loss":
            print("You burned the wrong item. The curse survives, and the manor remains damned.")
        else:
            print("The final curse ritual was left unresolved.")

    def __build_scenario(self, iteration):
        people, elders, victim_carry = self.__build_people(iteration)
        victim_profile = self.__build_victim_profile(people, elders, iteration, victim_carry)
        backstories = self.__build_backstories(people, iteration, elders)

        weapon_id = self.weapon_plan[iteration - 1]
        trait_atom = MysteryGame.WEAPON_TEXTS[weapon_id]["trait_atom"]

        candidate_items = list(self.meta_candidate_sets[iteration - 1])
        self.random.shuffle(candidate_items)

        confessor = self.random.choice([person["id"] for person in people])
        item_to_room = self.__build_item_room_map()
        visits = self.__build_visit_map(people, confessor, candidate_items, item_to_room)

        return {
            "iteration": iteration,
            "weapon_id": weapon_id,
            "trait_atom": trait_atom,
            "people": people,
            "elders": elders,
            "victim_profile": victim_profile,
            "backstories": backstories,
            "rooms": list(self.ROOM_POOL),
            "items": list(self.ITEM_POOL),
            "item_to_room": item_to_room,
            "visits": visits,
            "confessor": confessor,
            "candidate_items": candidate_items,
            "cursed_heirloom": self.cursed_heirloom,
        }

    def __build_meta_candidate_sets(self):
        if self.total_iterations != 3:
            raise ValueError("Meta-mystery requires exactly 3 generations.")

        distractors = [item for item in self.ITEM_POOL if item != self.cursed_heirloom]
        self.random.shuffle(distractors)
        d1, d2, d3, d4 = distractors[:4]

        candidate_sets = [
            [self.cursed_heirloom, d1, d2],
            [self.cursed_heirloom, d2, d3],
            [self.cursed_heirloom, d3, d4],
        ]

        for candidate_set in candidate_sets:
            self.random.shuffle(candidate_set)

        return candidate_sets

    def __build_item_room_map(self):
        rooms = list(self.ROOM_POOL)
        items = list(self.ITEM_POOL)
        self.random.shuffle(rooms)

        if self.previous_cursed_room and self.random.random() < self.CURSED_ROOM_STAY_PROBABILITY:
            cursed_room = self.previous_cursed_room
        else:
            cursed_room = self.random.choice(rooms)

        mapping = {self.cursed_heirloom: cursed_room}

        remaining_items = [item for item in items if item != self.cursed_heirloom]
        remaining_rooms = [room for room in rooms if room != cursed_room]
        self.random.shuffle(remaining_items)
        self.random.shuffle(remaining_rooms)

        for item, room in zip(remaining_items, remaining_rooms):
            mapping[item] = room

        self.previous_cursed_room = cursed_room
        return mapping

    def __build_visit_map(self, people, confessor, candidate_items, item_to_room):
        visits = {}

        confessor_rooms = sorted({item_to_room[item] for item in candidate_items})
        if len(confessor_rooms) != 3:
            raise ValueError("Each candidate set must map to exactly three distinct rooms.")
        visits[confessor] = confessor_rooms

        for person in people:
            person_id = person["id"]
            if person_id == confessor:
                continue

            sampled_rooms = sorted(self.random.sample(self.ROOM_POOL, 3))
            if sampled_rooms == confessor_rooms:
                alternatives = [room for room in self.ROOM_POOL if room not in sampled_rooms]
                replacement = self.random.choice(alternatives)
                sampled_rooms = sorted([sampled_rooms[0], sampled_rooms[1], replacement])

            visits[person_id] = sampled_rooms

        return visits

    def __build_people(self, iteration):
        people = []
        elders = []
        victim_carry = None

        if iteration == 1:
            boy_letters = set(self.random.sample(self.LETTERS, 2))
            for letter in self.LETTERS:
                gender = "boy" if letter in boy_letters else "girl"
                name_id = self.__pick_name(letter, gender)
                age = self.random.randint(18, 34)
                people.append(
                    {
                        "id": name_id,
                        "letter": letter,
                        "gender": gender,
                        "age": age,
                        "is_carryover": False,
                    }
                )
        else:
            survivor = self.random.choice(self.previous_youngest)
            victim_raw = [p for p in self.previous_youngest if p["id"] != survivor["id"]][0]

            carried = {
                "id": survivor["id"],
                "letter": survivor["letter"],
                "gender": survivor["gender"],
                "age": self.random.randint(58, 74) + (iteration - 2) * 2,
                "is_carryover": True,
            }
            people.append(carried)
            elders.append(carried["id"])

            victim_carry = {
                "id": victim_raw["id"],
                "letter": victim_raw["letter"],
                "gender": victim_raw["gender"],
                "age": self.random.randint(58, 74) + (iteration - 2) * 2,
            }

            carry_letters = {person["letter"] for person in people}
            missing_letters = [letter for letter in self.LETTERS if letter not in carry_letters]

            current_boys = sum(1 for person in people if person["gender"] == "boy")
            need_boys = 2 - current_boys
            boy_letters = set(self.random.sample(missing_letters, need_boys))

            for letter in missing_letters:
                gender = "boy" if letter in boy_letters else "girl"
                name_id = self.__pick_name(letter, gender)
                age = self.random.randint(18, 30)
                people.append(
                    {
                        "id": name_id,
                        "letter": letter,
                        "gender": gender,
                        "age": age,
                        "is_carryover": False,
                    }
                )

        people = sorted(people, key=lambda person: person["letter"])

        n_boys = sum(1 for person in people if person["gender"] == "boy")
        n_girls = sum(1 for person in people if person["gender"] == "girl")
        if n_boys != 2 or n_girls != 2:
            raise ValueError("Iteration roster must contain exactly two boys and two girls.")

        return people, elders, victim_carry

    def __pick_name(self, letter, gender):
        pool = self.LETTER_NAME_POOLS[letter][gender]
        available = [name for name in pool if name not in self.used_names]
        if not available:
            available = pool

        chosen = self.random.choice(available)
        self.used_names.add(chosen)
        return chosen

    def __build_victim_profile(self, people, elders, iteration, victim_carry):
        people_by_id = {person["id"]: person for person in people}
        disallowed_names = {person["id"] for person in people}

        if victim_carry:
            victim_id = victim_carry["id"]
            victim_gender = victim_carry["gender"]
            victim_age = victim_carry["age"]
            victim_story = (
                f"an elder of the family who survived the previous tragedy, "
                "only to be brutally murdered decades later."
            )
        else:
            oldest_age = max(person["age"] for person in people)
            oldest_candidates = [person for person in people if person["age"] == oldest_age]
            anchor = self.random.choice(oldest_candidates)
            victim_id, victim_gender = self.__pick_dead_name(
                anchor["letter"],
                anchor["gender"],
                disallowed_names,
            )
            victim_age = anchor["age"] + self.random.randint(10, 24)
            victim_story = (
                "a senior household member tied to this branch of the estate; "
                "their death is the spark for this case."
            )

        timeline = "in this first recorded case" if iteration == 1 else "after decades of family tension"
        victim_story = f"{victim_story} They fell {timeline}."

        return {
            "id": victim_id,
            "gender": victim_gender,
            "age": victim_age,
            "story": victim_story,
        }

    def __pick_dead_name(self, letter, preferred_gender, disallowed_names):
        primary_pool = list(self.LETTER_NAME_POOLS[letter][preferred_gender])
        secondary_gender = "girl" if preferred_gender == "boy" else "boy"
        secondary_pool = list(self.LETTER_NAME_POOLS[letter][secondary_gender])
        candidate_pool = primary_pool + secondary_pool

        available = [
            name
            for name in candidate_pool
            if name not in self.used_names and name not in disallowed_names
        ]
        if not available:
            available = [name for name in candidate_pool if name not in disallowed_names]
        if not available:
            available = candidate_pool

        chosen = self.random.choice(available)
        self.used_names.add(chosen)

        gender = "boy" if chosen in self.LETTER_NAME_POOLS[letter]["boy"] else "girl"
        return chosen, gender

    def __build_backstories(self, people, iteration, elders):
        backstories = {}
        for person in people:
            person_id = person["id"]
            if person_id in elders:
                backstories[person_id] = "an elder who survived the previous tragedy."
            elif iteration == 1:
                backstories[person_id] = "a suspect in this first recorded case."
            else:
                backstories[person_id] = "a suspect from the new generation."

        return backstories

    def __select_next_youngest(self, people):
        alive_people = sorted(people, key=lambda person: person["age"])
        return [
            {
                "id": person["id"],
                "letter": person["letter"],
                "gender": person["gender"],
                "age": person["age"],
            }
            for person in alive_people[:2]
        ]


