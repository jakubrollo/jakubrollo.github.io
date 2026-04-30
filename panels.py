from __future__ import annotations
import tkinter as tk
try:
    import customtkinter as ctk  # type: ignore[import-not-found]
except ImportError:
    pass

class GUIPanelsMixin:
    def _build_case_log(self) -> None:
        self.case_log_frame = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=self.COLOR_PANEL,
            border_width=1,
            border_color=self.COLOR_BORDER,
        )
        self.case_log_frame.grid(row=0, column=0, padx=(16, 8), pady=(16, 8), sticky="nsew")
        self.case_log_frame.grid_rowconfigure(1, weight=1)
        self.case_log_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self.case_log_frame,
            text="THE CASE LOG",
            anchor="w",
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color=self.COLOR_TEXT,
        )
        title.grid(row=0, column=0, padx=14, pady=(12, 6), sticky="ew")

        self.case_log_box = ctk.CTkTextbox(
            self.case_log_frame,
            wrap="word",
            fg_color=self.COLOR_CARD,
            text_color=self.COLOR_TEXT,
            corner_radius=10,
            border_width=1,
            border_color=self.COLOR_BORDER,
            font=ctk.CTkFont(family="Consolas", size=13),
        )
        self.case_log_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self.case_log_box.configure(state="disabled")

    def _build_dossier_panel(self) -> None:
        self.dossier_frame = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=self.COLOR_PANEL,
            border_width=1,
            border_color=self.COLOR_BORDER,
        )
        self.dossier_frame.grid(row=0, column=1, padx=(8, 8), pady=(16, 8), sticky="nsew")
        self.dossier_frame.grid_rowconfigure(2, weight=1)
        self.dossier_frame.grid_rowconfigure(4, weight=1)
        self.dossier_frame.grid_rowconfigure(6, weight=1)
        self.dossier_frame.grid_rowconfigure(8, weight=1)
        self.dossier_frame.grid_columnconfigure(0, weight=1)

        dossier_title = ctk.CTkLabel(
            self.dossier_frame,
            text="DOSSIER",
            anchor="w",
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color=self.COLOR_TEXT,
        )
        dossier_title.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")

        rooms_label = ctk.CTkLabel(
            self.dossier_frame,
            text="Rooms",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_MUTED,
        )
        rooms_label.grid(row=1, column=0, padx=12, pady=(6, 4), sticky="nw")

        rooms_holder, self.rooms_listbox = self._create_listbox(self.dossier_frame)
        rooms_holder.grid(row=2, column=0, padx=12, pady=(0, 10), sticky="nsew")

        people_label = ctk.CTkLabel(
            self.dossier_frame,
            text="People",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_MUTED,
        )
        people_label.grid(row=3, column=0, padx=12, pady=(6, 4), sticky="nw")

        people_holder, self.people_listbox = self._create_listbox(self.dossier_frame)
        people_holder.grid(row=4, column=0, padx=12, pady=(0, 10), sticky="nsew")
        self.people_listbox.bind("<<ListboxSelect>>", self._on_people_selection_changed)

        items_label = ctk.CTkLabel(
            self.dossier_frame,
            text="Items In Current Room",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_MUTED,
        )
        items_label.grid(row=5, column=0, padx=12, pady=(6, 4), sticky="nw")

        items_holder, self.items_listbox = self._create_listbox(self.dossier_frame)
        items_holder.grid(row=6, column=0, padx=12, pady=(0, 10), sticky="nsew")

        notes_label = ctk.CTkLabel(
            self.dossier_frame,
            text="Case Notes",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_MUTED,
        )
        notes_label.grid(row=7, column=0, padx=12, pady=(6, 4), sticky="nw")

        self.notes_box = ctk.CTkTextbox(
            self.dossier_frame,
            wrap="word",
            fg_color=self.COLOR_CARD,
            text_color=self.COLOR_TEXT,
            corner_radius=10,
            border_width=1,
            border_color=self.COLOR_BORDER,
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.notes_box.grid(row=8, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self.notes_box.configure(state="disabled")

    def _create_listbox(self, parent: ctk.CTkFrame) -> tuple[ctk.CTkFrame, tk.Listbox]:
        holder = ctk.CTkFrame(
            parent,
            fg_color=self.COLOR_CARD,
            border_width=1,
            border_color=self.COLOR_BORDER,
            corner_radius=10,
        )
        holder.grid_rowconfigure(0, weight=1)
        holder.grid_columnconfigure(0, weight=1)

        listbox = tk.Listbox(
            holder,
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT,
            selectbackground=self.COLOR_ACCENT,
            selectforeground=self.COLOR_BG,
            highlightthickness=0,
            relief="flat",
            activestyle="none",
            exportselection=False,
            font=("Segoe UI", 12),
        )
        listbox.grid(row=0, column=0, padx=(8, 0), pady=8, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(
            holder,
            orientation="vertical",
            command=listbox.yview,
            fg_color=self.COLOR_CARD,
            button_color=self.COLOR_MUTED,
            button_hover_color=self.COLOR_ACCENT,
        )
        scrollbar.grid(row=0, column=1, padx=(4, 8), pady=8, sticky="ns")
        listbox.configure(yscrollcommand=scrollbar.set)

        return holder, listbox

    def _build_action_bar(self) -> None:
        self.action_frame = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=self.COLOR_PANEL,
            border_width=1,
            border_color=self.COLOR_BORDER,
        )
        self.action_frame.grid(row=1, column=0, columnspan=2, padx=16, pady=(8, 16), sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)
        self.action_frame.grid_columnconfigure(1, weight=1)

        self.mode_label = ctk.CTkLabel(
            self.action_frame,
            text="Mode: Investigating",
            anchor="w",
            text_color=self.COLOR_MUTED,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        self.mode_label.grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")

        self.status_label = ctk.CTkLabel(
            self.action_frame,
            text="",
            anchor="e",
            text_color=self.COLOR_MUTED,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        self.status_label.grid(row=0, column=1, padx=14, pady=(10, 4), sticky="e")

        self.investigation_actions = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        self.investigation_actions.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        for i in range(6):
            self.investigation_actions.grid_columnconfigure(i, weight=1)

        self.review_button = ctk.CTkButton(
            self.investigation_actions,
            text="Review Rules",
            command=self.on_review_rules,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_BG,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
        )
        self.review_button.grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        self.notepad_button = ctk.CTkButton(
            self.investigation_actions,
            text="Toggle Notepad",
            command=self.on_toggle_notepad,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_BG,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
        )
        self.notepad_button.grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        
        self.end_case_button = ctk.CTkButton(
            self.investigation_actions,
            text="End Case",
            command=self.on_end_case,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_BG,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
            state="disabled"
        )
        self.end_case_button.grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        self.quit_button = ctk.CTkButton(
            self.investigation_actions,
            text="Quit Case",
            command=self.on_quit_case,
            fg_color=self.COLOR_DANGER,
            hover_color=self.COLOR_DANGER_HOVER,
            text_color=self.COLOR_TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
        )
        self.quit_button.grid(row=0, column=3, padx=6, pady=6, sticky="ew")

        self.command_label = ctk.CTkLabel(
            self.investigation_actions,
            text="Use room/person lists above. Accuse with dropdowns below.",
            anchor="w",
            text_color=self.COLOR_MUTED,
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.command_label.grid(row=0, column=4, columnspan=2, padx=6, pady=6, sticky="ew")

        self.go_room_button = ctk.CTkButton(
            self.investigation_actions,
            text="Go To Selected Room",
            command=self.on_go_selected_room,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_BG,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
        )
        self.go_room_button.grid(row=1, column=0, columnspan=2, padx=6, pady=6, sticky="ew")

        self.examine_room_button = ctk.CTkButton(
            self.investigation_actions,
            text="Examine Current Room",
            command=self.on_examine_current_room,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_BG,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
        )
        self.examine_room_button.grid(row=1, column=2, columnspan=2, padx=6, pady=6, sticky="ew")

        self.interrogate_button = ctk.CTkButton(
            self.investigation_actions,
            text="Interrogate Selected Person",
            command=self.on_begin_interrogation,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_BG,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
        )
        self.interrogate_button.grid(row=1, column=4, columnspan=2, padx=6, pady=6, sticky="ew")

        self.accuse_primary_combo = ctk.CTkComboBox(
            self.investigation_actions,
            values=["(no suspects)"],
            fg_color=self.COLOR_CARD,
            border_color=self.COLOR_BORDER,
            button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_TEXT,
            dropdown_fg_color=self.COLOR_CARD,
            dropdown_text_color=self.COLOR_TEXT,
            dropdown_hover_color=self.COLOR_PANEL,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            height=38,
        )
        self.accuse_primary_combo.grid(row=2, column=0, columnspan=2, padx=6, pady=6, sticky="ew")

        self.accuse_secondary_combo = ctk.CTkComboBox(
            self.investigation_actions,
            values=["(none)"],
            fg_color=self.COLOR_CARD,
            border_color=self.COLOR_BORDER,
            button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_TEXT,
            dropdown_fg_color=self.COLOR_CARD,
            dropdown_text_color=self.COLOR_TEXT,
            dropdown_hover_color=self.COLOR_PANEL,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            height=38,
        )
        self.accuse_secondary_combo.grid(row=2, column=2, columnspan=2, padx=6, pady=6, sticky="ew")

        self.accuse_button = ctk.CTkButton(
            self.investigation_actions,
            text="Accuse (1 or 2 Suspects)",
            command=self.on_accuse,
            fg_color=self.COLOR_DANGER,
            hover_color=self.COLOR_DANGER_HOVER,
            text_color=self.COLOR_TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
        )
        self.accuse_button.grid(row=2, column=4, columnspan=2, padx=6, pady=6, sticky="ew")

        self.finale_actions = ctk.CTkFrame(self.investigation_actions, fg_color="transparent")
        self.finale_actions.grid(row=3, column=0, columnspan=6, padx=0, pady=(2, 0), sticky="ew")

        for i in range(5):
            self.finale_actions.grid_columnconfigure(i, weight=1)

        self.inventory_button = ctk.CTkButton(
            self.finale_actions,
            text="Inventory",
            command=self.on_inventory,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_BG,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
        )
        self.inventory_button.grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        self.take_item_button = ctk.CTkButton(
            self.finale_actions,
            text="Take Selected Item",
            command=self.on_take_selected_item,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_BG,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
        )
        self.take_item_button.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        self.inventory_combo = ctk.CTkComboBox(
            self.finale_actions,
            values=["(inventory empty)"],
            fg_color=self.COLOR_CARD,
            border_color=self.COLOR_BORDER,
            button_color=self.COLOR_ACCENT,
            button_hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_TEXT,
            dropdown_fg_color=self.COLOR_CARD,
            dropdown_text_color=self.COLOR_TEXT,
            dropdown_hover_color=self.COLOR_PANEL,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            height=38,
        )
        self.inventory_combo.grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        self.burn_item_button = ctk.CTkButton(
            self.finale_actions,
            text="Burn Selected Inventory Item",
            command=self.on_burn_selected_item,
            fg_color=self.COLOR_DANGER,
            hover_color=self.COLOR_DANGER_HOVER,
            text_color=self.COLOR_TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
        )
        self.burn_item_button.grid(row=0, column=3, padx=6, pady=6, sticky="ew")

        self.finale_hint_label = ctk.CTkLabel(
            self.finale_actions,
            text="Final ritual controls unlock after solving generation 3.",
            anchor="w",
            text_color=self.COLOR_MUTED,
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self.finale_hint_label.grid(row=0, column=4, padx=6, pady=6, sticky="ew")

        self.finale_actions.grid_remove()

        self.questioning_actions = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        self.questioning_actions.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        for i in range(3):
            self.questioning_actions.grid_columnconfigure(i, weight=1)

        self.ask_belief_button = ctk.CTkButton(
            self.questioning_actions,
            text="Ask Option 1: Belief Statement",
            command=self.on_ask_belief,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_BG,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=40,
        )
        self.ask_belief_button.grid(row=0, column=0, padx=6, pady=6, sticky="ew")

        self.ask_trait_button = ctk.CTkButton(
            self.questioning_actions,
            text="Ask Option 2: Personal Trait (Truth)",
            command=self.on_ask_personal_trait,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_ACCENT_HOVER,
            text_color=self.COLOR_BG,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=40,
        )
        self.ask_trait_button.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        self.stop_interrogation_button = ctk.CTkButton(
            self.questioning_actions,
            text="Stop Interrogation",
            command=self.on_stop_interrogation,
            fg_color=self.COLOR_DANGER,
            hover_color=self.COLOR_DANGER_HOVER,
            text_color=self.COLOR_TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=40,
        )
        self.stop_interrogation_button.grid(row=0, column=2, padx=6, pady=6, sticky="ew")

    def _build_notepad_panel(self) -> None:
        self.notepad_frame = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=self.COLOR_PANEL,
            border_width=1,
            border_color=self.COLOR_BORDER,
        )
        # Not gridded initially
        self.notepad_frame.grid_rowconfigure(1, weight=1)
        self.notepad_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self.notepad_frame,
            text="BLACKWOOD'S NOTEPAD",
            anchor="w",
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color=self.COLOR_TEXT,
        )
        title.grid(row=0, column=0, padx=14, pady=(12, 6), sticky="ew")

        self.user_notes_box = ctk.CTkTextbox(
            self.notepad_frame,
            wrap="word",
            fg_color=self.COLOR_CARD,
            text_color=self.COLOR_TEXT,
            corner_radius=10,
            border_width=1,
            border_color=self.COLOR_BORDER,
            font=ctk.CTkFont(family="Consolas", size=13),
        )
        self.user_notes_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

        combo_title = ctk.CTkLabel(
            self.notepad_frame,
            text="Suspect Combinations Tracker",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.COLOR_TEXT,
        )
        combo_title.grid(row=2, column=0, padx=12, pady=(0, 2), sticky="w")
        
        combo_legend = ctk.CTkLabel(
            self.notepad_frame,
            text="Grey: Unsure | Gold: Possible | Red: Ruled Out",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.COLOR_MUTED,
        )
        combo_legend.grid(row=3, column=0, padx=12, pady=(0, 8), sticky="w")

        self.combo_frame = ctk.CTkFrame(self.notepad_frame, fg_color="transparent")
        self.combo_frame.grid(row=4, column=0, padx=12, pady=(0, 16), sticky="w")

        # Create Buttons for Combinations (A, B, C, D, AB, AC...)
        combos = [
            ("A", 0, 0), ("B", 0, 1), ("C", 0, 2), ("D", 0, 3),
            ("AB", 1, 0), ("AC", 1, 1), ("AD", 1, 2),
            ("BC", 2, 0), ("BD", 2, 1), ("CD", 2, 2)
        ]
        
        self.combo_buttons = {}
        self.combo_states = {}

        for text, r, c in combos:
            self.combo_states[text] = 0
            btn = ctk.CTkButton(
                self.combo_frame,
                text=text,
                width=50,
                height=35,
                fg_color=self.COLOR_CARD,
                border_color=self.COLOR_BORDER,
                border_width=1,
                text_color=self.COLOR_TEXT,
                hover_color=self.COLOR_PANEL,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                command=lambda t=text: self._toggle_combo_state(t)
            )
            btn.grid(row=r, column=c, padx=4, pady=4)
            self.combo_buttons[text] = btn

