import sys
import nltk
import pickle

entries = nltk.corpus.cmudict.entries()
dictionary = dict((key, value) for key, value in entries)

for arg in sys.argv[1:]:
    file_name = arg
    ext = file_name[-5:]
    base_name = file_name[:-5]
    
    file = open(file_name, 'r')
    output = open("%s-arpabet%s"%(base_name, ext), 'w')
    
    lines = []
    lines_t = []
    i = 0
    
    for line in file:
        i += 1
        tokens = line.split(' ', 1)
        line = (tokens[0], tokens[1].strip())
        lines.append(line)
        
        words = line[1].split()
        try:
            t = [dictionary[word] for word in words]
            lines_t.append((tokens[0], t))
            output.write(tokens[0]+' ')
            
            for word in t:
                for symbol in word[:-1]:
                    output.write(symbol+'-')
                output.write(word[-1]+' ')
            output.write('\n')
                
        except Exception as error:
            print i, error

    #serialize for python
    pic = open(file_name+'.pickle', 'w')
    pickle.dump(lines_t, pic, pickle.HIGHEST_PROTOCOL)  
        
        
    
        