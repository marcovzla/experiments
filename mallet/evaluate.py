from __future__ import division

predicted_tags = []
with open('predicted_tags.txt') as f:
    for line in f:
        if line.startswith('O') or line.startswith('X'):
            predicted_tags.append(line[0])

real_tags = []
with open('real_tags.txt') as f:
    for line in f:
        if line.startswith('O') or line.startswith('X'):
            real_tags.append(line[0])

tp = tn = fp = fn = 0
for r,p in zip(real_tags, predicted_tags):
    if p == 'X':
        if r == p:
            tp += 1
        else:
            fp += 1
    else:
        if r == p:
            tn += 1
        else:
            fn += 1


print 'precision:', tp / (tp + fp)
print 'recall:', tp / (tp + fn)
