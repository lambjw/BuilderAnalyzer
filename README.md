# BuilderAnalyzer
Analyzes Team Builders from Pokemon Showdown, outputs sets compendium, builder statistics, and sorted builders.  
## Prerequisites
Python 3
## Configuration
Most of the instructions below are for fine-tuning.  Some are critical, like the sorting order.  
### Step 1: Identify your File
Replace 
```fin = 'my_builder.txt'```
with your builder name.  
### Step 2: Get Database from Pokemon Showdown
Note: In Python, True and False are case sensitive boolean values, so remember to capitalize!!!
```downloadPokedex``` downloads the Pokemon Showdown Pokedex.  Set to True if you're using for the first time or want to update.  
### Step 3: Which metagames?
```allGenerations = True``` if you want to process all metagames in your builder (default).  
If you want only to process specific metagames, make ```allGenerations = False``` and list them out in ```generation```
### Step 4: What counts as an incomplete team?  
```anomalyThreshold``` is a number that describes how unfinished a team is by looking at remaining EVs, missing moves and missing pokemon.  Set to 0 for strictest, allowing no missed moves and at most 4 EVs lost (80 EVs for LC) (default).  Set to 999 to include all teams regardless of completion.  
```includeIncompleteTeams``` places incomplete teams at the top of the builder if set to True (default)
### Step 5: Sets compendium
```EVthreshold```: Two sets are considered similar if the EV movement is at most this number, ie. 252HP 0Atk and 212HP 40Atk differ by 40EVs.  Set to 0 to distinguish all sets.  
```IVthreshold```: Two sets are considered similar if the IVs differ by at most this number, ie. 31HP and 0HP differ by 31.  Set to 999 to ignore IV differences (recommended)
```combineMoves``` is the number of combined moveslots.  Set to 2 to combine on two moveslots (default).  To distinguish all sets, set to 0.  
```sortMovesByAscendingFrequency, sortMovesByDescendingFrequency, sortMovesByAlphabetical``` tell if/how you want the moves sorted.  Choose at most one to set to True.  To leave moves in original order, set to False.  
```showShiny, showIVs, showNicknames``` describe how you want the sets displayed.  ```showIVs``` is recommended to be false due to possible slashed moves conflict.  
```ignoreSetsFraction``` filters the lowest fraction of these sets away.  ```ignoreSetsFraction = [1/8,1/16,1/32,0]``` removes the least-used 1/8, 1/16, 1/32 sets of each pokemon and writes the sets compendium to different files.  Zero removes no sets.  
```showStatisticsInSets``` displays statistics of set usage if set to True (default)
### Step 6: Builder sort
```sortBuilder``` set to True (default) if you want to receive a sorted builder
```sortGenByAlphabetical, sortGenByReverseAlphabetical, sortGenByFrequency``` tell how you want the metagames sorted.  Choose at most one to set to True.  
```sortFolderByAlphabetical, sortFolderByReverseAlphabetical, sortFolderByFrequency``` tell if/how you want the folders sorted.  Choose at most one to set to True.  Set to False to leave folder order irrelvant.  
```sortTeamsByAlphabetical, sortTeamsByReverseAlphabetical, sortTeamsByLead``` tell how you want the teams sorted.  Choose at most one to set to True.  
If alphabetical sort is not used, then ```sortTeamsByCore``` will sort the builder by usage stats of this core number.  In other words, ```sortTeamsByCore = 2``` will sort teams by usage stats of pairs of pokemon.  
```sortTeamsByMonFrequency``` sorts within the team by individual mon usage if set to True
