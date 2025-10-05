# Appendix

## Purpose
Quick reference for contributors: shared terminology, conventions, a reusable scenario template, ready-made scenarios, and a lightweight QA checklist to keep the bot consistent and bilingual (EN/ES).

---

## Glossary
- **Intent** – user goal label (e.g., `greet`, `goodbye`, `book_appointment`).
- **Entity** – structured value extracted from text (e.g., date, symptom).
- **Slot** – variable stored across turns (e.g., `lang`, `appointment_date`).
- **Response** – predefined message in `domain.yml` (keys `utter_*`).
- **Action** – custom code executed by the bot (in `actions/`; served by `rasa run actions`).
- **Rule** – deterministic mapping (often “intent → response/action”) in `data/rules.yml`.
- **Story** – multi-turn conversation example in `data/stories.yml`.

---

## Repository Map (quick)
- `data/` → `nlu.yml` (intents/entities), `rules.yml`, `stories.yml`
- `domain.yml` → intents, entities, slots, responses, actions
- `config.yml` → NLU pipeline & policies
- `actions/` → custom actions (optional)
- `tests/` → Rasa tests (optional)
- `endpoints.yml`, `credentials.yml` → runtime config

---

## NLU Conventions (EN/ES)
- **Naming**: snake_case (e.g., `tired_sleep_issue`, `book_appointment`).
- **Coverage**: ≥ **10** examples per intent; vary wording/length.
- **Bilingual**: add examples in **English** and **Spanish** for each new intent.
- **No overlap**: keep examples clearly separated across intents.
- **Entities**: annotate where relevant; use synonyms for common variants.
- **Atomic examples**: one clear intention per training example.

---

## Scenario Template (copy/paste)
Use this to propose new conversations before adding training data.

**User story**  
What the user wants to achieve.

**Sample messages (EN & ES)**  
- EN: …  
- ES: …

**Expected bot reply**  
- `utter_*` or action name

**Entities & slots**  
- Which values are extracted and stored?

**Notes / edge cases**  
- Validation rules, fallback behavior, etc.

---

## Scenarios (ready-to-use examples)

### S1 — Book an appointment
**User story**  
A user asks to schedule a medical appointment.

**Sample messages (EN & ES)**  
- EN: *I want to book an appointment* · *Can I schedule a visit?* · *I need an appointment next week*  
- ES: *Quiero una cita* · *¿Puedo agendar una cita?* · *Necesito una cita la próxima semana*

**Expected bot reply**  
- `utter_appointment_ack` (e.g., “Great! What day and time would you like the appointment?”)

**Entities & slots**  
- (Later) date/time → `appointment_date`, `appointment_time`

**Notes / edge cases**  
- If no date/time provided, ask for both.  
- If low NLU confidence, ask a clarifying question instead of proceeding.

---

### S2 — Daytime sleepiness
**User story**  
A user reports excessive daytime sleepiness / can’t stay awake.

**Sample messages (EN & ES)**  
- EN: *I can’t stay awake* · *I’m so sleepy* · *I keep nodding off*  
- ES: *No puedo mantenerme despierto* · *Tengo mucho sueño* · *Me quedo dormido en el día*

**Expected bot reply**  
- `utter_sleep_ack` (e.g., “Got it. How long has this been happening, and how many hours did you sleep last night?”)

**Entities & slots**  
- (Optional) duration, last-night-hours → `sleep_duration`, `sleep_hours`

**Notes / edge cases**  
- If the user expresses crisis/risk language, escalate per safety guidelines (future work).

---

## QA Checklist (quick)
1. `rasa train` completes without errors.  
2. `rasa shell nlu` correctly classifies base + new intents (reasonable confidence).  
3. `rasa shell` produces the expected `utter_*` responses/actions.  
4. No unintended `nlu_fallback` for typical phrases.  
5. If new entities/slots were added, test realistic inputs (dates, symptoms, etc.).

---

## Roadmap (next)
- Language-aware replies (store `lang` via a tiny detection action; condition responses).
- Date/time extraction with **Duckling** for appointment flows.
- Appointment confirmation mini-flow (ask day/time → confirm → finalize).
- Channel integration (e.g., **WhatsApp Cloud API**) when ready.
- Optional CI with `rasa test` to guard against regressions.

---

## Links
- Schedule: https://docs.google.com/document/d/1Fc4Nd6bXYUpguRtHNKKSMtOwxlnK3pX1b9m8A17RnX4/edit?usp=sharing  
- Appendix Doc: https://docs.google.com/document/d/1iTb1mTRsvmgF1rklFITARZv8HsuuzJ4QHgWdADOTos8/edit?tab=t.je7pfpg3diru  
- Scenario Template (Google Doc): https://docs.google.com/document/d/1XXESTDAFcaD2rKV5EP7lajFpS95f8vXbl75qD9VKTjU/edit?tab=t.0  
- Rasa Docs: https://legacy-docs-oss.rasa.com/docs/rasa/
