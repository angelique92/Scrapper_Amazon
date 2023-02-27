# libraries
import numpy as np
import matplotlib.pyplot as plt

# Affiche un diagramme 
# Les 3 paramètre correspond aux listes de résultat obtenue pour les 3 algorightme FOREST DESICIONTREE CNN
# Selon l'index de l element dans list on a la methode de vectorisation 
# soit index 0 > TFID 
#      index 1 > NGRAM
def diagramme(l1,l2,l3):
    barWidth = 0.3
    # The x position of bars
    r1 = np.arange(len(l1))
    r2 = [x + barWidth for x in r1]
    r3 = [x + barWidth for x in r2]
    
    # Create blue bars
    plt.bar(r1, l1, width = barWidth, color = 'blue', edgecolor = 'black',  capsize=7, label='FOREST')
    
    # Create cyan bars
    plt.bar(r2, l2, width = barWidth, color = 'cyan', edgecolor = 'black', capsize=7, label='DESICION TREE')


    # Create grey bars
    plt.bar(r3, l3, width = barWidth, color = 'grey', edgecolor = 'black', capsize=7, label='CNN')
    
    
    # general layout
    plt.xticks([r + barWidth for r in range(len(l1))], ['TFID', 'NGRAM'])
    plt.ylabel('Accuracy %')
    plt.legend()
    
    # Show graphic
    plt.show()
