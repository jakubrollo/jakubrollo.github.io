import gradio as gr
import io
import random
import builtins
from contextlib import redirect_stdout

# Import from the murder_mystery module
from murder_mystery.campaign import MysteryCampaign
from murder_mystery.game import MysteryGame

class PersonInfo:
    def __init__(self, person_id: str, label: str):
        self.person_id = person_id
        self.label = label
        
    def __repr__(self):
        return self.label

# Global sessions dictionary so each player on HuggingFace Spaces gets their own instance.
sessions = {}

def get_session(request: gr.Request):
    session_id = request.session_hash if request else "local"
    if session_id not in sessions:
        sessions[session_id] = GradioGameSession(session_id)
        sessions[session_id].start_next_case()
    return sessions[session_id]

class GradioGameSession:
    def __init__(self, session_hash: str):
        self.session_hash = session_hash
        self.campaign = MysteryCampaign(total_iterations=3)
        self.current_iteration = 0
        self.current_scenario = None
        self.current_game = None
        
        self.current_mode = "investigation"
        self.question_target = None
        
        self.case_log_text = ""
        self.notes_text = ""
        self.user_notes = ""
        
        self.room_ids = []
        self.people = []
        self.items_in_current_room = []
        
        self.campaign_finished = False
        self.current_case_scored = False
        
        self.combo_states = {c: 0 for c in ["A", "B", "C", "D", "AB", "AC", "AD", "BC", "BD", "CD"]}

    def append_log(self, text: str):
        self.case_log_text += str(text).rstrip() + "\n"

    def _capture_backend_output(self, fn) -> list:
        output_capture = io.StringIO()
        with redirect_stdout(output_capture):
            fn()
        rendered = output_capture.getvalue().strip("\n")
        if not rendered:
            return []
        return rendered.splitlines()

    def _append_lines(self, lines: list):
        for line in lines:
            self.append_log(line)

    def pretty_name(self, atom: str) -> str:
        return atom.replace("_", " ").title()

    def start_next_case(self):
        if self.campaign_finished:
            return

        next_iteration = self.current_iteration + 1
        if next_iteration > self.campaign.total_iterations:
            self.campaign_finished = True
            self.append_log("=" * 60)
            self.append_log("   THE BLACKWOOD CHRONICLES - FINISHED   ")
            self.append_log("=" * 60)
            self.append_log(f"All {self.campaign.total_iterations} cases completed!")
            self.current_game = None
            return

        scenario = None
        game = None

        def _build():
            nonlocal scenario, game
            # use public methods or mangle the name to call __build_scenario
            scenario = self.campaign._MysteryCampaign__build_scenario(next_iteration)
            player_role = random.choice([person["id"] for person in scenario["people"]])
            game = MysteryGame(scenario, player_role, self.campaign.total_iterations)

        build_lines = self._capture_backend_output(_build)
        self._append_lines(build_lines)

        self.current_iteration = next_iteration
        self.current_scenario = scenario
        self.current_game = game
        self.current_case_scored = False

        self.append_log("=" * 60)
        self.append_log(f" CASE FILE {game.iteration}/{game.total_iterations} ")
        self.append_log("=" * 60)

        weapon_text = game.WEAPON_TEXTS[game.weapon_id]["murder_text"]
        victim_name = game.victim_profile["id"].capitalize()

        self.append_log(
            f"\n{victim_name}, one of the oldest members of the household, "
            f"was found dead in the study. Cause of death: {weapon_text}."
        )

        self.append_log("")
        self.append_log(f"You are {game.player_role.capitalize()} in this case.")
        self.append_log("Think carefully: you may interrogate any suspect, including yourself.")
        self.append_log("There are 4 living suspects.")
        self.append_log("One or two of them are the murderers.")
        self.append_log("Innocents always tell the truth; murderers always lie (unless talking about their traits).")
        self.append_log("You may freely explore rooms and search for items (they seem to have some significance).")
        self.append_log(f"You begin in the {self.pretty_name(game.current_room)}.")
        self.append_log("Type 'review rules' to see the facts of the case, or '?' for commands.")

        self.current_mode = "investigation"
        self.combo_states = {c: 0 for c in ["A", "B", "C", "D", "AB", "AC", "AD", "BC", "BD", "CD"]}
        self.refresh_data()

    def refresh_data(self):
        if not self.current_game:
            return
            
        self.room_ids = list(self.current_game.rooms)
        ordered_people = sorted(
            self.current_game.people_info.values(),
            key=lambda person: person["letter"],
        )
        self.people = []
        for person in ordered_people:
            person_id = person["id"]
            marker = " [YOU]" if person_id == self.current_game.player_role else ""
            label = f"{person_id.capitalize()} ({person['gender']}, age {person['age']}){marker}"
            self.people.append(PersonInfo(person_id=person_id, label=label))
            
        # Extract selected rooms dynamically below
        self.items_in_current_room = list(self.current_game.room_items.get(self.current_game.current_room, []))

    def dispatch_command(self, command: str, interrogation_choice: str = None):
        if not self.current_game:
            return

        self.append_log(f"\n> {command}")

        def _run_action():
            matching_actions = [
                action for action in self.current_game.actions if action.matches(command)
            ]
            if len(matching_actions) == 0:
                print("Invalid command! Please type '?' for help.")
            elif len(matching_actions) > 1:
                print("Multiple actions possible! Please be more specific.")
            else:
                if interrogation_choice is None:
                    self.current_game._MysteryGame__perform_action(matching_actions[0], command)
                else:
                    original_input = builtins.input
                    try:
                        builtins.input = lambda _prompt="": interrogation_choice
                        self.current_game._MysteryGame__perform_action(matching_actions[0], command)
                    finally:
                        builtins.input = original_input

        lines = self._capture_backend_output(_run_action)
        self._append_lines(lines)

        self.refresh_data()
        
        # Check transition
        if getattr(self.current_game, "case_ended", False) and not getattr(self.current_game, "game_quit", False):
            if not getattr(self.current_game, "_score_calculated", False):
                def _score():
                    self.current_game._MysteryGame__calculate_final_score()
                score_lines = self._capture_backend_output(_score)
                self._append_lines(score_lines)
                self.current_game._score_calculated = True
                
                # Save survivors for the next generation
                if self.current_scenario and "people" in self.current_scenario:
                    self.campaign.previous_youngest = self.campaign._MysteryCampaign__select_next_youngest(
                        self.current_scenario["people"]
                    )
                
        if getattr(self.current_game, "game_quit", False):
            self.campaign_finished = True

def toggle_combo(state: int):
    if state is None:
        state = 0
    # 0 -> 1 -> 2 -> 0. 0=Secondary(Gray), 1=Primary(Gold), 2=Stop(Red)
    new_s = (state + 1) % 3
    if new_s == 0:
        return new_s, gr.update(elem_classes=["combo-btn", "combo-unsure"])
    elif new_s == 1:
        return new_s, gr.update(elem_classes=["combo-btn", "combo-possible"])
    else:
        return new_s, gr.update(elem_classes=["combo-btn", "combo-ruledout"])


def update_all_ui(request: gr.Request):
    sess = get_session(request)
    
    # 1. Handle Campaign Over state 
    # (Returning empty/disabled states since the game is finished)
    if not sess.current_game:
        return (
            sess.case_log_text,            # log_box
            "Campaign Finished",           # status_lbl
            gr.update(choices=[]),         # cb_rooms
            gr.update(choices=[]),         # cb_people
            gr.update(choices=[]),         # cb_items
            gr.update(choices=[]),         # cb_accuse_prim
            gr.update(choices=[]),         # cb_accuse_sec
            gr.update(choices=[]),         # cb_inventory
            gr.update(visible=False),      # finale_actions_group
            gr.update(interactive=False),  # btn_accuse
            gr.update(interactive=False)   # btn_end_case (Disabled because campaign is totally over)
        )
            
    # 2. Format labels for components
    room_choices = []
    for r in sess.room_ids:
        lbl = sess.pretty_name(r)
        if r == sess.current_game.current_room:
            lbl += " [current]"
        if r == sess.current_game.fireplace_room:  
            lbl += " [fireplace]"
        room_choices.append(lbl)
            
    people_choices = [p.label for p in sess.people]
    item_choices = [sess.pretty_name(i) for i in sess.items_in_current_room] if sess.items_in_current_room else []
    
    status_text = (
        f"**Case {sess.current_game.iteration}/{sess.current_game.total_iterations}** | "
        f"**You:** {sess.current_game.player_role.capitalize()} | "
        f"**Room:** {sess.pretty_name(sess.current_game.current_room).capitalize()}"
    )
    
    accuse_prim_choices = [p.person_id for p in sess.people]
    accuse_sec_choices = ["(none)"] + [p.person_id for p in sess.people]
    
    inventory_choices = list(sess.current_game.inventory_items) if sess.current_game.inventory_items else ["(inventory empty)"]
    
    # 3. Show finale area ONLY if generation 3 and finale unlocked
    show_finale = False
    if sess.current_game.iteration == sess.current_game.total_iterations:
        if getattr(sess.current_game, "finale_unlocked", False) and not getattr(sess.current_game, "ended", False) and not sess.campaign_finished:
            show_finale = True
            
    # 4. Check if a case was already solved/accused
    post_acc_phase = getattr(sess.current_game, "post_accusation_phase", False)
    case_ended = getattr(sess.current_game, "case_ended", False)

    # 5. Return UI updates mapping for standard components
    return (
        sess.case_log_text,
        status_text,
        gr.update(choices=room_choices),
        gr.update(choices=people_choices),
        gr.update(choices=item_choices),
        gr.update(choices=accuse_prim_choices, interactive=not post_acc_phase),
        gr.update(choices=accuse_sec_choices, interactive=not post_acc_phase),
        gr.update(choices=inventory_choices),
        gr.update(visible=show_finale),
        gr.update(interactive=not post_acc_phase), # btn_accuse (Disabled after accusation)
        gr.update(interactive=post_acc_phase)      # btn_end_case (ENABLED only after accusation)
    )

def reset_combo_buttons():
    # Return 10 states (0) and 10 secondary button updates
    res = []
    for _ in range(10):
        res.extend([0, gr.update(elem_classes=["combo-btn", "combo-unsure"])])
    return tuple(res)


def handle_review(request: gr.Request):
    sess = get_session(request)
    sess.dispatch_command("review rules")
    return update_all_ui(request)

def handle_go_room(room_label: str, request: gr.Request):
    sess = get_session(request)
    if not room_label:
        sess.append_log("No room selected.")
        return update_all_ui(request)
        
    idx = 0  # To find original room ID from selection
    for r in sess.room_ids:
        lbl = sess.pretty_name(r)
        if r == sess.current_game.current_room: lbl += " [current]"
        if r == sess.current_game.fireplace_room: lbl += " [fireplace]"
        if lbl == room_label:
            sess.dispatch_command(f"go {r}")
            return update_all_ui(request)
    sess.append_log("Invalid room selection.")
    return update_all_ui(request)

def handle_examine_room(request: gr.Request):
    sess = get_session(request)
    sess.dispatch_command(f"examine {sess.current_game.current_room}")
    return update_all_ui(request)

def handle_interrogate(person_label: str, request: gr.Request):
    sess = get_session(request)
    if not person_label:
        sess.append_log("No person selected.")
        return update_all_ui(request) + (gr.Row(visible=False), gr.Row(visible=True))
        
    for p in sess.people:
        if p.label == person_label:
            sess.current_mode = "questioning"
            sess.question_target = p.person_id
            return update_all_ui(request) + (gr.Row(visible=True), gr.Row(visible=False))
            
    return update_all_ui(request) + (gr.Row(visible=False), gr.Row(visible=True))

def handle_ask(choice: str, request: gr.Request):
    sess = get_session(request)
    sess.dispatch_command(f"interrogate {sess.question_target}", interrogation_choice=choice)
    # Automatically drop out of questioning if desired, but here the GUI explicitly stopped it or could do 1 question.
    sess.current_mode = "investigation"
    sess.question_target = None
    return update_all_ui(request) + (gr.Row(visible=False), gr.Row(visible=True))

def handle_stop_interrogation(request: gr.Request):
    sess = get_session(request)
    sess.current_mode = "investigation"
    sess.question_target = None
    return update_all_ui(request) + (gr.Row(visible=False), gr.Row(visible=True))

def handle_accuse(primary: str, secondary: str, request: gr.Request):
    sess = get_session(request)
    cmd = f"accuse {primary}"
    if secondary and secondary != "(none)":
        cmd += f" {secondary}"
    sess.dispatch_command(cmd)
    
    # Check if case ended, to toggle next case button
    is_ended = getattr(sess.current_game, "case_ended", False)
    
    updates = list(update_all_ui(request))
    # inject button state toggle to updates list manually or handle separately
    return tuple(updates)

def handle_end_case(request: gr.Request):
    sess = get_session(request)
    sess.dispatch_command("end case")
    sess.start_next_case()
    return update_all_ui(request)

def handle_take_item(item_label: str, request: gr.Request):
    sess = get_session(request)
    if not item_label:
        return update_all_ui(request)
    raw_id = None
    for i in sess.items_in_current_room:
        if sess.pretty_name(i) == item_label:
            raw_id = i
            break
    if raw_id:
        sess.dispatch_command(f"take {raw_id}")
    return update_all_ui(request)

def handle_burn_item(item_label: str, request: gr.Request):
    sess = get_session(request)
    if not item_label or item_label == "(inventory empty)":
        return update_all_ui(request)
    sess.dispatch_command(f"burn {item_label}")
    return update_all_ui(request)

def on_load(request: gr.Request):
    # This runs when a new user visits the page
    return update_all_ui(request)

def handle_ask_1(request: gr.Request):
    return handle_ask("1", request)

def handle_ask_2(request: gr.Request):
    return handle_ask("2", request)

# Build the Gradio Theme
with gr.Blocks() as demo:
    
    gr.Markdown("# Blackwood Chronicles")
    gr.Markdown("A generative Noir Murder Mystery powered by Gradio & Answer Set Programming (Clingo)")
    
    with gr.Row():
        with gr.Column(scale=5):
            status_lbl = gr.Markdown("**Case Loading...**")
            log_box = gr.Textbox(
                label="Case Log", 
                lines=20, 
                max_lines=30, 
                interactive=False, 
                elem_classes=["case-log"]
            )
            
            with gr.Row() as investigation_group:
                with gr.Column():
                    btn_review = gr.Button("Review Rules", variant="secondary")
                    btn_examine_room = gr.Button("Examine Current Room", variant="primary")
                    btn_go_room = gr.Button("Go To Selected Room")
                    btn_interrogate = gr.Button("Interrogate Person")
                    
            with gr.Row(visible=False) as interrogation_group:
                with gr.Column():
                    gr.Markdown("### Interrogation Mode")
                    btn_ask_1 = gr.Button("Ask Option 1: Motives & Beliefs")
                    btn_ask_2 = gr.Button("Ask Option 2: Personal Traits")
                    btn_stop_int = gr.Button("Stop Interrogation", variant="stop")
            
            with gr.Group():
                gr.Markdown("### Accusation & Case Resolution")
                with gr.Row():
                    cb_accuse_prim = gr.Dropdown(label="Primary Suspect")
                    cb_accuse_sec = gr.Dropdown(label="Secondary Suspect")
                with gr.Row():
                    btn_accuse = gr.Button("Accuse", variant="stop")
                    btn_end_case = gr.Button("Next Case (End Current Phase)")

        with gr.Column(scale=3):
            with gr.Group(elem_classes=["dossier-panel"]):
                gr.Markdown("### Dossier")
                cb_rooms = gr.Dropdown(label="Rooms")
                cb_people = gr.Dropdown(label="People")
                cb_items = gr.Dropdown(label="Items Visible In Room")
                
            with gr.Group(visible=False) as finale_actions_group:
                gr.Markdown("### Finale Actions")
                cb_inventory = gr.Dropdown(label="Held Items")
                with gr.Row():
                    btn_take = gr.Button("Take Item in Room")
                    btn_burn = gr.Button("Burn Item", variant="stop")

            # Notes area
            with gr.Group():
                gr.Markdown("### Notepad")
                gr.Textbox(label="Player Notes", lines=7, interactive=True, placeholder="Jot down suspect motives and room findings here...")
                
                gr.Markdown("**Suspect Combinations Tracker**")
                gr.Markdown("_Grey: Unsure | Gold: Possible | Red: Ruled Out_")
                
                # We'll use Button groups and pass state back and forth
                combo_names = [
                    "A", "B", "C", "D",
                    "AB", "AC", "AD",
                    "BC", "BD", "CD"
                ]
                combo_btn_refs = {}
                combo_states_refs = {}
                with gr.Row():
                    for name in combo_names[:4]:
                        combo_states_refs[name] = gr.State(0)
                        combo_btn_refs[name] = gr.Button(name, elem_classes=["combo-btn", "combo-unsure"])
                with gr.Row():
                    for name in combo_names[4:7]:
                        combo_states_refs[name] = gr.State(0)
                        combo_btn_refs[name] = gr.Button(name, elem_classes=["combo-btn", "combo-unsure"])
                with gr.Row():
                    for name in combo_names[7:]:
                        combo_states_refs[name] = gr.State(0)
                        combo_btn_refs[name] = gr.Button(name, elem_classes=["combo-btn", "combo-unsure"])

    # Wire up events
    base_outputs = [log_box, status_lbl, cb_rooms, cb_people, cb_items, cb_accuse_prim, cb_accuse_sec, cb_inventory, finale_actions_group, btn_accuse, btn_end_case]
    interrogation_outputs = base_outputs + [interrogation_group, investigation_group]

    demo.load(on_load, inputs=[], outputs=base_outputs)

    btn_review.click(handle_review, inputs=[], outputs=base_outputs)
    btn_go_room.click(handle_go_room, inputs=[cb_rooms], outputs=base_outputs)
    btn_examine_room.click(handle_examine_room, inputs=[], outputs=base_outputs)
    
    btn_interrogate.click(handle_interrogate, inputs=[cb_people], outputs=interrogation_outputs)
    btn_ask_1.click(handle_ask_1, inputs=[], outputs=interrogation_outputs)
    btn_ask_2.click(handle_ask_2, inputs=[], outputs=interrogation_outputs)
    btn_stop_int.click(handle_stop_interrogation, inputs=[], outputs=interrogation_outputs)
    
    btn_accuse.click(handle_accuse, inputs=[cb_accuse_prim, cb_accuse_sec], outputs=base_outputs)
    
    btn_take.click(handle_take_item, inputs=[cb_items], outputs=base_outputs)
    btn_burn.click(handle_burn_item, inputs=[cb_inventory], outputs=base_outputs)

    # Wire up combos
    for name in combo_names:
        combo_btn_refs[name].click(
            toggle_combo,
            inputs=[combo_states_refs[name]],
            outputs=[combo_states_refs[name], combo_btn_refs[name]]
        )

    btn_end_case.click(
        reset_combo_buttons,
        inputs=[],
        outputs=[st_or_btn for n in combo_names for st_or_btn in (combo_states_refs[n], combo_btn_refs[n])]
    ).then(
        handle_end_case,
        inputs=[],
        outputs=base_outputs
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Monochrome(
        neutral_hue="slate",
        text_size=gr.themes.sizes.text_md
    ), css="""
    .case-log textarea { background-color: #0F1113 !important; color: #ECE7DD !important; font-family: monospace; font-size: 14px;}
    .dossier-panel { background-color: #171A1E; padding: 15px; border-radius: 8px;}
    .combo-btn { min-width: 0 !important; width: 45px !important; height: 35px !important; padding: 4px !important; margin: 2px !important; font-weight: bold; border: 1px solid #2A2F36 !important; }
    .combo-unsure { background: #1E2227 !important; color: #ECE7DD !important; }
    .combo-possible { background: #B7905A !important; color: #0F1113 !important; }
    .combo-ruledout { background: #8C3A3A !important; color: #ECE7DD !important; }
    """)