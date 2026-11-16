"""Explicit source controls mirrored on PRESETS; never add synthesis controls."""

def enrich(entry):
    name = entry['name']
    for p in entry['parameters']:
        if name == 'Prophet' and p['key'] == 'p143':p['edit_name']='Resonance'
        if name == 'Hera' and p['key'] == 'vcf_resonance':p['edit_name']='VCF Resonance'
        if name == 'Aphex' and p['key'] in ('lpf_reso','hpf_reso'):p['edit_name']=('LPF' if p['key']=='lpf_reso' else 'HPF')+' Resonance'

    profiles = {
        'CS-1': [['p58'], ['p59'], ['p61']],
        'FM-106': [['p11'], ['p12'], ['p13']],
        'FMini-1': [['p105'], ['p106'], ['p107']],
        'Guru-600': [['p113'], ['p114'], ['p116']],
        'OberVave': [['p13'], ['p14'], ['p15']],
        'Prophet': [['p142'], ['p143'], ['p157']],
        'S1Vave': [['p15'], ['p16'], ['p17']],
        'Aphex': [['lpf_cut'], ['lpf_reso'], ['hpf_cut']],
        'Braids': [['cutoff'], ['resonance'], ['timbre']],
        'Hera': [['vcf_cutoff'], ['vcf_resonance'], ['vcf_env']],
        'Plaits': [['timbre'], ['morph'], ['harmonics', 'lpg_colour']],
        'Dexed': [['algorithm'], ['feedback'], ['output_level']],
        'MONO2K': [['p18'], ['p20'], ['p17']],
        'DRUM-X': [['morph'], ['tune'], ['decay']],
        'Elixir': [[f'p{i}' for i in range(38, 44)],
                   [f'p{i}' for i in range(44, 50)],
                   [f'p{i}' for i in range(51, 63, 2)]],
        'Hortator': [[f'p{120+52*i}' for i in range(8)],
                     [f'p{121+52*i}' for i in range(8)],
                     [f'p{3+11*i}' for i in range(8)]],
        'Acid Engine': [['p4'], ['p5'], ['p6']],
        'K-WASUB': [['p28'], ['p29'], ['p31']],
        'Sophie': [[f'p{i:02}_cutoff' for i in range(1, 17)],
                   [f'p{i:02}_resonance' for i in range(1, 17)],
                   [f'p{i:02}_decay' for i in range(1, 17)]],
    }
    if name == 'K-WASUB' and entry.get('variant'):
        profiles[name] = [['p2'], ['p3'], ['p4']]
    # Availability is checked against the current voice/model's actual visible
    # controls. A hidden 6-Op selector can never become a duplicate preset knob.
    keys = {p['key'] for p in entry['parameters']}
    entry['quick_controls'] = [[k for k in candidates if k in keys]
                               for candidates in profiles.get(name, [[], [], []])]
