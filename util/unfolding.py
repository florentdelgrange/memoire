"""Prism mdp unfodling

This script allows to unfold a mdp from a prism file (for a reward bounded reachability problem).

Usage:
    unfolding.py PRISM_FILE (-t <reward> <T> <threshold>)... [-o OUTPUT_FILE_NAME]
    unfolding.py (-h | --help)

Options:
  -h --help                                                             Display help.
  -o <file_name> --out <file_name>                                      Output unfolded prism file.
  -t <reward> <T> <threshold> --target_label <reward> <T> <threshold>   Reward's name, the target set and its threshold (following this reward).
"""

from docopt import docopt
import stormpy
import sys
from collections import deque

def get_labels(model):
    labels = {}
    for state in model.states:
        for label in model.labels_state(state.id):
            if label not in labels:
                labels[label] = deque()
            labels[label].append(state.id)
    labels.pop('init', None)
    return labels

def unfold_mdp(model, thresholds, model_name='model'):
    """
    Note :
        - rewards must be integer
    """

    res = deque(
        'mdp\n\n\
module unfolded_{}\n\n\
s: [0..{}] init {};\n'.format(
        model_name,
        model.nr_states - 1,
        model.initial_states[0])
        )

    for name in model.reward_models.keys():
        res.append('v_{}: [0..{}] init 0;\n'.format(name, thresholds[name] + 1))

    res.append('\n')

    i = 0
    for state in model.states:
        for action in state.actions:
            res.append("[a{}_{}] s={} -> ".format(state, action, state))
            for tr_num, transition in enumerate(action.transitions):
                res.append("{} : (s'={})".format(transition.value(),
                    transition.column))
                for name in thresholds:
                    res.append(" & (v_{}'=min(v_{}+{:d}, {}))".format(
                        name, name,
                        int(model.reward_models[name].state_action_rewards[i]),
                        thresholds[name] + 1))

                if tr_num < len(action.transitions) - 1:
                    res.append(' + ')
                else:
                    res.append(';\n')
                    i += 1
    res.append('\nendmodule')

    return res

def build_prism_file(prism_file, target_labels):
    prism_program = stormpy.parse_prism_program(prism_file)
    model = stormpy.build_model(prism_program)

    thresholds = {}
    for name in target_labels:
        for _, threshold in target_labels[name]:
            thresholds[name] = threshold

    res = unfold_mdp(model, thresholds, prism_file.split('/')[-1].split('.')[0])

    res.append('\n\n')

    labels = get_labels(model)
    temp = {}

    for name in target_labels:
        for label, threshold in target_labels[name]:
            if label in temp:
                temp[label].append((name, threshold))
            else:
                temp[label] = [(name, threshold)]

    target_labels = temp

    for label in labels:
        if label in target_labels:
            for name, threshold in target_labels[label]:
                res.append('label "{}_{}" = ({}) & v_{} <= {};\n'.format(
                    label, name,
                    ' | '.join(['s={}'.format(s) for s in labels[label]]),
                        name, threshold))
        else:
            res.append('label "{}" = {};\n'.format(
                label,
                ' | '.join(['s={}'.format(s) for s in labels[label]])))
    return ''.join(res)

if __name__ == '__main__':
    #path = sys.argv[1]
    #x = build_prism_file(path, {'weights': [('T', 8)], 'test': [('G', 14)]})
    #with open('unfolded_{}'.format(path.split('/')[-1]), 'w') as f:
    #    f.write(x)
    args = docopt(__doc__)
    path = args['PRISM_FILE']
    target_labels = {}
    for i, name in enumerate(args['--target_label']):
        if name not in target_labels:
            target_labels[name] = deque()
        target_labels[name].append((args['<T>'][i], eval(args['<threshold>'][i])))

    print(target_labels)
    unfolded_mdp = build_prism_file(path, target_labels)

    output_file = 'unfolded_{}'.format(path.split('/')[-1]) \
        if not args['--out'] else args['--out']
    with open(output_file, 'w') as f:
        f.write(unfolded_mdp)
