from simple_clingo import SimpleClingo
import os
import re
import time

class MysteryGame:
    WEAPON_TEXTS = {
        "poisoned_cognac": {
            "trait_atom": "drinks_cognac",
            "murder_text": "poisoned via evening Cognac",
            "trait_desc": "be a Cognac drinker",
            "has_trait": "Cognac Drinker",
            "no_trait": "Abstainer",
        },
        "revolver": {
            "trait_atom": "owns_gun",
            "murder_text": "shot point-blank with a Revolver",
            "trait_desc": "own a gun",
            "has_trait": "Gun Owner",
            "no_trait": "Unarmed",
        },
        "heavy_candlestick": {
            "trait_atom": "is_strong",
            "murder_text": "bludgeoned with a Heavy Candlestick",
            "trait_desc": "possess great physical strength",
            "has_trait": "Strong",
            "no_trait": "Weak",
        },
        "dagger": {
            "trait_atom": "is_agile",
            "murder_text": "stabbed with a ceremonial Dagger",
            "trait_desc": "be highly agile",
            "has_trait": "Agile",
            "no_trait": "Clumsy",
        },
    }

    TRAIT_REVEAL_LINES = {
        "Cognac Drinker": "\"I will not lie about it: I do drink Cognac regularly.\"",
        "Abstainer": "\"Not a single drop of liquor passes my lips. I am an abstainer.\"",
        "Gun Owner": "\"I legally keep a firearm; yes, I am a gun owner.\"",
        "Unarmed": "\"I own no firearm at all. I am unarmed.\"",
        "Strong": "\"I have the build for hard labor; I am strong.\"",
        "Weak": "\"Physical force is not my gift. I am weak.\"",
        "Agile": "\"I move quickly and lightly; I am agile.\"",
        "Clumsy": "\"Grace has never favored me; I am undeniably clumsy.\"",
    }

    class ActionInfo:
        action_pattern = re.compile("([^<>]+)")
        arg_pattern = re.compile("<([^>]+)>")

        def __init__(self, command, method_name, help_text, automatic_validation=True, min_args=None, max_args=None):
            self.command = command
            self.command_base = self.action_pattern.match(command).group(0).rstrip()
            self.argument_names = self.arg_pattern.findall(command)
            self.method_name = method_name
            self.help_text = help_text
            self.automatic_validation = automatic_validation
            expected_args = len(self.argument_names)
            self.min_args = expected_args if min_args is None else min_args
            self.max_args = expected_args if max_args is None else max_args

        def matches(self, user_input):
            return user_input.startswith(self.command_base)

        def extract_args(self, user_input):
            args = user_input[len(self.command_base) + 1 :]
            args = [x for x in map(lambda s: s.strip(), args.split(" ")) if x != ""]
            if len(args) < self.min_args or len(args) > self.max_args:
                return "Invalid number of arguments for action"
            return args

    default_actions = [
        ActionInfo("?", "__help", "shows this help", automatic_validation=False),
        ActionInfo("review rules", "__review_rules", "reminds you of the facts of the case", automatic_validation=False),
        ActionInfo("list people", "__list_people", "lists all living suspects", automatic_validation=False),
        ActionInfo("list rooms", "__list_rooms", "lists all rooms you can explore", automatic_validation=False),
        ActionInfo("go <room>", "__go_room", "move to a room", automatic_validation=True),
        ActionInfo("examine <room>", "__examine_room", "inspect room contents", automatic_validation=True),
        ActionInfo("inventory", "__inventory", "shows items currently held", automatic_validation=False),
        ActionInfo("take <item>", "__take_item", "pick up an item (unlocked in final generation)", automatic_validation=True),
        ActionInfo("burn <item>", "__burn_item", "burn a held item in the living room fireplace", automatic_validation=True),
        ActionInfo("interrogate <person>", "__interrogate_person", "question a suspect (beliefs, or a guaranteed-truth personal trait)", automatic_validation=True),
        ActionInfo(
            "accuse <person>",
            "__accuse_people",
            "accuse one suspect or a pair (e.g. accuse arthur / accuse charles diana)",
            automatic_validation=True,
            min_args=1,
            max_args=2,
        ),
        ActionInfo("end case", "__end_case", "end the case after a correct accusation", automatic_validation=False),
        ActionInfo("quit", "__quit", "quits the game", automatic_validation=False),
    ]

    def __init__(self, scenario, player_role="inspector", total_iterations=3):

        self.scenario = scenario
        self.iteration = scenario["iteration"]
        self.total_iterations = total_iterations
        self.player_role = player_role

        self.people_info = {person["id"]: person for person in scenario["people"]}
        self.backstories = scenario["backstories"]

        self.rooms = sorted(scenario["rooms"])
        self.items = sorted(scenario["items"])
        self.item_locations = dict(scenario["item_to_room"])
        self.room_items = {room: [] for room in self.rooms}
        for item, room in self.item_locations.items():
            self.room_items[room].append(item)
        for room in self.room_items:
            self.room_items[room].sort()

        self.current_room = "living_room" if "living_room" in self.rooms else self.rooms[0]
        self.fireplace_room = "living_room" if "living_room" in self.rooms else self.current_room
        self.inventory_items = []

        self.cursed_heirloom = scenario["cursed_heirloom"]
        self.confessor = scenario["confessor"]
        self.confession_rooms = scenario["visits"][self.confessor]
        self.candidate_items = scenario["candidate_items"]

        self.finale_unlocked = False
        self.meta_outcome = None
        
        self.post_accusation_phase = False

        clingo = SimpleClingo()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        clingo.load_path(os.path.join(base_dir, "3_murder_mystery.lp"))

        for person in scenario["people"]:
            clingo.add_clause(f"person({person['id']}).")

        for elder in scenario["elders"]:
            clingo.add_clause(f"elder({elder}).")

        for room in scenario["rooms"]:
            clingo.add_clause(f"room({room}).")

        for item in scenario["items"]:
            clingo.add_clause(f"item({item}).")

        for item, room in scenario["item_to_room"].items():
            clingo.add_clause(f"item_in_room({item}, {room}).")

        for person_id, visited_rooms in scenario["visits"].items():
            for room in visited_rooms:
                clingo.add_clause(f"visited({person_id}, {room}).")

        clingo.add_clause(f"cursed_heirloom({scenario['cursed_heirloom']}).")
        clingo.add_clause(f"murderer({self.confessor}).")

        clingo.add_clause(f"selected_weapon({scenario['weapon_id']}, {scenario['trait_atom']}).")
        clingo.add_clause(f"victim({scenario['victim_profile']['id']}).")

        solutions = clingo.solve()
        if not solutions:
            raise ValueError("Failed to generate a mystery for this iteration.")

        self.model = solutions[0]

        weapon_data = self.model.get("selected_weapon", [])[0]
        self.weapon_id = weapon_data[0]
        self.trait_name = weapon_data[1]
        self.victim = self.model.get("victim", [scenario["victim_profile"]["id"]])[0]
        self.victim_profile = scenario["victim_profile"]

        self.suspects_with_trait = [
            has_trait[0]
            for has_trait in self.model.get("has_trait", [])
            if has_trait[1] == self.trait_name
        ]

        self.ended = False
        self.case_solved = False
        self.actions = self.default_actions
        self.n_actions = 0

    def start(self):
        print("=" * 60)
        print(f" CASE FILE {self.iteration}/{self.total_iterations} ")
        print("=" * 60)

        w_text = self.WEAPON_TEXTS[self.weapon_id]["murder_text"]
        victim_name = self.victim_profile["id"].capitalize()

        print(
            f"\n{victim_name}, one of the oldest members of the household, "
            f"was found dead in the study. Cause of death: {w_text}."
        )

        print(f"\nYou are {self.player_role.capitalize()} in this case.")
        print("Think carefully: you may interrogate any suspect, including yourself.")
        print("There are always 4 living suspects (A, B, C, D): exactly 2 boys and 2 girls.")
        print("Plus one dead victim tied to this generation.")
        print("You may freely explore rooms before making your accusation.")
        print(f"You begin in the {self.__pretty_name(self.current_room)}.")
        print("\nType 'review rules' to see the facts of the case, or '?' for commands.\n")

        self.__print_backstories()

        while not self.ended:
            self.__main_loop()

    def __print_backstories(self):
        print("\n--- HOUSEHOLD BACKSTORIES ---")
        for person in self.__ordered_people():
            person_id = person["id"]
            name = person_id.capitalize()
            gender = "Boy" if person["gender"] == "boy" else "Girl"
            age = person["age"]
            story = self.backstories[person_id]
            marker = " [YOU]" if person_id == self.player_role else ""
            print(f"- {name} ({gender}, age {age}, Alive Suspect){marker}: {story}")

        victim_name = self.victim_profile["id"].capitalize()
        victim_gender = "Boy" if self.victim_profile["gender"] == "boy" else "Girl"
        victim_age = self.victim_profile["age"]
        victim_story = self.victim_profile["story"]
        print(f"- {victim_name} ({victim_gender}, age {victim_age}, Dead Victim): {victim_story}")

    def __ordered_people(self):
        return sorted(self.people_info.values(), key=lambda person: person["letter"])

    def __main_loop(self):
        user_input = input("\nWhat is your order? > ").strip().lower()

        matching_actions = list(filter(lambda action: action.matches(user_input), self.actions))
        if len(matching_actions) == 0:
            print("Invalid command! Please type '?' for help.")
        elif len(matching_actions) > 1:
            print("Multiple actions possible! Please be more specific.")
        else:
            self.__perform_action(matching_actions[0], user_input)

    def __perform_action(self, action, user_input):
        args = action.extract_args(user_input)
        if isinstance(args, str):
            print(args)
            return

        if action.automatic_validation:
            for i, arg in enumerate(args):
                arg_name = action.argument_names[min(i, len(action.argument_names) - 1)]
                valid_values = self.model.get(arg_name, [])
                if arg not in valid_values:
                    print(f"'{arg}' is not a valid {arg_name}.")
                    return

        if action.command not in ["?", "quit", "end case"]:
            self.n_actions += 1

        method_name = action.method_name
        if method_name[:2] == "__":
            method_name = "_MysteryGame{}".format(method_name)
        getattr(self, method_name)(*args)

    def __help(self):
        print("Possible commands:")
        print("\n".join(["  {} = {}".format(action.command, action.help_text) for action in self.actions]))

    def __end_case(self):
        if not getattr(self, "post_accusation_phase", False):
            print("You cannot end the case until you make a correct accusation.")
            return
        if self.iteration == self.total_iterations:
            print("You must complete the final ritual (burn an item) to end this generation.")
            return
        print("You conclude the investigation and prepare for the years ahead.")
        self.ended = True

    def __quit(self):
        print("You leave the manor, leaving the mystery unsolved. The murderers walk free...")
        self.ended = True

    def __review_rules(self):
        w_text = self.WEAPON_TEXTS[self.weapon_id]
        print("\n--- FACTS OF THE CASE ---")
        print("1. There are either exactly 1 or exactly 2 murderers among living suspects.")
        print(
            f"2. The victim was {w_text['murder_text']}. "
            f"Therefore, AT LEAST ONE killer must {w_text['trait_desc']}."
        )
        print("3. ABSOLUTE RULE: Innocent suspects always tell the truth. Murderers ALWAYS lie.")
        print("4. Your accusation must include the exact full set of killers in one command.")
        print("5. Special exception: during interrogation of personal traits everyone answers truthfully.")
        print("6. After a correct accusation, a killer confesses only rooms they visited, never item names.")
        if self.iteration == self.total_iterations:
            print("7. In generation 3, solve the murder first, then burn exactly one held item in the living room fireplace.")

    def __list_people(self):
        print("\n--- LIVING SUSPECTS ---")
        for person in self.__ordered_people():
            person_id = person["id"]
            name = person_id.capitalize()
            gender = "Boy" if person["gender"] == "boy" else "Girl"
            age = person["age"]
            marker = ", YOU" if person_id == self.player_role else ""
            print(f"- {name} ({gender}, age {age}, Alive Suspect{marker})")

        print(f"Dead victim: {self.victim_profile['id'].capitalize()}.")

    def __list_rooms(self):
        print("\n--- MANOR ROOMS ---")
        for room in self.rooms:
            tags = []
            if room == self.current_room:
                tags.append("current")
            if room == self.fireplace_room:
                tags.append("fireplace")

            tag_text = f" [{', '.join(tags)}]" if tags else ""
            print(f"- {self.__pretty_name(room)}{tag_text}")

    def __go_room(self, room):
        self.current_room = room
        print(f"You move to the {self.__pretty_name(room)}.")

    def __examine_room(self, room):
        if room != self.current_room:
            print(f"You are currently in the {self.__pretty_name(self.current_room)}.")
            print("Move there first with 'go <room>' before examining it.")
            return

        print(f"\n--- {self.__pretty_name(room).upper()} ---")
        items = self.room_items.get(room, [])
        if items:
            for item in items:
                print(f"- {self.__pretty_name(item)}")
        else:
            print("No loose objects remain here.")

        if room == self.fireplace_room:
            print("A fireplace crackles here. In the final case, this is where the ritual ends.")

    def __inventory(self):
        if not self.inventory_items:
            print("You are not carrying any items.")
            return

        print("\n--- INVENTORY ---")
        for item in self.inventory_items:
            print(f"- {self.__pretty_name(item)}")

    def __take_item(self, item):
        if not self.finale_unlocked:
            print("You may only collect items after solving generation 3's murder.")
            return

        if item in self.inventory_items:
            print(f"You already carry the {self.__pretty_name(item)}.")
            return

        item_room = self.item_locations.get(item)
        if item_room is None:
            print(f"The {self.__pretty_name(item)} is no longer in the manor.")
            return
        if item_room != self.current_room:
            print(f"The {self.__pretty_name(item)} is not in this room.")
            return

        self.inventory_items.append(item)
        self.room_items[item_room] = [room_item for room_item in self.room_items[item_room] if room_item != item]
        self.item_locations[item] = None
        print(f"You take the {self.__pretty_name(item)}.")

    def __burn_item(self, item):
        if not self.finale_unlocked:
            print("The burn ritual is only available after solving generation 3's murder.")
            return

        if self.current_room != self.fireplace_room:
            print("You must be in the living room at the fireplace to burn an item.")
            return

        if item not in self.inventory_items:
            print(f"You are not holding the {self.__pretty_name(item)}.")
            return

        print(f"You cast the {self.__pretty_name(item)} into the flames...")
        time.sleep(1)

        if item == self.cursed_heirloom:
            print("\nThe manor groans, then falls silent. The curse is broken.")
            print("META-MYSTERY SOLVED: You destroyed the true cursed heirloom.")
            self.meta_outcome = "win"
        else:
            print("\nThe fire spits black smoke. The curse remains unbroken.")
            print("META-MYSTERY FAILED: You burned the wrong item.")
            self.meta_outcome = "loss"

        self.ended = True

    def __print_confession(self):
        print("\n--- CONFESSION / RECOLLECTION ---")
        if self.confessor == self.player_role:
            print("Since you are the confessor, you silently recall the rooms you visited before the murder:")
            for room in self.confession_rooms:
                print(f"- {self.__pretty_name(room)}")
            print("(You naturally know not to leave the item names out in the open.)")
        else:
            print(f"{self.confessor.capitalize()} breaks down and admits involvement.")
            print("\"The whispers came from these rooms... over and over, until I could no longer resist them...\"")
            for room in self.confession_rooms:
                print(f"- {self.__pretty_name(room)}")
            print("(No item names are revealed.)")

    @staticmethod
    def __pretty_name(raw_name):
        return raw_name.replace("_", " ").title()

    def __interrogate_person(self, person):
        if getattr(self, "post_accusation_phase", False):
            print("The accusation has already been made. Further interrogation is pointless.")
            return

        if person == self.victim:
            print(f"{person.capitalize()} is the victim and can no longer be questioned.")
            return

        print(f"\nYou begin questioning {person.capitalize()}.")
        #print("1. Ask who they think is or is not a murderer.")
        #print("2. Ask them to reveal something about themselves (guaranteed truthful answer).")
        choice = input("Choose 1 or 2 > ").strip()

        if choice == "1":
            self.__ask_belief_statement(person)
        elif choice == "2":
            self.__ask_personal_trait(person)
        else:
            print("Invalid choice. Interrogation ended.")
            return

    def __ask_belief_statement(self, person):
        statements = self.model.get("statement", [])
        person_statement = None
        for statement in statements:
            if statement[0] == person:
                person_statement = statement[1]
                break

        if not person_statement:
            print(f"{person.capitalize()} refuses to speak.")
            return

        stmt_type, args = self.__parse_statement(str(person_statement))
        if not stmt_type:
            print(f"{person.capitalize()} mutters something incomprehensible.")
            return

        stmt_text = ""
        if stmt_type == "claims_innocent":
            q = args[1].capitalize()
            stmt_text = f"\"I swear on my honor, neither I nor {q} committed this heinous act!\""
        elif stmt_type == "claims_implication":
            q = args[0].capitalize()
            r = args[1].capitalize()
            stmt_text = f"\"I have a theory. If {q} is involved, then {r} must certainly be involved too.\""
        elif stmt_type == "claims_sole_killer":
            q = args[1].capitalize()
            stmt_text = f"\"I am completely innocent! The only killer here is {q}.\""
        elif stmt_type == "claims_two_killers":
            stmt_text = "\"I know for a fact that there were exactly two perpetrators working together.\""
        elif stmt_type == "claims_one_killer":
            stmt_text = "\"I am certain that the killer acted entirely alone.\""
        elif stmt_type == "claims_is_guilty":
            q = args[0].capitalize()
            stmt_text = f"\"I saw something suspicious... {q} is definitely one of the killers!\""
        elif stmt_type == "claims_is_innocent":
            q = args[0].capitalize()
            stmt_text = f"\"I can personally vouch for {q}. They are completely innocent!\""
        elif stmt_type == "claims_both_guilty":
            q = args[0].capitalize()
            r = args[1].capitalize()
            stmt_text = f"\"It was a conspiracy! {q} and {r} committed this crime together!\""
        elif stmt_type == "claims_xor":
            q = args[0].capitalize()
            r = args[1].capitalize()
            stmt_text = f"\"Exactly one of {q} or {r} is guilty, but not both!\""
        elif stmt_type == "claims_same_status":
            q = args[0].capitalize()
            r = args[1].capitalize()
            stmt_text = f"\"{q} and {r} share the same secret: both guilty or both innocent.\""

        if person == self.player_role:
            print("\nYou state your beliefs out loud:")
            print(stmt_text)
        else:
            print(f"\n[{person.capitalize()}] looks at you and says:")
            print(stmt_text)

    def __ask_personal_trait(self, person):
        trait_text = self.WEAPON_TEXTS[self.weapon_id]
        has_trait = person in self.suspects_with_trait
        trait_label = trait_text["has_trait"] if has_trait else trait_text["no_trait"]
        reveal_line = self.TRAIT_REVEAL_LINES.get(
            trait_label,
            f"\"For this line of inquiry, I am {trait_label.lower()}.\"",
        )

        if person == self.player_role:
            print("\nYou think to yourself:")
            clean_line = reveal_line.strip('"')
            print(f"It is true. {clean_line}")
        else:
            print(f"\n[{person.capitalize()}] responds about themselves:")
            print("(This is a known fact, this personal trait answer is truthful.)")
            print(reveal_line)

    @staticmethod
    def __parse_statement(statement):
        match = re.fullmatch(r"([a-zA-Z_][a-zA-Z0-9_]*)(?:\((.*)\))?", statement)
        if not match:
            return None, []

        stmt_type = match.group(1)
        arg_string = match.group(2)
        if not arg_string:
            return stmt_type, []

        return stmt_type, [arg.strip() for arg in arg_string.split(",") if arg.strip()]

    def __accuse_people(self, *people):
        if getattr(self, "post_accusation_phase", False):
            print("You have already correctly accused the murderer(s).")
            return

        if len(people) == 2 and people[0] == people[1]:
            print("If you accuse two suspects, they must be different people.")
            return

        accused = sorted(list(people))
        murderers = sorted(self.model["murderer"])

        accused_text = " and ".join([person.capitalize() for person in accused])
        if self.player_role in murderers:
            print(f"You thought it was just a nightmare... but it's true. You are the murderer!")
        else:
            print(f"You point your finger at {accused_text}!")

        time.sleep(1)
        print("...")
        time.sleep(1)

        if accused == murderers:
            print(f"\nBRILLIANT DEDUCTION! You solved this case in {self.n_actions} steps.")
            m_list = " and ".join([murderer.capitalize() for murderer in murderers])
            
            if self.player_role in murderers:
                print(f"You keep your own involvement quiet, but successfully identify the full conspiracy.")
                print(f"The guilty party was indeed: {m_list}.")
            else:
                print(f"The guilty party was: {m_list}.")

            self.case_solved = True
            self.post_accusation_phase = True

            self.__print_confession()

            if self.iteration == self.total_iterations:
                self.finale_unlocked = True
                print("\nFinal ritual unlocked.")
                print("Explore rooms, identify the single consistent heirloom across all confessions,")
                print("take exactly one item, then burn it in the living room fireplace.")
            else:
                print("\nYou may continue to explore the manor.")
                print("Click 'End Case' or type 'end case' when you are ready to move to the next generation.")
        else:
            print("\nWRONG! Your accusation does not match the exact set of murderers.")
            m_list = " and ".join([murderer.capitalize() for murderer in murderers])
            print(f"The actual guilty party was: {m_list}.")
            self.ended = True


