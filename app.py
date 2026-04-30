# The GUI was fully generated using Gemini 3.1 Pro

from __future__ import annotations

from contextlib import redirect_stdout
from dataclasses import dataclass
import builtins
import io
import random
import tkinter as tk
from tkinter import messagebox

from murder_mystery.campaign import MysteryCampaign
from murder_mystery.game import MysteryGame

try:
    import customtkinter as ctk  # type: ignore[import-not-found]
except ImportError as exc:
    raise SystemExit(
        "CustomTkinter is required for this UI. Install it with: pip install customtkinter"
    ) from exc


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


@dataclass(frozen=True)
class PersonInfo:
    person_id: str
    label: str


from murder_mystery.gui.panels import GUIPanelsMixin

class MysteryGameGUI(ctk.CTk, GUIPanelsMixin):
    """Noir-style GUI for the multi-generation Blackwood campaign."""

    COLOR_BG = "#0F1113"
    COLOR_PANEL = "#171A1E"
    COLOR_CARD = "#1E2227"
    COLOR_BORDER = "#2A2F36"
    COLOR_TEXT = "#ECE7DD"
    COLOR_MUTED = "#A79F92"
    COLOR_ACCENT = "#B7905A"
    COLOR_ACCENT_HOVER = "#9F7845"
    COLOR_DANGER = "#8C3A3A"
    COLOR_DANGER_HOVER = "#712F2F"

    def __init__(self) -> None:
        super().__init__()

        self.title("Murder case - Blackwood Chronicles")
        self.geometry("1440x840")
        self.minsize(1080, 700)
        self.configure(fg_color=self.COLOR_BG)

        self.campaign = MysteryCampaign(total_iterations=3)
        self.current_iteration = 0
        self.current_scenario: dict | None = None
        self.current_game: MysteryGame | None = None

        self.current_mode = "investigation"
        self.question_target: str | None = None

        self._current_case_scored = False
        self._campaign_finished = False

        self.room_ids: list[str] = []
        self.people: list[PersonInfo] = []
        self.items_in_current_room: list[str] = []
        self.confession_history: list[tuple[int, str, list[str]]] = []

        self._configure_window_grid()
        self._build_case_log()
        self._build_dossier_panel()
        self._build_action_bar()
        self._build_notepad_panel()

        self._start_next_case()

    def _configure_window_grid(self) -> None:
        self.grid_columnconfigure(0, weight=3) # Case Log
        self.grid_columnconfigure(1, weight=1) # Dossier
        self.grid_columnconfigure(2, weight=0) # Notepad (hidden initially)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

    def _toggle_combo_state(self, combo_text: str) -> None:
        """Cycles combination button through Neutral (0) -> Circled/Gold (1) -> Crossed/Red (2)"""
        current_state = self.combo_states[combo_text]
        next_state = (current_state + 1) % 3
        self.combo_states[combo_text] = next_state
        
        btn = self.combo_buttons[combo_text]
        if next_state == 0:
            btn.configure(fg_color=self.COLOR_CARD)
        elif next_state == 1:
            btn.configure(fg_color=self.COLOR_ACCENT)
        elif next_state == 2:
            btn.configure(fg_color=self.COLOR_DANGER)

    def _reset_notepad_combinations(self) -> None:
        """Resets the combination tracker colors back to Neutral."""
        for text in self.combo_states:
            self.combo_states[text] = 0
            self.combo_buttons[text].configure(fg_color=self.COLOR_CARD)

    def append_log(self, text: str) -> None:
        self.case_log_box.configure(state="normal")
        self.case_log_box.insert(tk.END, text.rstrip() + "\n")
        self.case_log_box.see(tk.END)
        self.case_log_box.configure(state="disabled")

    def _set_notes_text(self, lines: list[str]) -> None:
        self.notes_box.configure(state="normal")
        self.notes_box.delete("1.0", tk.END)
        self.notes_box.insert(tk.END, "\n".join(lines))
        self.notes_box.see("1.0")
        self.notes_box.configure(state="disabled")

    @staticmethod
    def _pretty_name(atom: str) -> str:
        return atom.replace("_", " ").title()

    def _selected_room(self) -> str | None:
        selected = self.rooms_listbox.curselection()
        if not selected:
            return None
        return self.room_ids[selected[0]]

    def _selected_person(self) -> PersonInfo | None:
        selected = self.people_listbox.curselection()
        if not selected:
            return None
        return self.people[selected[0]]

    def _selected_room_item(self) -> str | None:
        if not self.items_in_current_room:
            return None
        selected = self.items_listbox.curselection()
        if not selected:
            return None
        return self.items_in_current_room[selected[0]]

    def _refresh_dossier_data(self) -> None:
        if self.current_game is None:
            return

        self.room_ids = list(self.current_game.rooms)
        self.rooms_listbox.delete(0, tk.END)
        for room_id in self.room_ids:
            label = self._pretty_name(room_id)
            if room_id == self.current_game.current_room:
                label += " [current]"
            if room_id == self.current_game.fireplace_room:
                label += " [fireplace]"
            self.rooms_listbox.insert(tk.END, label)

        ordered_people = sorted(
            self.current_game.people_info.values(),
            key=lambda person: person["letter"],
        )
        self.people = []
        self.people_listbox.delete(0, tk.END)
        for person in ordered_people:
            person_id = person["id"]
            marker = " [YOU]" if person_id == self.current_game.player_role else ""
            label = f"{person_id.capitalize()} ({person['gender']}, age {person['age']}){marker}"
            self.people.append(PersonInfo(person_id=person_id, label=label))
            self.people_listbox.insert(tk.END, label)

        self.items_in_current_room = list(self.current_game.room_items.get(self.current_game.current_room, []))
        self.items_listbox.delete(0, tk.END)
        if self.items_in_current_room:
            for item in self.items_in_current_room:
                self.items_listbox.insert(tk.END, self._pretty_name(item))
        else:
            self.items_listbox.insert(tk.END, "(no loose items)")

        people_values = [person.person_id for person in self.people]

        primary_values = people_values if people_values else ["(no suspects)"]
        previous_primary = self.accuse_primary_combo.get().strip().lower()
        self.accuse_primary_combo.configure(values=primary_values)
        if previous_primary in primary_values:
            self.accuse_primary_combo.set(previous_primary)
        else:
            self.accuse_primary_combo.set(primary_values[0])

        secondary_values = ["(none)"] + people_values if people_values else ["(none)"]
        previous_secondary = self.accuse_secondary_combo.get().strip().lower()
        self.accuse_secondary_combo.configure(values=secondary_values)
        if previous_secondary in secondary_values:
            self.accuse_secondary_combo.set(previous_secondary)
        else:
            self.accuse_secondary_combo.set("(none)")

        inventory_values = list(self.current_game.inventory_items)
        previous_inventory = self.inventory_combo.get().strip().lower()
        if not inventory_values:
            inventory_values = ["(inventory empty)"]
        self.inventory_combo.configure(values=inventory_values)
        if previous_inventory in inventory_values:
            self.inventory_combo.set(previous_inventory)
        else:
            self.inventory_combo.set(inventory_values[0])

        self._update_status_labels()
        self._refresh_action_buttons_state()
        self._refresh_finale_controls_visibility()
        self._update_notes_snapshot(None)

    def _refresh_action_buttons_state(self) -> None:
        """Handles disabling interrogation and accuse buttons if in post-accusation phase."""
        if self.current_game is None:
            return
            
        if getattr(self.current_game, "post_accusation_phase", False):
            self.interrogate_button.configure(state="disabled")
            self.accuse_button.configure(state="disabled")
            self.accuse_primary_combo.configure(state="disabled")
            self.accuse_secondary_combo.configure(state="disabled")
            if self.current_game.iteration != self.current_game.total_iterations:
                self.end_case_button.configure(state="normal")
            else:
                self.end_case_button.configure(state="disabled")
        else:
            self.interrogate_button.configure(state="normal")
            self.accuse_button.configure(state="normal")
            self.accuse_primary_combo.configure(state="normal")
            self.accuse_secondary_combo.configure(state="normal")
            self.end_case_button.configure(state="disabled")

    def _update_status_labels(self) -> None:
        if self.current_game is None:
            return

        if self.current_mode == "questioning":
            self.mode_label.configure(text="Mode: Interrogation")
        else:
            self.mode_label.configure(text="Mode: Investigating")

        self.status_label.configure(
            text=(
                f"Case {self.current_game.iteration}/{self.current_game.total_iterations} | "
                f"You: {self.current_game.player_role.capitalize()} | "
                f"Room: {self._pretty_name(self.current_game.current_room)}"
            )
        )

    def _is_finale_ui_unlocked(self) -> bool:
        if self.current_game is None:
            return False

        return (
            self.current_game.iteration == self.current_game.total_iterations
            and getattr(self.current_game, "finale_unlocked", False)
            and not self.current_game.ended
            and not self._campaign_finished
        )

    def _refresh_finale_controls_visibility(self) -> None:
        if self._is_finale_ui_unlocked():
            self.finale_actions.grid()
            self.finale_hint_label.configure(
                text="Final ritual unlocked: take one item and burn it in the living room."
            )
        else:
            self.finale_hint_label.configure(
                text="Final ritual controls unlock after solving generation 3."
            )
            self.finale_actions.grid_remove()

    def _update_notes_snapshot(self, selected_person_id: str | None) -> None:
        if self.current_game is None:
            return

        lines: list[str] = []
        lines.append(f"Current room: {self._pretty_name(self.current_game.current_room)}")
        lines.append("Select a person from the list and interrogate them using option 1 or 2.")
        lines.append("Use the two accuse dropdowns to accuse one suspect or a pair.")

        if getattr(self.current_game, "post_accusation_phase", False):
            lines.append("\nAccusation successful! You may continue exploring rooms or end the case.")

        if self._is_finale_ui_unlocked():
            lines.append("Final ritual is active: inventory/take/burn controls are now available.")
        else:
            lines.append("Inventory and ritual controls stay hidden until generation 3 is solved.")

        if selected_person_id is not None:
            lines.append("")
            lines.append(f"Selected person: {selected_person_id.capitalize()}")
            lines.append("Option 1 reveals their generated belief statement.")
            lines.append("Option 2 reveals a guaranteed truthful personal trait answer.")

        if self.confession_history:
            lines.append("")
            lines.append("Confession Rooms So Far:")
            for case_no, confessor, rooms in self.confession_history:
                pretty_rooms = ", ".join(self._pretty_name(room) for room in rooms)
                lines.append(
                    f"Case {case_no}: {confessor.capitalize()} -> {pretty_rooms}"
                )

        self._set_notes_text(lines)

    def _on_people_selection_changed(self, _event: object) -> None:
        person = self._selected_person()
        self._update_notes_snapshot(person.person_id if person else None)

    def _capture_backend_output(self, fn) -> list[str]:
        output_capture = io.StringIO()
        with redirect_stdout(output_capture):
            fn()

        rendered = output_capture.getvalue().strip("\n")
        if not rendered:
            return []
        return rendered.splitlines()

    def _append_lines(self, lines: list[str]) -> None:
        for line in lines:
            self.append_log(line)

    def _set_mode(self, mode: str, target: str | None = None) -> None:
        self.current_mode = mode
        self.question_target = target

        if mode == "questioning":
            self.investigation_actions.grid_remove()
            self.questioning_actions.grid()
            if target:
                self.mode_label.configure(text=f"Mode: Interrogating {target.capitalize()}")
            else:
                self.mode_label.configure(text="Mode: Interrogation")
        else:
            self.questioning_actions.grid_remove()
            self.investigation_actions.grid()
            self.mode_label.configure(text="Mode: Investigating")

        self._update_status_labels()
        self._refresh_finale_controls_visibility()

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        widgets = [
            self.review_button,
            self.notepad_button,
            self.end_case_button,
            self.quit_button,
            self.go_room_button,
            self.examine_room_button,
            self.interrogate_button,
            self.accuse_primary_combo,
            self.accuse_secondary_combo,
            self.accuse_button,
            self.inventory_button,
            self.take_item_button,
            self.inventory_combo,
            self.burn_item_button,
            self.ask_belief_button,
            self.ask_trait_button,
            self.stop_interrogation_button,
        ]
        for widget in widgets:
            widget.configure(state=state)

    def _dispatch_command(self, command: str, interrogation_choice: str | None = None) -> list[str]:
        if self.current_game is None:
            return []

        self.append_log(f"> {command}")

        def _run_action() -> None:
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

        self._refresh_dossier_data()
        self._handle_case_transition_if_needed()
        return lines

    def _start_next_case(self) -> None:
        if self._campaign_finished:
            return

        next_iteration = self.current_iteration + 1
        if next_iteration > self.campaign.total_iterations:
            self._finish_campaign()
            return

        # Reset Notepad Combinations when starting a fresh case
        self._reset_notepad_combinations()

        scenario: dict | None = None
        game: MysteryGame | None = None

        def _build() -> None:
            nonlocal scenario, game
            scenario = self.campaign._MysteryCampaign__build_scenario(next_iteration)
            player_role = random.choice([person["id"] for person in scenario["people"]])
            game = MysteryGame(scenario, player_role, self.campaign.total_iterations)

        build_lines = self._capture_backend_output(_build)
        self._append_lines(build_lines)

        if scenario is None or game is None:
            raise RuntimeError("Failed to start next case.")

        self.current_iteration = next_iteration
        self.current_scenario = scenario
        self.current_game = game
        self._current_case_scored = False

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
        self.append_log("Innocents always tell the truth; murderers always lie (unless they are talking about their traits).")
        self.append_log("Plus one dead victim tied to this generation.")
        self.append_log("You may freely explore rooms and search for items (they seem to have some significance).")
        self.append_log(f"You begin in the {self._pretty_name(game.current_room)}.")
        self.append_log("Type 'review rules' to see the facts of the case, or '?' for commands.")

        # Dynamically Generated Relationships
        #self.append_log("")
        #self.append_log("--- Known Relationships ---")
        #people = sorted(self.current_scenario["people"], key=lambda p: p["age"], reverse=True)
        #for i in range(len(people)):
        #    p1 = people[i]
        #    for j in range(i + 1, len(people)):
        #        p2 = people[j]
        #        diff = p1['age'] - p2['age']
        #        if diff >= 20:
        #            rel = "acts as a parental figure to"
        #        elif diff >= 10:
        #            rel = "is an older, protective sibling to"
        #        else:
        #            rel = "is a close peer and rival of"
        #       self.append_log(f"{p1['id'].capitalize()} (age {p1['age']}) {rel} {p2['id'].capitalize()} (age {p2['age']}).")
        #self.append_log("---------------------------")
        #self.append_log("")

        self._set_mode("investigation")
        self._refresh_dossier_data()
        self._set_controls_enabled(True)

    def _handle_case_transition_if_needed(self) -> None:
        if self.current_game is None or self.current_scenario is None:
            return

        if not self.current_game.ended:
            return

        if not self._current_case_scored:
            if getattr(self.current_game, "case_solved", False):
                self.campaign.solved_cases += 1
                self.confession_history.append(
                    (
                        self.current_game.iteration,
                        self.current_game.confessor,
                        list(self.current_game.confession_rooms),
                    )
                )

            if self.current_game.iteration == self.campaign.total_iterations:
                self.campaign.meta_outcome = self.current_game.meta_outcome

            self._current_case_scored = True

        self.campaign.previous_youngest = self.campaign._MysteryCampaign__select_next_youngest(
            self.current_scenario["people"]
        )

        if self.current_game.iteration < self.campaign.total_iterations:
            self.append_log("")
            self.append_log("--- Decades pass. A new generation inherits Blackwood Manor. ---")
            self.append_log("")
            self._start_next_case()
            return

        self._finish_campaign()

    def _finish_campaign(self) -> None:
        if self._campaign_finished:
            return

        self._campaign_finished = True
        self.append_log("")
        self.append_log("=" * 60)
        self.append_log("Campaign complete.")
        self.append_log(
            f"Solved cases: {self.campaign.solved_cases}/{self.campaign.total_iterations}."
        )

        if self.campaign.meta_outcome == "win":
            self.append_log("The cursed heirloom was destroyed. Blackwood Manor is finally free.")
        elif self.campaign.meta_outcome == "loss":
            self.append_log("You burned the wrong item. The curse survives, and the manor remains damned.")
        else:
            self.append_log("The final curse ritual was left unresolved.")

        self._set_controls_enabled(False)

    def on_toggle_notepad(self) -> None:
        """Toggles the embedded Notepad panel's visibility in the main window."""
        if self.notepad_frame.winfo_viewable():
            # Hide it
            self.notepad_frame.grid_remove()
            self.notepad_button.configure(text="Open Notepad")
            self.grid_columnconfigure(2, weight=0)
        else:
            # Show it
            self.notepad_frame.grid(row=0, column=2, rowspan=2, padx=(0, 16), pady=(16, 8), sticky="nsew")
            self.notepad_button.configure(text="Close Notepad")
            self.grid_columnconfigure(2, weight=1)

    def on_review_rules(self) -> None:
        self._dispatch_command("review rules")
        

    def on_inventory(self) -> None:
        if not self._is_finale_ui_unlocked():
            return
        self._dispatch_command("inventory")

    def on_end_case(self) -> None:
        self._dispatch_command("end case")

    def on_quit_case(self) -> None:
        self._dispatch_command("quit")

    def on_go_selected_room(self) -> None:
        room = self._selected_room()
        if room is None:
            messagebox.showinfo("No room selected", "Select a room in the Dossier first.")
            return

        self._dispatch_command(f"go {room}")

    def on_examine_current_room(self) -> None:
        if self.current_game is None:
            return
        self._dispatch_command(f"examine {self.current_game.current_room}")

    def on_begin_interrogation(self) -> None:
        person = self._selected_person()
        if person is None:
            messagebox.showinfo("No person selected", "Select a person in the Dossier first.")
            return

        self._set_mode("questioning", person.person_id)
        self._update_notes_snapshot(person.person_id)

    def on_ask_belief(self) -> None:
        if self.question_target is None:
            return
        self._dispatch_command(
            f"interrogate {self.question_target}",
            interrogation_choice="1",
        )

    def on_ask_personal_trait(self) -> None:
        if self.question_target is None:
            return
        self._dispatch_command(
            f"interrogate {self.question_target}",
            interrogation_choice="2",
        )

    def on_stop_interrogation(self) -> None:
        self._set_mode("investigation")

    def on_accuse(self) -> None:
        first = self.accuse_primary_combo.get().strip().lower()
        second = self.accuse_secondary_combo.get().strip().lower()

        if not first or first.startswith("("):
            messagebox.showinfo("No suspect selected", "Choose at least one suspect in the first accuse dropdown.")
            return

        if not second or second.startswith("("):
            self._dispatch_command(f"accuse {first}")
            return

        self._dispatch_command(f"accuse {first} {second}")

    def on_take_selected_item(self) -> None:
        if not self._is_finale_ui_unlocked():
            return
        item = self._selected_room_item()
        if item is None:
            messagebox.showinfo("No item selected", "Select an item in the current-room list first.")
            return

        self._dispatch_command(f"take {item}")

    def on_burn_selected_item(self) -> None:
        if not self._is_finale_ui_unlocked():
            return
        item = self.inventory_combo.get().strip().lower()
        if not item or item.startswith("("):
            messagebox.showinfo("No inventory item", "Pick an item from your inventory list first.")
            return

        self._dispatch_command(f"burn {item}")

