### Written by vapicuno, 2019/06/13 v6
### python 3.5
### Takes in fin which is in showdown teambuilder format
### Spits out sets list by gen, builder by gen, stats by gen, and combined builder.  
### Sorting order is determined by parameters that can be set

from itertools import combinations
import copy
import urllib.request
import json

######## PARAMETERS FOR TUNING TO YOUR LIKING ########

#### --- REPLACE WITH YOUR BUILDER --- ####
fin = 'my_builder.txt'

### DOWNLOAD LATEST POKEDEX
downloadPokedex = True

#### METAGAME PARAMETERS
allGenerations = True
generation = ['gen1ou','gen3ou','gen7ou'] 

### UNFINISHED TEAMS
anomalyThreshold = 0
includeIncompleteTeams = True

#### SETS PARAMETERS (will only affect sets list, not sorted builder)
### --- SET COMBINING
EVthreshold = 40 
IVthreshold = 999 
combineMoves = 2 
### --- MOVE SORT
sortMovesByFrequency = -1
sortMovesByAlphabetical = 0
### --- DISPLAY
showShiny = True
showIVs = False 
showNicknames = True
ignoreSetsFraction = [1/8,1/16,1/32,0] 
showStatisticsInSets = True

#### COMBINED BUILDER PARAMETERS
sortBuilder = True
### --- METAGAME-SORTING
sortGenByFrequency = -1
sortGenByAlphabetical = 0
### --- FOLDER SORTING WITHIN GENERATION
sortFolderByFrequency = -1
sortFolderByAlphabetical = 0
### --- TEAM SORTING WITHIN FOLDER
sortTeamsByLeadFrequencyTeamPreview = 0
sortTeamsByLeadFrequencyNoTeamPreview = -1
sortTeamsByCore = -1
sortTeamsByAlphabetical = 0
coreNumber = 2
### --- POKEMON SORTING WITHIN TEAMS
sortMonsByFrequency = -1
sortMonsByColor = False
gamma = 1

######## PARAMETERS END HERE ########

if downloadPokedex:
    print('Beginning pokedex download...')
    urlPokedex = 'https://raw.githubusercontent.com/Zarel/Pokemon-Showdown/master/data/pokedex.js'  
    urllib.request.urlretrieve(urlPokedex, 'pokedex.js')  
    print('Beginning items download...')
    urlItems = 'https://raw.githubusercontent.com/Zarel/Pokemon-Showdown/master/data/items.js'  
    urllib.request.urlretrieve(urlItems, 'items.js')  
    print('Beginning moves download...')
    urlMoves = 'https://raw.githubusercontent.com/Zarel/Pokemon-Showdown/master/data/moves.js'  
    urllib.request.urlretrieve(urlMoves, 'moves.js')  
    print('Beginning abilities download...')
    urlAbilities = 'https://raw.githubusercontent.com/Zarel/Pokemon-Showdown/master/data/abilities.js'  
    urllib.request.urlretrieve(urlAbilities, 'abilities.js')  
    

pokedexFile = open('pokedex.js')
pokedexStr = pokedexFile.read()
itemsFile = open('items.js')
itemsStr = itemsFile.read()
movesFile = open('moves.js')
movesStr = movesFile.read()
abilitiesFile = open('abilities.js')
abilitiesStr = abilitiesFile.read()
if sortMonsByColor:
    colorsFile = open('colors.js')
    colorsStr = colorsFile.read()
    colors = json.loads(colorsStr)

## Extracts set from text and puts it into a dict
def ExtractSet(setText,inputFormatDense,pokedexStr,itemsStr,abilitiesStr,movesStr):
    setDict = {}
    # for statistics
    setDict['SharedMoves1'] = dict()
    setDict['SharedMoves2'] = dict()
    # initialize gender, nickname, item, name, moves and EVs
    setDict['Gender'] = ''
    setDict['Nickname'] = ''
    setDict['Item'] = ''
    setDict['Ability'] = ''
    setDict['Nature'] = ''
    setDict['Shiny'] = False
    setDict['Moveset'] = list()
    setDict['EVs'] = [0,0,0,0,0,0]
    setDict['IVs'] = [31,31,31,31,31,31]
    setDict['Level'] = 100
    setDict['Happiness'] = 255
    setDict['AlternateForm'] = ''
    
    if inputFormatDense:
        indexDelimiter2 = setText.find('|')
        setDict['Nickname'] = setText[0:indexDelimiter2]
        
        indexDelimiter1 = indexDelimiter2
        indexDelimiter2 = setText.find('|', indexDelimiter1+1)
        if indexDelimiter1 + 1 < indexDelimiter2:
            parseName = setText[indexDelimiter1+1:indexDelimiter2]
            indexNameKey = pokedexStr.find(parseName+': ')
            if indexNameKey == -1: # Alternate Form
                indexNameKey = pokedexStr.find(parseName)
                if indexNameKey == -1:
                    print('Warning: Pokemon name of '.encode('utf-8') + parseName.encode('utf-8','ignore') + ' not found'.encode('utf-8'))
                indexSpecies = pokedexStr.rfind('species: ',0,indexNameKey)
                indexNameKeyBase2 = pokedexStr.rfind('{',0,indexSpecies) - 2
                indexNameKeyBase1 = pokedexStr.rfind('\t',0,indexNameKeyBase2) + 1
                nameKeyBase = pokedexStr[indexNameKeyBase1:indexNameKeyBase2]
                # Assume that Alternate Forms are Base Form + '-' + Descriptor
                setDict['AlternateForm'] = parseName[len(nameKeyBase):].capitalize()
            else:
                indexSpecies = pokedexStr.find('species: ',indexNameKey)
            indexName1 = pokedexStr.find('"',indexSpecies)
            indexName2 = pokedexStr.find('"',indexName1+1)
            setDict['Name'] = pokedexStr[indexName1+1:indexName2]
            if setDict['AlternateForm'] != '':
                setDict['Name'] += '-' + setDict['AlternateForm']
        else:
            setDict['Name'] = setDict['Nickname']
            setDict['Nickname'] = ''
            indexName1 = pokedexStr.find(setDict['Name'])
            if indexName1 == -1:
                indexHyphen = setDict['Name'].find('-')
                indexName1 = pokedexStr.find('"'+setDict['Name'][0:indexHyphen]+'"')
                if indexName1 == -1:
                    print('Warning: Pokemon base form of '.encode('utf-8') + setDict['Name'].encode('utf-8','ignore') + ' not found'.encode('utf-8'))
                setDict['AlternateForm'] = setDict['Name'][indexHyphen+1:]
            
        indexDelimiter1 = indexDelimiter2
        indexDelimiter2 = setText.find('|', indexDelimiter1+1)
        if indexDelimiter1 + 1 < indexDelimiter2:
            parseItem = setText[indexDelimiter1+1:indexDelimiter2]
            indexItemKey = itemsStr.find('"'+parseItem+'": ')
            indexItemName = itemsStr.find('name: ',indexItemKey)
            indexItem1 = itemsStr.find('"',indexItemName)
            indexItem2 = itemsStr.find('"',indexItem1+1)
            setDict['Item'] = itemsStr[indexItem1+1:indexItem2]
        
        indexDelimiter1 = indexDelimiter2
        indexDelimiter2 = setText.find('|', indexDelimiter1+1)
        parseAbility = setText[indexDelimiter1+1:indexDelimiter2]
        if parseAbility == '':
            parseAbility == '0'
        if len(parseAbility) <= 1:
            if 'indexNameKey' in locals():
                indexNameAbilities = indexNameKey
                if setDict['AlternateForm'] != '':
                    indexAbilities = pokedexStr.rfind('abilities: ',0,indexNameAbilities)
                else:
                    indexAbilities = pokedexStr.find('abilities: ',indexNameAbilities)
            else: 
                indexNameAbilities = pokedexStr.find('"'+setDict['Name']+'"')
                if indexNameAbilities == -1:
                    indexHyphen = setDict['Name'].find('-')
                    if indexHyphen == -1:
                        print('Warning: Pokemon base form of '.encode('utf-8') + setDict['Name'].encode('utf-8','ignore') + ' not found'.encode('utf-8'))
                    indexNameAbilities = pokedexStr.find('"'+setDict['Name'][0:indexHyphen]+'"')
                indexAbilities = pokedexStr.find('abilities: ',indexNameAbilities)
            indexAbility = pokedexStr.find(parseAbility+': ',indexAbilities)
            indexAbility1 = pokedexStr.find('"',indexAbility)
            indexAbility2 = pokedexStr.find('"',indexAbility1+1)
            setDict['Ability'] = pokedexStr[indexAbility1+1:indexAbility2]
        elif parseAbility == 'none': 
            setDict['Ability'] = 'none'
        else:
            indexAbilityKey = abilitiesStr.find('"'+parseAbility+'": ')
            if indexAbilityKey == -1:
                setDict['Ability'] = parseAbility
            else:
                indexAbility = abilitiesStr.find('name: ',indexAbilityKey)
                indexAbility1 = abilitiesStr.find('"',indexAbility)
                indexAbility2 = abilitiesStr.find('"',indexAbility1+1)
                setDict['Ability'] = abilitiesStr[indexAbility1+1:indexAbility2]
        
        indexDelimiter1 = indexDelimiter2
        indexDelimiter2 = setText.find('|', indexDelimiter1+1)
        if indexDelimiter1 + 1 < indexDelimiter2:
            indexMove1 = indexDelimiter1
            while indexMove1 < indexDelimiter2:
                indexMove2 = setText.find(',',indexMove1+1,indexDelimiter2)
                if indexMove2 == -1:
                    indexMove2 = indexDelimiter2
                parseMove = setText[indexMove1+1:indexMove2]
                indexMoveKey = movesStr.find('"'+parseMove+'": ')
                if indexMoveKey == -1:
                    indexMove1 = indexMove2
                    continue
                indexMoveName = movesStr.find('name: ',indexMoveKey)
                indexMoveName1 = movesStr.find('"',indexMoveName)
                indexMoveName2 = movesStr.find('"',indexMoveName1+1)
                setDict['Moveset'].append(movesStr[indexMoveName1+1:indexMoveName2])
                indexMove1 = indexMove2
        
        indexDelimiter1 = indexDelimiter2
        indexDelimiter2 = setText.find('|', indexDelimiter1+1)
        if indexDelimiter1 + 1 < indexDelimiter2:
            setDict['Nature'] = setText[indexDelimiter1+1:indexDelimiter2]
        
        indexDelimiter1 = indexDelimiter2
        indexDelimiter2 = setText.find('|', indexDelimiter1+1)
        if indexDelimiter1 + 2 < indexDelimiter2: # 2 takes into account sometimes storing 0 EVs as single 0
            indexEV1 = indexDelimiter1
            for n in range(0,6):
                if n < 5:
                    indexEV2 = setText.find(',',indexEV1+1,indexDelimiter2)
                else:
                    indexEV2 = indexDelimiter2
                EV = setText[indexEV1+1:indexEV2]
                if EV == '':
                    EV = 0
                setDict['EVs'][n] = int(EV)
                indexEV1 = indexEV2
        
        indexDelimiter1 = indexDelimiter2
        indexDelimiter2 = setText.find('|', indexDelimiter1+1)
        if indexDelimiter1 + 1 < indexDelimiter2:
            setDict['Gender'] = setText[indexDelimiter1+1:indexDelimiter2]
        
        indexDelimiter1 = indexDelimiter2
        indexDelimiter2 = setText.find('|', indexDelimiter1+1)
        if indexDelimiter1 + 1 < indexDelimiter2:
            indexIV1 = indexDelimiter1
            for n in range(0,6):
                if n < 5:
                    indexIV2 = setText.find(',',indexIV1+1,indexDelimiter2)
                else:
                    indexIV2 = indexDelimiter2
                IV = setText[indexIV1+1:indexIV2]
                if IV == '':
                    IV = 31
                setDict['IVs'][n] = int(IV)
                indexIV1 = indexIV2
            
        indexDelimiter1 = indexDelimiter2
        indexDelimiter2 = setText.find('|', indexDelimiter1+1)
        if indexDelimiter1 + 1 < indexDelimiter2:
            setDict['Shiny'] = (setText[indexDelimiter1+1:indexDelimiter2] == 'S')
        
        indexDelimiter1 = indexDelimiter2
        indexDelimiter2 = setText.find('|', indexDelimiter1+1)
        if indexDelimiter1 + 1 < indexDelimiter2:
            level = setText[indexDelimiter1+1:indexDelimiter2]
            if level == '':
                setDict['Level'] = 100
            else:
                setDict['Level'] = int(level)
            
        indexDelimiter1 = indexDelimiter2
        happiness = setText[indexDelimiter1+1:]
        if indexDelimiter1 + 1 < indexDelimiter2:
            if level == '':
                setDict['Happiness'] = 255
            else:
                setDict['Happiness'] = int(happiness)
    else:
        stat2index = {
        'HP' : 0,
        'Atk' : 1,
        'Def' : 2,
        'SpA' : 3,
        'SpD' : 4,
        'Spe' : 5
        }
        pos2 = max(setText.rfind(' (F) @ '),setText.rfind(' (F)  \n'))
        if pos2 > -1:
            setDict['Gender'] = 'F'
        else:
            pos2 = max(setText.rfind(' (M) @ '),setText.rfind(' (M)  \n'))
            if pos2 > -1:
                setDict['Gender'] = 'M'
            else:
                pos2 = setText.rfind(' @ ')
                if pos2 == -1:
                    pos2 = setText.find('  \n')
        if setText[pos2-1] == ')':
            pos2 = pos2 - 1;
            pos1 = pos2 - 1;
            while setText[pos1] != '(':
                pos1 = pos1 - 1;
            pos1 = pos1 + 1;
            setDict['Nickname'] = setText[:pos1-2]
        else:
            pos1 = 0;
        posItem = setText.find(' @ ',pos2) + 3
        setDict['Name'] = setText[pos1:pos2]
        if posItem != -1:
            setDict['Item'] = setText[posItem:setText.find('  \n')]

        # obtain shiny status
        posShiny = setText.find('\nShiny: Yes')
        setDict['Shiny'] = (posShiny > -1)
        # obtain current moves
        nlindex = list() # newline indices
        lenset = len(setText)
        posMove1 = lenset
        while setText.rfind('- ',0,posMove1) > -1: 
            posMove1 = setText.rfind('- ',0,posMove1)
            posMove2 = setText.find('\n',posMove1)
            setDict['Moveset'].insert(0,setText[posMove1+2:posMove2-2]) # Extract moves
        partition = posMove1;

        # obtain current EVs
        EVindex = list()
        if setText.find('\nEVs: ') > -1:
            EVindex.append(setText.find('\nEVs: ')+5)
            EVindex.append(setText.find('\n',EVindex[0]))
            EVspaces = [EVindex[0]]
            while EVspaces[-1] < EVindex[1]-1:
                EVspaces.append(setText.find(' ',EVspaces[-1]+1))
            for e in range(0,int(len(EVspaces)/3)):
                EVs = int(setText[EVspaces[3*e]+1:EVspaces[3*e+1]])
                stat = setText[EVspaces[3*e+1]+1:EVspaces[3*e+2]]
                setDict['EVs'][stat2index[stat]] = EVs
        # obtain current IVs
        IVindex = list()
        if setText.find('\nIVs: ') > -1:
            IVindex.append(setText.find('\nIVs: ')+5)
            IVindex.append(setText.find('\n',IVindex[0]))
            IVspaces = [IVindex[0]]
            while IVspaces[-1] < IVindex[1]-1:
                IVspaces.append(setText.find(' ',IVspaces[-1]+1))
            for e in range(0,int(len(IVspaces)/3)):
                IVs = int(setText[IVspaces[3*e]+1:IVspaces[3*e+1]])
                stat = setText[IVspaces[3*e+1]+1:IVspaces[3*e+2]]
                setDict['IVs'][stat2index[stat]] = IVs 
        # obtain Nature
        setDict['Nature'] = ''
        posNature2 = setText.find('Nature  \n') - 1
        if posNature2 > -1:
            posNature1 = setText.rfind('\n',0,posNature2) + 1
            setDict['Nature'] = setText[posNature1:posNature2]
        # obtain current ability
        posAbility1 = setText.find('\nAbility: ') + 10
        posAbility2 = setText.find('\n',posAbility1) - 2
        setDict['Ability'] = setText[posAbility1:posAbility2]
        # obtain current level
        setDict['Level'] = 100
        if setText.find('\nLevel: ') > -1:
            posLevel1 = setText.find('\nLevel: ') + 8
            posLevel2 = setText.find('\n',posLevel1)
            setDict['Level'] = int(setText[posLevel1:posLevel2])
        # obtain current happiness
        setDict['Happiness'] = 255
        if setText.find('\nHappiness: ') > -1:
            posHappiness1 = setText.find('\nHappiness: ') + 12
            posHappiness2 = setText.find('\n',posHappiness1)
            setDict['Happiness'] = int(setText[posHappiness1:posHappiness2])
        # obtain current item
        setDict['Item'] = ''
        postemp = setText.find(setDict['Name']) + len(setDict['Name'])
        if setText.find(' @ ',postemp) > -1:
            posItem1 = setText.find(' @ ',postemp) + 3
            posItem2 = setText.find('\n',posItem1) - 2
            setDict['Item'] = setText[posItem1:posItem2]
    return setDict

def PrintSet(setDict,moveFrequency,showShiny,showIVs,showNicknames,sortMovesByAlphabetical,sortMovesByFrequency):
    index2stat = {
    0 : 'HP',
    1 : 'Atk',
    2 : 'Def',
    3 : 'SpA',
    4 : 'SpD',
    5 : 'Spe'
    }
    setText = ''
    if setDict['Nickname'] != '' and showNicknames:
        setText += setDict['Nickname']
        setText += ' ('
    setText += setDict['Name']
    if setDict['Nickname'] != '' and showNicknames:
        setText += ')'
    if setDict['Gender'] != '':
        setText += ' ('
        setText += setDict['Gender']
        setText += ')'
    if setDict['Item'] != '':
        setText += ' @ '
        setText += setDict['Item']
    setText += '  \nAbility: '
    setText += setDict['Ability']
    if setDict['Level'] != 100:
        setText += '  \nLevel: '
        setText += str(int(setDict['Level']))
    if setDict['Shiny'] == True and showShiny:
        setText += ' \nShiny: Yes'
    if setDict['Happiness'] != 255:
        setText += '  \nHappiness: '
        setText += str(int(setDict['Happiness']))
    if sum(setDict['EVs']) > 0:
        setText += '  \nEVs: '
        for n in range(6):
            if setDict['EVs'][n] > 0:
                setText += str(int(setDict['EVs'][n])) + ' ' + index2stat[n] + ' / '
        if setText[-3:] == ' / ':
            setText = setText[:-3]
    if setDict['Nature'] != '':
        setText += '  \n'
        setText += setDict['Nature']
        setText += ' Nature'
    if 31*6 - sum(setDict['IVs']) > 0.5:
        sharedMoves1 = list(setDict['SharedMoves1'].keys())
        sharedMoves2 = list(setDict['SharedMoves2'].keys())
        sharedMoves = sharedMoves1 + sharedMoves2
        hasHP = 0
        for m in sharedMoves:
            if m.find('Hidden Power') > -1:
                hasHP += 1
        if showIVs or hasHP == 0:
            setText += '  \nIVs: '
            for n in range(6):
                if setDict['IVs'][n] < 31:
                    setText += str(int(setDict['IVs'][n])) + ' ' + index2stat[n] + ' / '
            if setText[-3:] == ' / ':
                setText = setText[:-3]
    setText += '  \n'
    moveList = list(setDict['Moveset'])
    def safeMoveFrequency(name,move,moveFrequency):
        if name in moveFrequency:
            if move in moveFrequency[name]:
                return moveFrequency[name][move]
        return 0
    if sortMovesByAlphabetical != 0:
        moveList.sort(reverse=ToBool(sortMovesByAlphabetical))
    if sortMovesByFrequency != 0:
        moveList.sort(key=lambda k:safeMoveFrequency(setDict['Name'],k,moveFrequency), reverse=ToBool(sortMovesByFrequency))
    for m in moveList:
        if m in setDict['SharedMoves2']:
            moves2 = list(setDict['SharedMoves2'].keys())
            moves2Sorted = sorted(moves2, key=lambda k:sum(list(setDict['SharedMoves2'][k].values())), reverse=True)
            moveText = moves2Sorted[0]
            for mm in range(1,len(moves2Sorted)):
                moveText += ' / '
                moveText += moves2Sorted[mm]
        elif m in setDict['SharedMoves1']:
            moves1 = list(setDict['SharedMoves1'].keys())
            moves1Sorted = sorted(moves1, key=lambda k:setDict['SharedMoves1'][k], reverse=True)
            moveText = moves1Sorted[0]
            for mm in range(1,len(moves1Sorted)):
                moveText += ' / '
                moveText += moves1Sorted[mm]
        else:
            moveText = m
        setText += '- '
        setText += moveText
        setText += '  \n'
    return setText

### Takes a string s and outputs a number that increases with alphanumeric order
### set reverse to True if intending to arrange by descending order
def OrdString(s,reverse):
    if not reverse:
        return s
    ordList = [ord(c) for c in s]
    reverseOrdList = [chr(1114111-o) for o in ordList]
    return ''.join(reverseOrdList)

### Takes a list and returns an list of absolute values.  Acts like np.abs
def AbsList(l):
    return [abs(i) for i in l]

### Takes two lists and subtracts
def SubtractLists(l1,l2):
    if len(l1) != len(l2):
        print('Error: Lists not same size')
        return
    lenl = len(l1)
    l = list()
    for n in range(0,lenl):
        l.append(l1[n]-l2[n])
    return l

def ToBool(n):
    return bool(n-1)

analyzeTeams = True
numTeamsGen = dict()
foutTemplate = fin[:fin.rfind('.')]

setListIncomplete = list()
teamListIncomplete = list()

## Determine parse format
f = open(fin, encoding='utf-8', errors='ignore')
line = f.readline()
inputFormatDense = False
while line:
    if line[0:3] == '===':
        inputFormatDense = False
        break
    if line[0:3] == 'gen':
        inputFormatDense = True
        break
    line = f.readline()
f.close()

if allGenerations:
    generation = list()
    f = open(fin, encoding='utf-8', errors='ignore')
    line = f.readline()
    if inputFormatDense:
        while line:
            if line.find(']') > -1:
                g = line[0:line.find(']')]
                if g not in generation:
                    generation.append(g)
            line = f.readline()
    else:
        while line:
            if line.find('=== [') > -1:
                if line[0:5] == '=== [' and line[-4:-1] == '===':
                    g = line[5:line.find(']')]
                    if g not in generation:
                        generation.append(g)
            line = f.readline()
    f.close()

for gen in generation:
    teamPreview = (int(gen[3]) >= 5)
    setList = list()
    teamList = list()
    folderCount = {'':1}
    rightGen = False if analyzeTeams else True
    f = open(fin, encoding='utf-8', errors='ignore')
    line = f.readline()
    lineCount = 0
    if inputFormatDense:
        while line:
            lineCount += 1
            indexVert = line.find('|')
            indexRight = line.find(']')
            indexRight2 = line.find(']')
            if analyzeTeams:
                if line[0:3] == 'gen':
                    if line.find(gen + ']') > -1:
                        if len(teamList) > 0:
                            teamList[-1]['Index'][1] = len(setList)
                        teamList.append({'Index': [len(setList),len(setList)], 
                                         'Name': line[1+len(gen):indexVert], 
                                         'Gen': gen,
                                         'Folder': '', 
                                         'Score': [0,0,0,0,0,0],
                                         'Line': lineCount,
                                         'Anomalies': 0})
                        if line.find('/') > -1:
                            teamList[-1]['Folder'] = line[1+len(gen):line.find('/')+1]
                            if teamList[-1]['Folder'] not in folderCount:
                                folderCount[teamList[-1]['Folder']] = 1
                            else:
                                folderCount[teamList[-1]['Folder']] += 1
                        indexRight = indexVert # deals with team name delimiter as | instead of ]
                        while indexRight > -1 and indexRight < len(line)-2:
                            indexRight2 = line.find(']',indexRight+1)
                            setList.append(ExtractSet(line[indexRight+1:indexRight2],inputFormatDense,pokedexStr,itemsStr,abilitiesStr,movesStr)) # also covers index of -1 for \n
                            indexRight = indexRight2
            line = f.readline()
        f.close()
    else:
        buffer = line
        lineStatus = 0; # 0 = importable not found, 1 if found
        while line:
            lineCount += 1
            if analyzeTeams:
                if line.find('===') > -1:
                    if line[0:3] == '===' and line[-4:-1] == '===':
                        if line.find('[' + gen +  ']') > -1:
                            if len(teamList) > 0:
                                teamList[-1]['Index'][1] = len(setList)
                            teamList.append({'Index': [len(setList),len(setList)], 
                                             'Gen': gen,
                                             'Name': line[7+len(gen):-5], 
                                             'Folder': '', 
                                             'Score': [0,0,0,0,0,0],
                                             'Line': lineCount,
                                             'Anomalies': 0})
                            if line.find('/') > -1:
                                teamList[-1]['Folder'] = line[7+len(gen):line.find('/')+1]
                                if teamList[-1]['Folder'] not in folderCount:
                                    folderCount[teamList[-1]['Folder']] = 1
                                else:
                                    folderCount[teamList[-1]['Folder']] += 1
                            rightGen = True
                        else:
                            rightGen = False
                            line = f.readline()
                            continue
                elif not rightGen:
                    line = f.readline()
                    continue

            if lineStatus == 0: # If importable has not been found
                mark = line.find('Ability:') # Use Ability to find importable set
                if mark == -1:
                    mark = line.find('Level: ')
                if mark == -1:
                    mark = line.find('Shiny: ')
                if mark == -1:
                    mark = line.find('EVs: ')
                if mark == -1:
                    mark = line.find('Nature  \n')
                    if mark > -1:
                        mark = 0
                if mark == -1:
                    mark = line.find('IVs: ')
                if mark == -1:
                    mark = line.find('-')
                if buffer == '\n':
                    mark == -1
                if mark == 0: 
                    lineStatus = 1
                    montxt = buffer
                buffer = line
            if lineStatus == 1: # If importable has been found
                if line == '\n': # If linebreak has been found
                    setList.append(ExtractSet(montxt,inputFormatDense,pokedexStr,itemsStr,abilitiesStr,movesStr)) # Save as a dict
                    lineStatus = 0
                else:
                    montxt = montxt + line # Add remaining importable lines
            line = f.readline()
        f.close()
        if lineStatus == 1: # If importable has been found
            setList.append(ExtractSet(montxt+'  \n',inputFormatDense,pokedexStr,itemsStr,abilitiesStr,movesStr)) # Save as a dict
            lineStatus = 0
    if analyzeTeams:
        teamList[-1]['Index'][1] = len(setList)
        if len(setList) == teamList[-1]['Index'][0]:
            teamList.pop()
        numTeamsGen[gen] = len(teamList)
    
    ## Determine if team is complete
    
    for n in range(len(teamList)):
        teamList[n]['Anomalies'] = 0
        if teamList[n]['Index'][1] - teamList[n]['Index'][0] < 6 and gen.find('1v1') == -1:
            teamList[n]['Anomalies'] += 6
        for s in setList[teamList[n]['Index'][0]:teamList[n]['Index'][1]]:
            if int(gen[3]) > 2 and sum(s['EVs']) < 508 - (400/s['Level']):
                teamList[n]['Anomalies'] += 1
            if len(s['Moveset']) < 4 and s['Name'] != 'Ditto':
                teamList[n]['Anomalies'] += 1          
        # if team is incomplete, copy team to teamListIncomplete and setListIncomplete
        if teamList[n]['Anomalies'] > anomalyThreshold:
            teamListIncomplete.append(copy.deepcopy(teamList[n]))
            teamListIncomplete[-1]['Index'][0] = len(setListIncomplete)
            setListIncomplete.extend(copy.deepcopy(setList[teamList[n]['Index'][0]:teamList[n]['Index'][1]]))
            teamListIncomplete[-1]['Index'][1] = len(setListIncomplete)
        
    ## Find cores and leads
    
    if analyzeTeams:
        coreList = [dict(),dict(),dict(),dict(),dict(),dict()]
        leadList = dict()
        for n in range(len(teamList)):
            if teamList[n]['Anomalies'] > anomalyThreshold:
                inc = 0 # increment
            else:
                inc = 1
            for p in range(6):
                core = combinations([s['Name'] for s in setList[teamList[n]['Index'][0]:teamList[n]['Index'][1]]],p+1)
                for c in core:
                    cSort = tuple(sorted(c))
                    if cSort in coreList[p]:
                        coreList[p][cSort] += inc
                    else:
                        coreList[p][cSort] = inc
            if not teamPreview:
                if setList[teamList[n]['Index'][0]]['Name'] in leadList:
                    leadList[setList[teamList[n]['Index'][0]]['Name']] += inc
                else:
                    leadList[setList[teamList[n]['Index'][0]]['Name']] = inc
                    
        ## Sort builder
        
        if sortBuilder:
            if sortMonsByFrequency != 0 or sortMonsByColor:
                off = 1 - teamPreview
                def DominantHue(s,gamma,colors,hueOffset):
                    if s['Name'] in colors:
                        colorDict = colors[s['Name']]
                        numColors = len(colorDict['Counts'])
                        weights = [colorDict['Counts'][i]*(colorDict['HSV'][i][1]+colorDict['HSV'][i][2])**gamma for i in range(0,numColors)]
                        dominantIndex = weights.index(max(weights))
                        return (colorDict['HSV'][dominantIndex][0] - hueOffset) % 1.0
                    else:
                        return 0
                def SetSortKey(x):
                    keyList = list()
                    if sortMonsByFrequency != 0:
                        keyList.append(sortMonsByFrequency*coreList[0][(x['Name'],)])
                    if sortMonsByColor:
                        keyList.append(DominantHue(x,gamma,colors,hueOffset))
                    return tuple(keyList)
                for n in range(len(teamList)):
                    if teamList[n]['Anomalies'] > anomalyThreshold:
                        continue
                    teamSets = setList[teamList[n]['Index'][0]+off:teamList[n]['Index'][1]] 
                    if sortMonsByColor:
                        hueOffset = 0
                        if off == 0:
                            dominantHueList = [DominantHue(s,gamma,colors,hueOffset) for s in teamSets]
                            dominantHueList.sort()
                            dominantHueDifferenceList = []
                            for i in range(0,len(dominantHueList)-1):
                                dominantHueDifferenceList.append(dominantHueList[i+1] - dominantHueList[i])
                            dominantHueDifferenceList.append(1 + dominantHueList[0] - dominantHueList[-1])
                            indexMaxHueDiff = dominantHueDifferenceList.index(max(dominantHueDifferenceList))
                            hueOffset = (dominantHueList[indexMaxHueDiff] + dominantHueDifferenceList[indexMaxHueDiff]/2) % 1.0
                        elif off == 1:
                            hueOffset = (DominantHue(setList[teamList[n]['Index'][0]],gamma,colors,hueOffset) - 0.1) % 1.0

                    teamSets.sort(key=SetSortKey)
                    setList[teamList[n]['Index'][0]+off:teamList[n]['Index'][1]] = teamSets
                    hueOffset = 0
                    
            ## Score the teams

            for n in range(len(teamList)):
                if teamList[n]['Anomalies'] > anomalyThreshold:
                    continue
                for p in range(6):
                    core = combinations([s['Name'] for s in setList[teamList[n]['Index'][0]:teamList[n]['Index'][1]]],p+1)
                    numCombinations = 0
                    for c in core:
                        cSort = tuple(sorted(c))
                        teamList[n]['Score'][p] += coreList[p][cSort] 
                        numCombinations += 1
                    teamList[n]['Score'][p] = teamList[n]['Score'][p] / len(teamList) # / numCombinations
                        

    ## Aggregates sets by EV equivalence
    
    # Make set list excluding incomplete teams
    setListComplete = list()
    for n in range(len(teamList)):
        if teamList[n]['Anomalies'] > anomalyThreshold:
            continue
        setListComplete.extend(setList[teamList[n]['Index'][0]:teamList[n]['Index'][1]])
    
    setListNameSorted = sorted(copy.deepcopy(setListComplete), key=lambda x:x['Name']); # Alphabetical-sorted list of sets in dict format
    setListEVcombined = list() # list of dicts of full sets
    chosenMon = '';
    chosenMonIdxEVcombined = 0;
    setListLen = len(setListNameSorted)
    for n in range(setListLen):
        currentSetDict = setListNameSorted[n]
        currentCount = 1

        # determine set equivalence except EVs and IVs
        matchIndex = -1; # matching set index
        nn = chosenMonIdxEVcombined # iterator
        while (matchIndex < 0 and nn < len(setListEVcombined)):
            if currentSetDict['Name'] == chosenMon:  
                if (currentSetDict['Nature'] == setListEVcombined[nn]['Nature'] and
                currentSetDict['Ability'] == setListEVcombined[nn]['Ability'] and
                currentSetDict['Level'] == setListEVcombined[nn]['Level'] and
                currentSetDict['Happiness'] == setListEVcombined[nn]['Happiness'] and
                currentSetDict['Item'] == setListEVcombined[nn]['Item'] and
                set(currentSetDict['Moveset']) == set(setListEVcombined[nn]['Moveset'])):
                    if sum(AbsList(SubtractLists(currentSetDict['EVs'],setListEVcombined[nn]['EVs']))) <= EVthreshold*2:
                        if sum(AbsList(SubtractLists(currentSetDict['IVs'],setListEVcombined[nn]['IVs']))) <= IVthreshold:
                            matchIndex = nn
                            if currentCount <= setListEVcombined[nn]['SubCountEV']:
                                setListEVcombined[nn]['CountEV'] += currentCount
                            else:
                                setListEVcombined[nn]['CountEV'] += currentCount
                                setListEVcombined[nn]['SubCountEV'] = currentCount
                                setListEVcombined[nn]['EVs'] = currentEVs
                                setListEVcombined[nn]['IVs'] = currentIVs
                                setListEVcombined[nn]['Index'] = n
            else:
                chosenMonIdxEVcombined = len(setListEVcombined)
                chosenMon = currentSetDict['Name']
            nn += 1
        if n == 0:
            chosenMonIdxEVcombined = len(setListEVcombined)
            chosenMon = currentSetDict['Name']
        if matchIndex < 0:
            currentSetDict['SubCountEV'] = currentCount;
            currentSetDict['CountEV'] = currentCount;
            currentSetDict['Index'] = n;
            setListEVcombined.append(currentSetDict)

    ## Sorting
    setListEVcombinedRank = [0]*len(setListEVcombined)
    for ii in range(0,len(setListEVcombined)):
        name = setListEVcombined[ii]['Name']
        count = setListEVcombined[ii]['CountEV']
        frontIdent1 = ord(name[0])
        frontIdent2 = ord(name[1])
        posSeparator = max(name.find('-'),name.find(' '))
        if posSeparator > -1:
            backIdent1 = ord(name[posSeparator+1])
            if posSeparator + 2 < len(name):
                backIdent2 = ord(name[posSeparator+2])
            else:
                backIdent2 = 0
        else:
            backIdent1 = ord(name[-2])
            backIdent2 = ord(name[-1])
        setListEVcombinedRank[ii] = (frontIdent1*2**24 + frontIdent2*2**16 + backIdent1*2**8 + backIdent2)*2**10 - count
    setListEVsorted = [setListEVcombined[i[0]] for i in sorted(enumerate(setListEVcombinedRank), key=lambda x:x[1])]

    ## Count move frequency
    moveFrequency = dict()
    monFrequency = dict()
    for ii in range(0,len(setListEVsorted)):
        if not (setListEVsorted[ii]['Name'] in moveFrequency):
            moveFrequency[setListEVsorted[ii]['Name']] = dict()
            monFrequency[setListEVsorted[ii]['Name']] = setListEVsorted[ii]['CountEV']
        else:
            monFrequency[setListEVsorted[ii]['Name']] += setListEVsorted[ii]['CountEV']
        for m in setListEVsorted[ii]['Moveset']:
            if not (m in  moveFrequency[setListEVsorted[ii]['Name']]):
                moveFrequency[setListEVsorted[ii]['Name']][m] = setListEVsorted[ii]['CountEV']
            else:
                moveFrequency[setListEVsorted[ii]['Name']][m] += setListEVsorted[ii]['CountEV']

    len(setListEVsorted)
    ## Aggregates sets by move equivalence up to one slot

    setListMoves1Combined = list() # list of dicts of full sets
    chosenMon = '';
    chosenMonIdxMoves1Combined = 0;
    for n in range(len(setListEVsorted)):
        currentSetDict = setListEVsorted[n]
        currentSetDict['SharedMoves1'] = dict()
        currentCount = setListEVsorted[n]['CountEV']
        currentSetDict['CountMoves'] = setListEVsorted[n]['CountEV']
        # determine set equivalence except EVs and IVs
        matchIndex = -1; # matching set index
        nn = chosenMonIdxMoves1Combined # iterator
        while (matchIndex < 0 and nn < len(setListMoves1Combined) and combineMoves >= 1):
            if currentSetDict['Name'] == chosenMon: 
                if(currentSetDict['Nature'] == setListMoves1Combined[nn]['Nature'] and
                currentSetDict['Ability'] == setListMoves1Combined[nn]['Ability'] and
                currentSetDict['Level'] == setListMoves1Combined[nn]['Level'] and
                currentSetDict['Happiness'] == setListMoves1Combined[nn]['Happiness'] and
                currentSetDict['Item'] == setListMoves1Combined[nn]['Item']):
                    if sum(AbsList(SubtractLists(currentSetDict['EVs'],setListMoves1Combined[nn]['EVs']))) <= EVthreshold*2:
                        if sum(AbsList(SubtractLists(currentSetDict['IVs'],setListMoves1Combined[nn]['IVs']))) <= IVthreshold:
                            # Ensure two movesets are equivalent except for one move
                            moveMatches1 = 0
                            moveMatches2 = 0
                            for move in currentSetDict['Moveset']:
                                if move in setListMoves1Combined[nn]['Moveset']:
                                    moveMatches1 += 1
                                else:
                                    nonCommonMove1 = move
                            for move in setListMoves1Combined[nn]['Moveset']:
                                if move in currentSetDict['Moveset']:
                                    moveMatches2 += 1
                                else:
                                    nonCommonMove2 = move
                            if len(setListMoves1Combined[nn]['Moveset']) == len(currentSetDict['Moveset']):
                                if moveMatches1 == moveMatches2:
                                    if moveMatches1 + 1 == len(setListMoves1Combined[nn]['Moveset']):
                                        # Moves are guaranteed to be in order of popularity by previous construction
                                        if bool(setListMoves1Combined[nn]['SharedMoves1']):
                                            if nonCommonMove2 in setListMoves1Combined[nn]['SharedMoves1']:
                                                setListMoves1Combined[nn]['SharedMoves1'][nonCommonMove1] = currentCount
                                                matchIndex = nn   
                                                setListMoves1Combined[nn]['CountMoves'] += currentCount
                                        else:
                                            setListMoves1Combined[nn]['SharedMoves1'][nonCommonMove2] = setListMoves1Combined[nn]['CountMoves']
                                            setListMoves1Combined[nn]['SharedMoves1'][nonCommonMove1] = currentCount
                                            matchIndex = nn
                                            setListMoves1Combined[nn]['CountMoves'] += currentCount
            else:
                chosenMonIdxMoves1Combined = len(setListMoves1Combined)
                chosenMon = currentSetDict['Name']
            nn += 1
        if n == 0:
            chosenMonIdxMoves1Combined = len(setListMoves1Combined)
            chosenMon = currentSetDict['Name']
        if matchIndex < 0:
            setListMoves1Combined.append(currentSetDict)

    ## Sorting
    setListMoves1CombinedRank = [0]*len(setListMoves1Combined)
    for ii in range(0,len(setListMoves1Combined)):
        name = setListMoves1Combined[ii]['Name']
        count = setListMoves1Combined[ii]['CountMoves']
        frontIdent1 = ord(name[0])
        frontIdent2 = ord(name[1])
        posSeparator = max(name.find('-'),name.find(' '))
        if posSeparator > -1:
            backIdent1 = ord(name[posSeparator+1])
            if posSeparator + 2 < len(name):
                backIdent2 = ord(name[posSeparator+2])
            else:
                backIdent2 = 0
        else:
            backIdent1 = ord(name[-2])
            backIdent2 = ord(name[-1])
        setListMoves1CombinedRank[ii] = (frontIdent1*2**24 + frontIdent2*2**16 + backIdent1*2**8 + backIdent2)*2**10 - count
    setListMoves1Sorted = [setListMoves1Combined[i[0]] for i in sorted(enumerate(setListMoves1CombinedRank), key=lambda x:x[1])]

    ## Aggregates sets by move equivalence up to two slots

    setListMoves2Combined = list() # list of dicts of full sets
    chosenMon = '';
    chosenMonIdxMoves2Combined = 0;
    for n in range(len(setListMoves1Sorted)):
        currentSetDict = setListMoves1Sorted[n]
        currentSetDict['SharedMoves2'] = dict()
        currentCount = setListMoves1Sorted[n]['CountMoves']
        currentSetDict['CountMoves'] = setListMoves1Sorted[n]['CountMoves']
        # determine set equivalence except EVs and IVs
        matchIndex = -1; # matching set index
        nn = chosenMonIdxMoves2Combined # iterator
        while (matchIndex < 0 and nn < len(setListMoves2Combined) and combineMoves >= 2):
            if currentSetDict['Name'] == chosenMon: 
                if(currentSetDict['Nature'] == setListMoves2Combined[nn]['Nature'] and
                currentSetDict['Ability'] == setListMoves2Combined[nn]['Ability'] and
                currentSetDict['Level'] == setListMoves2Combined[nn]['Level'] and
                currentSetDict['Happiness'] == setListMoves2Combined[nn]['Happiness'] and
                currentSetDict['Item'] == setListMoves2Combined[nn]['Item']):
                    if sum(AbsList(SubtractLists(currentSetDict['EVs'],setListMoves2Combined[nn]['EVs']))) <= EVthreshold*2:
                        if sum(AbsList(SubtractLists(currentSetDict['IVs'],setListMoves2Combined[nn]['IVs']))) <= IVthreshold:
                            moveMatches1 = 0
                            moveMatches2 = 0
                            for move in currentSetDict['Moveset']:
                                if move in setListMoves2Combined[nn]['Moveset']:
                                    moveMatches1 += 1
                                else:
                                    nonCommonMove1 = move
                            for move in setListMoves2Combined[nn]['Moveset']:
                                if move in currentSetDict['Moveset']:
                                    moveMatches2 += 1
                                else:
                                    nonCommonMove2 = move
                            if len(setListMoves2Combined[nn]['Moveset']) == len(currentSetDict['Moveset']):
                                if moveMatches1 == moveMatches2:
                                    if moveMatches1 + 1 == len(setListMoves2Combined[nn]['Moveset']):
                                        # Compare equivalence and order of previously slashed moves
                                        if set(currentSetDict['SharedMoves1'].keys()) == set(setListMoves2Combined[nn]['SharedMoves1'].keys()):
                                            order1 = [currentSetDict['SharedMoves1'][key] for key in currentSetDict['SharedMoves1'].keys()]
                                            order2 = [setListMoves2Combined[nn]['SharedMoves1'][key] for key in currentSetDict['SharedMoves1'].keys()]
                                            r = 0
                                            corr = True
                                            while r < len(order1) and corr == True:
                                                s = 0
                                                while s < r and corr == True:
                                                    corr = (order1[r] <= order1[s] and order2[r] <= order2[s]) or (order1[r] >= order1[s] and order2[r] >= order2[s])
                                                    s += 1
                                                r += 1
                                            if corr:
                                                if bool(setListMoves2Combined[nn]['SharedMoves2']):
                                                    if nonCommonMove2 in setListMoves2Combined[nn]['SharedMoves2']:
                                                        setListMoves2Combined[nn]['SharedMoves2'][nonCommonMove1] = currentSetDict['SharedMoves1']
                                                        matchIndex = nn   
                                                        setListMoves2Combined[nn]['CountMoves'] += currentCount
                                                else:
                                                    setListMoves2Combined[nn]['SharedMoves2'][nonCommonMove2] = setListMoves2Combined[nn]['SharedMoves1']
                                                    setListMoves2Combined[nn]['SharedMoves2'][nonCommonMove1] = currentSetDict['SharedMoves1']
                                                    matchIndex = nn
                                                    setListMoves2Combined[nn]['CountMoves'] += currentCount
            else:
                chosenMonIdxMoves2Combined = len(setListMoves2Combined)
                chosenMon = currentSetDict['Name']
            nn += 1
        if n == 0:
            chosenMonIdxMoves2Combined = len(setListMoves2Combined)
            chosenMon = currentSetDict['Name']
        if matchIndex < 0:
            setListMoves2Combined.append(currentSetDict)

    ## Sorting
    setListMoves2CombinedRank = [0]*len(setListMoves2Combined)
    for ii in range(0,len(setListMoves2Combined)):
        name = setListMoves2Combined[ii]['Name']
        count = setListMoves2Combined[ii]['CountMoves']
        frontIdent1 = ord(name[0])
        frontIdent2 = ord(name[1])
        posSeparator = max(name.find('-'),name.find(' '))
        if posSeparator > -1:
            backIdent1 = ord(name[posSeparator+1])
            if posSeparator + 2 < len(name):
                backIdent2 = ord(name[posSeparator+2])
            else:
                backIdent2 = 0
        else:
            backIdent1 = ord(name[-2])
            backIdent2 = ord(name[-1])
        setListMoves2CombinedRank[ii] = (frontIdent1*2**24 + frontIdent2*2**16 + backIdent1*2**8 + backIdent2)*2**10 - count
    setListMoves2Sorted = [setListMoves2Combined[i[0]] for i in sorted(enumerate(setListMoves2CombinedRank), key=lambda x:x[1])]

    ## Print statistics to file
    f = open(foutTemplate + '_' + gen + '_statistics' + '.txt','w',encoding='utf-8', errors='ignore')
    totalMons = sum(list(monFrequency.values()))
    if len(setList) > 0:
        maxNameLen = max([len(s['Name']) for s in setList])
    else:
        maxNameLen = 18
    
    if analyzeTeams:
        if not teamPreview:
            leadFrequencySorted = [(l,leadList[l]) for l in sorted(leadList, key=lambda x:leadList[x], reverse=True)]
            f.write('Team Lead Arranged by Frequency\n')
            f.write(' Counts | Freq (%) | Lead\n')
            for (lead,freq) in leadFrequencySorted:
                f.write((7-len(str(freq)))*' ' + str(freq))
                f.write(' | ')
                percentStr = "{:.3f}".format(freq/len(teamList)*100)
                f.write((8-len(percentStr))*' ' + percentStr)
                f.write(' | ')
                f.write(' '*(maxNameLen-len(lead)) + lead)
                f.write('\n')
            f.write('\n')
        for p in range(6):
            coreFrequencySorted = [(c,coreList[p][c]) for c in sorted(coreList[p], key=lambda x:coreList[p][x], reverse=True)]
            if p == 0:
                f.write('Pokemon Arranged by Frequency\n')
                f.write(' Counts | Freq (%) | Pokemon\n')
            else:
                f.write(str(p+1) + '-Cores Arranged by Frequency\n')
                f.write(' Counts | Freq (%) | Cores\n')
            for (core,freq) in coreFrequencySorted:
                if freq == 0:
                    continue
                f.write((7-len(str(freq)))*' ' + str(freq))
                f.write(' | ')
                percentStr = "{:.3f}".format(freq/len(teamList)*100)
                f.write((8-len(percentStr))*' ' + percentStr)
                f.write(' | ')
                for q in range(p):
                    f.write(' '*(maxNameLen-len(core[q])) + core[q])
                    f.write(', ')
                f.write(' '*(maxNameLen-len(core[p])) + core[p])
                f.write('\n')
            f.write('\n')
    else: 
        monFrequencySorted = [(mon,monFrequency[mon]) for mon in sorted(monFrequency, key=lambda x:monFrequency[x], reverse=True)]
        f.write('Pokemon Arranged by Frequency\n')
        f.write(' Counts | Freq (%) | Pokemon\n')
        for (mon,freq) in monFrequencySorted:
            f.write((7-len(str(freq)))*' ' + str(freq))
            f.write(' | ')
            percentStr = "{:.3f}".format(freq/totalMons*100)
            f.write((8-len(percentStr))*' ' + percentStr)
            f.write(' | ')
            f.write(mon)
            f.write('\n')

    ## Print builder to file by gen
    if analyzeTeams and sortBuilder:
        f = open(foutTemplate + '_' + gen + '_sorted_builder' + '.txt','w',encoding='utf-8', errors='ignore')
        sortTeamsByLeadFrequency = sortTeamsByLeadFrequencyTeamPreview if teamPreview else sortTeamsByLeadFrequencyNoTeamPreview
        ## Define sort key
        def SortKey(x):
            keyList = list()
            if sortFolderByFrequency != 0 or sortFolderByAlphabetical != 0:
                if sortFolderByFrequency != 0:
                    keyList.append(sortFolderByFrequency*folderCount[x['Folder']])
                keyList.append(OrdString(x['Folder'].casefold(),ToBool(sortFolderByAlphabetical)))
            
            if sortTeamsByLeadFrequency != 0 or sortTeamsByCore != 0 or sortTeamsByAlphabetical != 0:
                if sortTeamsByLeadFrequency != 0:
                    if teamPreview:
                        keyList.append(sortTeamsByLeadFrequency*coreList[0][(setList[x['Index'][0]]['Name'],)])
                    else:
                        keyList.append(sortTeamsByLeadFrequency*leadList[setList[x['Index'][0]]['Name']])
                    keyList.append(OrdString(setList[x['Index'][0]]['Name'],False))
                if sortTeamsByCore != 0:
                    keyList.append(sortTeamsByCore*x['Score'][coreNumber-1])
                    keyList.append(OrdString(setList[x['Index'][0]]['Name'],False))
                if sortTeamsByAlphabetical != 0:
                    keyList.append(OrdString(x['Name'].casefold(),ToBool(sortTeamsByAlphabetical)))
            return tuple(keyList)
        
        teamList.sort(key=SortKey)
        
        for n in range(len(teamList)):
            if teamList[n]['Anomalies'] > anomalyThreshold:
                continue
            f.write('=== [' + gen + '] ')
            f.write(teamList[n]['Name'])
            f.write(' ===\n\n')
            for i in range(teamList[n]['Index'][0],teamList[n]['Index'][1]):
                f.write(PrintSet(setList[i],moveFrequency,True,True,True,sortMovesByAlphabetical,sortMovesByFrequency))
                f.write('\n')
            f.write('\n')          

    ## Print sets to file
    for fracThreshold in ignoreSetsFraction:
        if fracThreshold == 0:
            fout = foutTemplate + '_' + gen + '_sets' + '.txt'
        else:
            fout = foutTemplate + '_' + gen + '_sets' + '_cut_' + str(int(1/fracThreshold)) +'.txt'
        f = open(fout,'w',encoding='utf-8', errors='ignore')
        f.write('Built from ' + foutTemplate + '.txt\n')
        f.write('-'*50 + '\n')
        f.write('Fraction of sets ignored: ')
        if fracThreshold == 0:
            f.write('All')
        else: 
            f.write("{:.2f}".format(fracThreshold*100) + '% or 1/' + str(int(1/fracThreshold)))
        f.write('\n')
        f.write('EV movements ignored: ' + str(EVthreshold) + '\n')  
        f.write('IV sum deviation from 31 ignored: ')
        if IVthreshold < 31*6:
            f.write(str(IVthreshold))
        else:
            f.write('All')
        f.write('\n')
        f.write('Moveslots combined: ' + str(combineMoves) + '\n')
        f.write('Move Sort Order: ')
        if sortMovesByFrequency == 1:
            f.write('Increasing Frequency')
        elif sortMovesByFrequency == -1:
            f.write('Decreasing Frequency')
        elif sortMovesByAlphabetical == 1:
            f.write('Increasing Alphabetical')
        elif sortMovesByAlphabetical == -1:
            f.write('Decreasing Alphabetical')
        else:
            f.write('Retained From Import')
        f.write('\n')
        f.write('Show IVs when Hidden Power Type is ambiguous: ')
        f.write('Yes' if showIVs else 'No')
        f.write('\n')
        f.write('Show Shiny: ')
        f.write('Yes' if showShiny else 'No')
        f.write('\n')
        f.write('Show Nicknames: ')
        f.write('Yes' if showNicknames else 'No')
        f.write('\n')
        f.write('-'*50 + '\n')
        f.write('To read statistics:\n')
        f.write('Counts | Frequency given the same Pokemon (%)\n\n')

        for s in setListMoves2Sorted:
            frac = s['CountMoves']/monFrequency[s['Name']]
            if frac >= fracThreshold:
                f.write(PrintSet(s,moveFrequency,showShiny,showIVs,showNicknames,sortMovesByAlphabetical,sortMovesByFrequency))
                if showStatisticsInSets:                
                    f.write('-'*28 + '\n')
                    if bool(s['SharedMoves1']) or bool(s['SharedMoves2']):
                        moveCombinations = list()
                        if bool(s['SharedMoves2']):
                            for m2 in s['SharedMoves2']:
                                for m1 in s['SharedMoves2'][m2]:
                                    moveCombinations.append((m1 + ' / ' + m2, s['SharedMoves2'][m2][m1]))
                        elif bool(s['SharedMoves1']):
                            for m in s['SharedMoves1']:
                                moveCombinations.append((m, s['SharedMoves1'][m]))
                        moveCombinations.sort(key=lambda x:x[1],reverse=True)
                        maxMoveCombinationsNameLen = max([len(m[0]) for m in moveCombinations])
                        maxMoveCombinationsCountLen = max([len(str(m[1])) for m in moveCombinations])
                        for (m,c) in moveCombinations:
                            f.write(m + ' '*(maxMoveCombinationsNameLen-len(m)) + ': ')
                            f.write(' '*(maxMoveCombinationsCountLen-len(str(c))) + str(c) + ' | ' + "{:.1f}".format(c/monFrequency[s['Name']]*100) + '%\n')
                f.write('Total: ' + str(s['CountMoves']) + ' | ' + "{:.1f}".format(frac*100) + '%\n')
                f.write('\n')
        f.close()
    
## Print incomplete teams
f = open(foutTemplate + '_incomplete' + '.txt','w',encoding='utf-8', errors='ignore')
teamListIncomplete.sort(key=lambda x:x['Line'])
for n in range(len(teamListIncomplete)):
    f.write('=== [' + teamListIncomplete[n]['Gen'] + '] ')
    f.write(teamListIncomplete[n]['Name'])
    f.write(' ===\n\n')
    for i in range(teamListIncomplete[n]['Index'][0],teamListIncomplete[n]['Index'][1]):
        f.write(PrintSet(setListIncomplete[i],moveFrequency,True,True,True,0,0))
        f.write('\n')
    f.write('\n')          
f.close()
    
## Print entire builder to file
if analyzeTeams and sortBuilder:
    if sortGenByFrequency != 0:
        generation.sort(key=lambda x:numTeamsGen[x],reverse=ToBool(sortGenByFrequency))
    elif sortGenByAlphabetical != 0:
        generation.sort(reverse=ToBool(sortGenByAlphabetical))
    fo = open(foutTemplate + '_full_sorted_builder' + '.txt','w',encoding='utf-8', errors='ignore')
    
    if includeIncompleteTeams:
        fi = open(foutTemplate + '_incomplete' + '.txt',encoding='utf-8', errors='ignore')
        line = fi.readline()
        while line:
            fo.write(line)
            line = fi.readline()
        fi.close()
    for gen in generation:
        fi = open(foutTemplate + '_' + gen + '_sorted_builder' + '.txt', encoding='utf-8', errors='ignore') 
        line = fi.readline()
        while line:
            fo.write(line)
            line = fi.readline()
        fi.close()
    fo.close()

print('Processing complete.')
print('Find your files in the same directory.')