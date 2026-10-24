"""
EU MDR device classifier (Annex VIII, simplified).
Every rule is checked. If several rules apply, the HIGHEST class wins
(MDR Annex VIII, section 3.5: the strictest rule applies).
"""
ORDER = {"I": 1, "IIa": 2, "IIb": 3, "III": 4}


def make(**facts):
    """Describe a device with yes/no facts. Anything not mentioned is 'no'."""
    device = dict(
        invasive=False,
        implantable=False,
        active=False,                    # needs a power source to work
        purpose="none",                  # "therapeutic", "diagnostic" or "none"
        contact_heart_or_cns=False,      # touches heart, central circulation, brain or spinal cord
        hazardous_energy=False,          # energy given to the body in a potentially hazardous way
        diagnostic_drives_therapy=False, # closed loop / AED: sensing decides the therapy
        controls_active_implant=False,   # controls or influences an active implantable device
        vital_danger=False,              # monitors vital signs where a change is immediately dangerous
        direct_diagnosis=False,          # gives a diagnosis or monitors vital processes
        energy_absorbed=False,           # diagnostic device that supplies energy absorbed by the body
        brain_stimulation=False,
                         joint_replacement=False,         # total or partial joint replacement
        breast_implant_or_mesh=False,    # breast implant or surgical mesh
        spinal_implant=False,            # spinal disc replacement / touches the spinal column
        placed_in_teeth=False,           # dental devices placed in the teeth         # electric/magnetic fields through the skull to change brain activity
    )
              # dental devices placed in the teeth
    device.update(facts)
    return device


def rule_1(d):
    if not d["invasive"]:
        return "I"          # non-invasive devices start at class I


def rule_8(d):
    if not d["implantable"]:
        return None
    if (d["active"] or d["contact_heart_or_cns"] or d["joint_replacement"]
            or d["breast_implant_or_mesh"] or d["spinal_implant"]):
        return "III"        # active implants, heart/CNS, joints, breast, spine
    if d["placed_in_teeth"]:
        return "IIa"        # dental devices placed in the teeth
    return "IIb"            # other implants (a few extra triggers still not coded)


def rule_9(d):
    if d["active"] and d["controls_active_implant"]:
        return "III"        # controls or monitors an active implant
    if d["active"] and d["purpose"] == "therapeutic":
        return "IIb" if d["hazardous_energy"] else "IIa"


def rule_10(d):
    if d["active"] and d["purpose"] == "diagnostic":
        if d["vital_danger"]:
            return "IIb"
        if d["energy_absorbed"] or d["direct_diagnosis"]:
            return "IIa"


def rule_13(d):
    if d["active"]:
        return "I"          # all other active devices


def rule_22(d):
    if d["active"] and d["purpose"] == "therapeutic" and d["diagnostic_drives_therapy"]:
        return "III"


def rule_xvi_brain_stim(d):
    # Brain stimulators with NO medical purpose were reclassified (Reg. 2022/2347)
    if d["active"] and d["brain_stimulation"] and d["purpose"] == "none":
        return "III"


RULES = {"Rule 1": rule_1, "Rule 8": rule_8, "Rule 9": rule_9,
         "Rule 10": rule_10, "Rule 13": rule_13, "Rule 22": rule_22,
         "Annex XVI reclass": rule_xvi_brain_stim}


def classify(d):
    """Return (class, [rules that gave that class])."""
    results = {name: fn(d) for name, fn in RULES.items() if fn(d)}
    top = max(results.values(), key=lambda c: ORDER[c])
    return top, [name for name, c in results.items() if c == top]


devices = {
    "Stethoscope": make(),
    "Deep brain stimulator": make(
        invasive=True, implantable=True, active=True,
        purpose="therapeutic", contact_heart_or_cns=True),
    "Automated external defibrillator": make(
        active=True, purpose="therapeutic",
        hazardous_energy=True, diagnostic_drives_therapy=True),
    "Low-energy muscle stimulator": make(active=True, purpose="therapeutic"),
    # judgement calls: you decide whether each flag is justified
    "TMS (magnetic brain stimulation)": make(
        active=True, purpose="therapeutic", hazardous_energy=True),
    "tDCS (weak electrical stimulation)": make(
        active=True, purpose="therapeutic", hazardous_energy=False),
    "TMS, research use (no medical aim)": make(
        active=True, purpose="none", hazardous_energy=True, brain_stimulation=True),
    "Vagus nerve stimulator (implanted)": make(
        invasive=True, implantable=True, active=True, purpose="therapeutic"),
}

if __name__ == "__main__":
    for name, facts in devices.items():
        cls, rules = classify(facts)
        print(f"{name:<38} Class {cls:<4} ({', '.join(rules)})")