"""
Check the classifier against worked examples from the official EU guidance
MDCG 2021-24 Rev.1 (April 2026). Each test: (device, class the guidance gives, facts).
The yes/no facts are my reading of each example's intended use.
"""
import importlib

clf = importlib.import_module("03_device_classifier")
make, classify = clf.make, clf.classify

tests = [
    ("Stethoscope", "I", make()),
    ("EEG/ECG electrodes (non-invasive)", "I", make()),
    ("Muscle stimulator", "IIa", make(active=True, purpose="therapeutic")),
    ("TENS device", "IIa", make(active=True, purpose="therapeutic")),
    ("External bone growth stimulator", "IIa", make(active=True, purpose="therapeutic")),
    ("Electroconvulsive therapy equipment", "IIb",
        make(active=True, purpose="therapeutic", hazardous_energy=True)),
    ("External defibrillator, no diagnostic function", "IIb",
        make(active=True, purpose="therapeutic", hazardous_energy=True)),
    ("Lung ventilator", "IIb",
        make(active=True, purpose="therapeutic", hazardous_energy=True)),
    ("AED (diagnostic function drives therapy)", "III",
        make(active=True, purpose="therapeutic", hazardous_energy=True,
             diagnostic_drives_therapy=True)),
    ("Programmer for implantable pulse generator", "III",
        make(active=True, controls_active_implant=True)),
    ("Implantable nerve stimulator", "III",
        make(invasive=True, implantable=True, active=True, purpose="therapeutic")),
    ("Cochlear implant", "III",
        make(invasive=True, implantable=True, active=True, purpose="therapeutic")),
    ("Implantable pacemaker", "III",
        make(invasive=True, implantable=True, active=True, purpose="therapeutic",
             contact_heart_or_cns=True)),
    ("CNS electrodes (implanted)", "III",
        make(invasive=True, implantable=True, contact_heart_or_cns=True)),
    ("Prosthetic heart valve", "III",
        make(invasive=True, implantable=True, contact_heart_or_cns=True)),
    ("Pedicle screws", "IIb", make(invasive=True, implantable=True)),
    ("Intra-ocular lens", "IIb", make(invasive=True, implantable=True)),
        ("Hip joint replacement", "III",
        make(invasive=True, implantable=True, joint_replacement=True)),
    ("Breast implant", "III",
        make(invasive=True, implantable=True, breast_implant_or_mesh=True)),
    ("Dental filling material", "IIa",
        make(invasive=True, implantable=True, placed_in_teeth=True)),
    ("Spinal disc replacement", "III",
        make(invasive=True, implantable=True, spinal_implant=True)),
    ("Electroencephalograph", "IIa",
        make(active=True, purpose="diagnostic", direct_diagnosis=True)),
    ("Electronic thermometer", "IIa",
        make(active=True, purpose="diagnostic", direct_diagnosis=True)),
    ("MRI equipment", "IIa",
        make(active=True, purpose="diagnostic", energy_absorbed=True)),
    ("Evoked response stimulator", "IIa",
        make(active=True, purpose="diagnostic", energy_absorbed=True)),
    ("ICU patient monitor", "IIb",
        make(active=True, purpose="diagnostic", direct_diagnosis=True, vital_danger=True)),
    ("Examination lamp", "I", make(active=True, purpose="diagnostic")),
    ("Electric wheelchair", "I", make(active=True)),
    ("Dental curing light", "I", make(active=True)),
]

passed = 0
for name, expected, facts in tests:
    got, rules = classify(facts)
    ok = got == expected
    passed += ok
    print(f"{'PASS' if ok else 'FAIL'}  {name:<48} guidance: {expected:<4} ours: {got:<4} ({', '.join(rules)})")

print(f"\n{passed} of {len(tests)} match the guidance")