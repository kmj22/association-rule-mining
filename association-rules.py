# Kevyn Jaremko

NUMBER_OF_DOCUMENTS = 600

def main():
    terms = ["Video", "Console", "Nintendo",
                   "Microsoft", "Xbox", "Playstation", "Sony",
                   "Sega", "Game", "Steam",
                   "Indie", "DLC",
                   "Emulator", "gamer", "multiplayer",
             
                    "Level", "Atari", "GameBoy", "Switch",
                     "Mario", "Platformer", "RPG", "RTS", "Shooter",
                     "Controller"]
    terms = [x.lower() for x in terms]
    
    indexFile = 'invertedIndex.txt'

    index = getPartialIndexFromFile(indexFile, terms)

    associationRuleMining(index, terms)

# Generate high confidence association rules given an index and terms
def associationRuleMining(index, terms):

    minSupport = .4
    minConfidence = .8

    # Store calculated supports for itemsets
    supportOfItemSet = {}
    
    numberOfTerms = len(terms)

    # Initialize list of empty lists for 1 to K itemsets
    frequentItemSets = []
    for i in range( numberOfTerms + 1 ):
        frequentItemSets.append([])

    print("Step 1: Generating frequent itemsets")

    # Add frequent 1-itemsets
    for term in terms:
        items = tuple( [term] )
        
        if getSupport(items, index, supportOfItemSet) > minSupport:
            frequentItemSets[1].append(items)

    # Add frequent 2 to K-itemsets
    for k in range(2, numberOfTerms + 1):
        previousSet = frequentItemSets[k-1]
        n = len(previousSet)

        # Compare each (k-1)-itemset to each other 
        for i in range (0, n-1):
            for j in range (i+1, n):                
                l1 = previousSet[i]
                l2 = previousSet[j]

                # If all terms except the last are the same, combine them                
                if needJoin(l1, l2):
                    l3 = join(l1, l2)

                    if l3 not in frequentItemSets[k] and getSupport(l3, index, supportOfItemSet) > minSupport:
                        frequentItemSets[k].append(l3)

        # Break if there are no itemsets to potentially combine
        if len(frequentItemSets[k]) == 1:
            break

    print("Step 2: Generating high confidence association rules from itemsets")
    rules = []

    # Generate high confidence association rules from each itemset
    for k in range(2, k+1):
        if len(frequentItemSets[k]) == 0:
            break

        # Iterate through each k-itemset
        for itemset in frequentItemSets[k]:

            for item in range(0, k):
                # Copy itemset and remove item
                itemset2 = list(itemset)
                itemset2.pop(item)
                itemset2 = tuple(itemset2)

                supportWithoutItem = getSupport(itemset2, index, supportOfItemSet)
                supportWithItem = getSupport(itemset, index, supportOfItemSet)

                confidence = supportWithItem / supportWithoutItem

                if confidence > minConfidence:
                    rule = []               
                    rule.append(itemset2)           #left-hand side of rule
                    rule.append(itemset[item])      #right-hand side of rule
                    rule.append(supportWithItem)    #support
                    rule.append(confidence)         #confidence
                    
                    rules.append(rule)

    saveRules(rules, 'rules.txt')
    print("Done!")

# Save rules to text file in readable format
def saveRules(rules, file):
    decimalPlaces = 4
    
    f = open(file, 'w+')
    
    for rule in rules:
        line = "{"
        line += ", ".join(rule[0])
        line += "} => {" + rule[1] + "}; support = "
        line += str(round(rule[2], decimalPlaces)) + ", confidence = " + str(round(rule[3], decimalPlaces)) + "\n"
        
        f.write(line)
       
    f.close()

# Restore index from file and return partial index
def getPartialIndexFromFile(indexFile, terms):
    print("Opening index and converting to partial index")

    # Restore index from file
    f = open(indexFile, 'r', encoding='utf-8')
    index = eval(f.read())
    f.close()

    # Extract occurence based partial index
    index = transformToPartialIndex(index, terms)

    return index

# Convert an index to a partial index based on terms
def transformToPartialIndex(index, terms):
    partialIndex = {}

    for term in terms:
        documents = []

        for occurrence in index[term]:
            documents.append(occurrence[0])
        partialIndex[term] = documents

    return partialIndex      

# Determine if two itemsets should be joined
def needJoin(list1, list2):
    for i in range(0, len(list1) - 1):
        if list1[i] != list2[i]:
            return False
    return True

# Join two (k-1)-itemsets
def join(list1, list2):
    list3 = list(list1)
    list3.append(list2[-1])
    return tuple(list3)

# Calculate support of items
def getSupport(items, index, supportOfItemSet):
    lists = []

    # Get all documents each term has appeared in
    for item in items:
        lists.append(index[item])

    numberOfCommonDocuments = len(intersect(*lists))
    support = numberOfCommonDocuments / NUMBER_OF_DOCUMENTS
    
    supportOfItemSet[items] = support
    
    return support

# Find intersection of a list of lists
def intersect(*lists):

    # Convert first list to a set
    # Use set's intersection method to compare with remaining lists    
    return set(lists[0]).intersection(*lists[1:])

main()
