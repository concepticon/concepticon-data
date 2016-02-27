from concepticondata.commands import reflexes
checklist = ['rain', 'spring','you', 'grease', 'palm', 'live', 
        'to blow (a. of the wind, b. with the mouth)', 'chop', 'right', 'tear',
        'leaf', 'snow', 'to live', 'nail', 'sow', 'lie', 
        'vagina or breast/milk', 'dull', 'rain', 
        'louse (a. general term, or b. head louse)',
        'to smell', 'Rain', '*you',
        'dry (a. general term, b. to dry up)', 'FLY', 
        'chicken',
        'burn',
        'breast',
        'hot', 'hurt', 'earth',
        'short (a. in height, b. in length)',
        'light',
        'ground',
        'dumb',
        'thin',
        'old',
        'louse',
        'think',
        'day',
        'smell',
        'dream',
        'fat',
        'you (thou)',
        'child',
        'work',
        'fur',
        'pig',
        'pupil',
        'mouse', 'fly', 'sweat', 'flesh', 'front', 
        'to climb (a. ladder, b. mountain)', 'thin (object)',
        'taste'
        ]


D,G = reflexes(path='../concepticondata')

def print_out():
    count = 1
    for k in G:
        if k not in checklist:
            if len(set([x[0] for x in G[k]])) > 1:
                print(count,'|', '{0:20}'.format(k),'|', '; '.join(sorted(set([x[1] for x in G[k]])))
                
                )
                count += 1

print_out()
