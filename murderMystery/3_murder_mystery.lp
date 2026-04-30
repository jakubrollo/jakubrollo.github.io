% This programs instantiates a murder mystery - it establishes the setting:
% Who is the murderer, who was where at time of murder, and some other clues to solving the case.
% With the power of ASP, it is easy to add constraints that make the mystery always solvable.

% Generate
% --------

%  domain pools
name_pool(a, boy, albert).
name_pool(a, boy, alfred).
name_pool(a, girl, agatha).
name_pool(a, girl, agnes).

name_pool(b, boy, bernard).
name_pool(b, boy, bertram).
name_pool(b, girl, beatrice).
name_pool(b, girl, blanche).

name_pool(c, boy, charles).
name_pool(c, boy, clarence).
name_pool(c, girl, clementine).
name_pool(c, girl, cristina).

name_pool(d, boy, desmond).
name_pool(d, boy, douglas).
name_pool(d, girl, diana).
name_pool(d, girl, dorothy).

letter_pool(a). letter_pool(b). letter_pool(c). letter_pool(d).

item_pool(obsidian_ring). item_pool(silver_compass). item_pool(ivory_chess_piece).
item_pool(brass_key). item_pool(porcelain_mask). item_pool(amber_pendant).
item_pool(iron_pocket_watch). item_pool(bone_letter_opener). item_pool(velvet_gloves).
item_pool(jade_snuffbox). item_pool(crystal_vial). item_pool(oak_music_box).

room_pool(foyer). room_pool(study). room_pool(library). room_pool(dining_room).
room_pool(kitchen). room_pool(conservatory). room_pool(gallery). room_pool(ballroom).
room_pool(attic). room_pool(cellar). room_pool(guest_room). room_pool(living_room).

% Facts expected from Python side for each iteration:
%   person(Name).
%   elder(Name).                     % optional (carry-over from previous iteration)
%   selected_weapon(Weapon, Trait).  % optional, can be forced externally
%   victim(Name).                    % required: exactly one dead person (not in person/1)
%   room(Room).
%   item(Item).
%   item_in_room(Item, Room).
%   visited(Person, Room).
%   cursed_heirloom(Item).

% Weapons and required traits for given weapon
weapon(poisoned_cognac, drinks_cognac).
weapon(revolver, owns_gun).
weapon(heavy_candlestick, is_strong).
weapon(dagger, is_agile).

% pick exactly one murder weapon
1 { selected_weapon(W, T) : weapon(W, T) } 1.

% exactly two people have the required trait for the selected weapon
2 { has_trait(P, T) : person(P) } 2 :- selected_weapon(_, T).

% exactly one victim is, and they are not among living people
:- #count{V : victim(V)} != 1.
:- victim(V), person(V).

% Room/item world is injected dynamically from Python each generation. (was easier)
:- #count{R : room(R)} == 0.
:- #count{I : item(I)} == 0.
:- item(I), #count{R : item_in_room(I, R)} != 1.
:- item_in_room(I, R), not item(I).
:- item_in_room(I, R), not room(R).
:- visited(P, R), not person(P).
:- visited(P, R), not room(R).
:- person(P), #count{R : visited(P, R)} != 3.
:- #count{I : cursed_heirloom(I)} != 1.
:- cursed_heirloom(I), not item(I).

% speakers are alive people
speaker(P) :- person(P).

% one or two murderers among speakers
1 { murderer(P) : speaker(P) } 2.

% at least one murderer must have the weapon-required trait
:- selected_weapon(_, T), #count{X : murderer(X), has_trait(X, T)} == 0.

% at least one murderer visited the room containing the cursed item
:- cursed_heirloom(I), item_in_room(I, R), #count{P : murderer(P), visited(P, R)} == 0.

% innocent speakers tell truth, murderers lie
truth_teller(P) :- speaker(P), not murderer(P).
liar(P) :- murderer(P).

% --- GENERATE STATEMENTS ---
possible_statement(P, claims_innocent(P, Q)) :- speaker(P), person(Q), P != Q.
possible_statement(P, claims_implication(Q, R)) :- speaker(P), person(Q), person(R), Q != R, P != Q, P != R.
possible_statement(P, claims_sole_killer(P, Q)) :- speaker(P), person(Q), P != Q.
possible_statement(P, claims_two_killers) :- speaker(P).
possible_statement(P, claims_one_killer) :- speaker(P).
possible_statement(P, claims_is_guilty(Q)) :- speaker(P), person(Q), P != Q.
possible_statement(P, claims_is_innocent(Q)) :- speaker(P), person(Q), P != Q.
possible_statement(P, claims_both_guilty(Q, R)) :- speaker(P), person(Q), person(R), Q != R, P != Q, P != R.
possible_statement(P, claims_xor(Q, R)) :- speaker(P), person(Q), person(R), Q != R, P != Q, P != R.
possible_statement(P, claims_same_status(Q, R)) :- speaker(P), person(Q), person(R), Q != R, P != Q, P != R.

% Each speaker says exactly one statement
1 { statement(P, S) : possible_statement(P, S) } 1 :- speaker(P).

% --- EVALUATE STATEMENTS (REAL WORLD) ---
holds(claims_innocent(P, Q)) :- person(P), person(Q), not murderer(P), not murderer(Q).
holds(claims_implication(Q, R)) :- person(Q), person(R), not murderer(Q).
holds(claims_implication(Q, R)) :- person(Q), person(R), murderer(R).
holds(claims_sole_killer(P, Q)) :- person(P), person(Q), not murderer(P), murderer(Q), #count{X : murderer(X)} == 1.
holds(claims_two_killers) :- #count{X : murderer(X)} == 2.
holds(claims_one_killer) :- #count{X : murderer(X)} == 1.
holds(claims_is_guilty(Q)) :- person(Q), murderer(Q).
holds(claims_is_innocent(Q)) :- person(Q), not murderer(Q).
holds(claims_both_guilty(Q, R)) :- person(Q), person(R), murderer(Q), murderer(R).
holds(claims_xor(Q, R)) :- person(Q), person(R), murderer(Q), not murderer(R).
holds(claims_xor(Q, R)) :- person(Q), person(R), not murderer(Q), murderer(R).
holds(claims_same_status(Q, R)) :- person(Q), person(R), murderer(Q), murderer(R).
holds(claims_same_status(Q, R)) :- person(Q), person(R), not murderer(Q), not murderer(R).

% Enforce truthfulness by role
:- truth_teller(P), statement(P, S), not holds(S).
:- liar(P), statement(P, S), holds(S).

% get unique solutions

% generate counter-example space
alt_murderer(P) | not_alt_murderer(P) :- speaker(P).

alt_size(N) :- N = #count{X : alt_murderer(X)}.

% derive `bot` if the counter-example candidate is INVALID

% invalid if size is not 1 or 2.
bot :- alt_size(0).
bot :- alt_size(N), N > 2.

% invalid if it's exactly the same as our primary `murderer` assignment
is_exact_match(P) :- speaker(P), murderer(P), alt_murderer(P).
is_exact_match(P) :- speaker(P), not murderer(P), not_alt_murderer(P).
n_speakers(N) :- N = #count{P : speaker(P)}.
bot :- n_speakers(N), N = #count{P : is_exact_match(P)}.

% invalid if NO alternate murderer has the required weapon trait
alt_lacks_trait(P) :- alt_murderer(P), selected_weapon(_, T), not has_trait(P, T).
bot :- alt_size(1), alt_murderer(P), alt_lacks_trait(P).
bot :- alt_size(2), alt_murderer(P1), alt_murderer(P2), P1 < P2, alt_lacks_trait(P1), alt_lacks_trait(P2).

% invalid if NO alternate murderer visited the cursed heirloom room
alt_did_not_visit(P) :- alt_murderer(P), cursed_heirloom(I), item_in_room(I, R), not visited(P, R).
bot :- alt_size(1), alt_murderer(P), alt_did_not_visit(P).
bot :- alt_size(2), alt_murderer(P1), alt_murderer(P2), P1 < P2, alt_did_not_visit(P1), alt_did_not_visit(P2).

% invalid if the alternate assignment contradicts any spoken statements
alt_holds(claims_innocent(P, Q)) :- person(P), person(Q), not_alt_murderer(P), not_alt_murderer(Q).
alt_holds(claims_implication(Q, R)) :- person(Q), person(R), not_alt_murderer(Q).
alt_holds(claims_implication(Q, R)) :- person(Q), person(R), alt_murderer(R).
alt_holds(claims_sole_killer(P, Q)) :- person(P), person(Q), not_alt_murderer(P), alt_murderer(Q), alt_size(1).
alt_holds(claims_two_killers) :- alt_size(2).
alt_holds(claims_one_killer) :- alt_size(1).
alt_holds(claims_is_guilty(Q)) :- person(Q), alt_murderer(Q).
alt_holds(claims_is_innocent(Q)) :- person(Q), not_alt_murderer(Q).
alt_holds(claims_both_guilty(Q, R)) :- person(Q), person(R), alt_murderer(Q), alt_murderer(R).
alt_holds(claims_xor(Q, R)) :- person(Q), person(R), alt_murderer(Q), not_alt_murderer(R).
alt_holds(claims_xor(Q, R)) :- person(Q), person(R), not_alt_murderer(Q), alt_murderer(R).
alt_holds(claims_same_status(Q, R)) :- person(Q), person(R), alt_murderer(Q), alt_murderer(R).
alt_holds(claims_same_status(Q, R)) :- person(Q), person(R), not_alt_murderer(Q), not_alt_murderer(R).

not_alt_holds(claims_innocent(P, Q)) :- person(P), person(Q), alt_murderer(P).
not_alt_holds(claims_innocent(P, Q)) :- person(P), person(Q), alt_murderer(Q).
not_alt_holds(claims_implication(Q, R)) :- person(Q), person(R), alt_murderer(Q), not_alt_murderer(R).
not_alt_holds(claims_sole_killer(P, Q)) :- person(P), person(Q), alt_murderer(P).
not_alt_holds(claims_sole_killer(P, Q)) :- person(P), person(Q), not_alt_murderer(Q).
not_alt_holds(claims_sole_killer(P, Q)) :- person(P), person(Q), alt_size(2).
not_alt_holds(claims_sole_killer(P, Q)) :- person(P), person(Q), alt_size(0).
not_alt_holds(claims_two_killers) :- alt_size(1).
not_alt_holds(claims_two_killers) :- alt_size(0).
not_alt_holds(claims_one_killer) :- alt_size(2).
not_alt_holds(claims_one_killer) :- alt_size(0).
not_alt_holds(claims_is_guilty(Q)) :- person(Q), not_alt_murderer(Q).
not_alt_holds(claims_is_innocent(Q)) :- person(Q), alt_murderer(Q).
not_alt_holds(claims_both_guilty(Q, R)) :- person(Q), person(R), not_alt_murderer(Q).
not_alt_holds(claims_both_guilty(Q, R)) :- person(Q), person(R), not_alt_murderer(R).
not_alt_holds(claims_xor(Q, R)) :- person(Q), person(R), alt_murderer(Q), alt_murderer(R).
not_alt_holds(claims_xor(Q, R)) :- person(Q), person(R), not_alt_murderer(Q), not_alt_murderer(R).
not_alt_holds(claims_same_status(Q, R)) :- person(Q), person(R), alt_murderer(Q), not_alt_murderer(R).
not_alt_holds(claims_same_status(Q, R)) :- person(Q), person(R), not_alt_murderer(Q), alt_murderer(R).

% if P is a truth teller, but S doesnt hold -> contradiction -> INVALID -> derive bot
bot :- speaker(P), not_alt_murderer(P), statement(P, S), not_alt_holds(S).
% if P is a liar, but S does hold -> contradiction -> INVALID -> derive bot
bot :- speaker(P), alt_murderer(P), statement(P, S), alt_holds(S).

% fill the whole counter-example space if `bot` is derived
alt_murderer(P) :- bot, speaker(P).
not_alt_murderer(P) :- bot, speaker(P).

% constraint that `bot` MUST be generated (meaning ALL valid counter-examples failed to exist)
:- not bot.

#maximize {
    2,P : statement(P, claims_implication(_,_));
    2,P : statement(P, claims_xor(_,_));
    2,P : statement(P, claims_same_status(_,_));
    1,P : statement(P, claims_both_guilty(_,_))
}.

#show murderer/1.
#show statement/2.
#show selected_weapon/2.
#show has_trait/2.
#show person/1.
#show victim/1.
#show room/1.
#show item/1.
#show item_in_room/2.
#show visited/2.
#show cursed_heirloom/1.
