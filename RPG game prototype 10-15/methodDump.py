import random
import time
import main

#Color inputted text and return it.
def colorText(color, text):
  code = ''
  match color:
    case 'red':
      code = '31'
    case 'green':
      code = '32'
    case 'yellow':
      code = '33'
    case 'blue':
      code = '34'
    case 'purple':
      code = '35'
    case 'cyan':
      code = '36'
    case 'white':
      code = '37'
  return '\033[1;{colorCode};40m'.format(colorCode=code) + str(text) + '\033[0;37;40m'

#Take an inputted string move code and turn it into a list form
def moveDecoder(moveToTranslate):
    
    #Turn the string code into a list of characters for easier reading
    moveCharList = []
    for x in moveToTranslate:
      moveCharList.append(x)

    #Determine what kind of move it is to handle it correctly
    match moveCharList[0]:
      case 'a':
        numberOfRolls = int(moveCharList[1])
        rollOutOf = int(moveCharList[2] + moveCharList[3])
        baseDamage = int(moveCharList[5] + moveCharList[6])
        returnList =['a', executeAttack(numberOfRolls, rollOutOf, baseDamage)]
        match moveCharList[-1]:
          case 'f':
            returnList.append('fire')
        return returnList
      case 's':
        return ['s', 0]
      case 'g':
         return ['g', (random.randint(0, 4))]
      case 'm':
        returnString = ''
        for x in range(1, len(moveCharList)):
          returnString = returnString + str(moveCharList[x])
        return ['m', int(returnString)]
      case 'n':
        return ['n', 0]

#Calculate how much extra or minus damage is dealt based on elemental type
def calclulateTypeAdvantage(attackingType, defendingType):
  if attackingType in defendingType:
    pass

def applyEffect(recipientList, effectInfo):
  for recipient in recipientList:
    effectType = effectInfo[0]
    effectDuration = effectInfo[1]
    effectAmp = effectInfo[2]
    effectAA = -1
    for x in recipient.activeEffects:
      if x[0] == effectInfo[0]:
        effectAA = recipient.activeEffects.index(x)
    if effectAA == -1:
      recipient.activeEffects.append([effectType, effectDuration, effectAmp])
    else:
      recipient.activeEffects[effectAA][1] += effectDuration
      if recipient.activeEffects[effectAA][2] < effectAmp:
        recipient.activeEffects[effectAA][2] /= effectAmp
        recipient.activeEffects[effectAA][2] *= 2
      elif recipient.activeEffects[effectAA][2] > effectAmp:
        effectAmp = (effectAmp / recipient.activeEffects[effectAA][2])
        recipient.activeEffects[effectAA][2] = effectAmp

#Special messages based on if an opponent tries to physically guard against elemental attacks.
def printTypeDamageText(element):
  time.sleep(0.6)
  match element:
    case 'fire':
      print('Your opponent could not hide from your blazing strike.')

#Use a few numbers to randomly roll a damage total and return it, for attacks from codes
def executeAttack(numOfRolls, rollNum, baseDmg):
  damageTotal = baseDmg
  for x in range(0, numOfRolls):
    damageTotal += random.randint(0, rollNum)
  return damageTotal

#An object that contains all the necessary information for a spell. Just a container object.
class Spell():

  name = ''
  spellID = 0
  spellCode = ''
  spellElement = ''
  manaCost = 0

  #Initialize and load all information for the spell from game data
  def loadSpellData(self):
    spellData = pullFromTextAssets('ID:  ' + str(self.spellID))
    self.spellElement = spellData[0].strip('\n')
    self.spellCode = spellData[1]
    self.manaCost = int(spellData[2])
    self.name = spellData[3]

  def __init__(self, ID):
    self.spellID = ID
    self.loadSpellData()

#Turns enemies encountered into easily manipulatable objects.
class Enemy():

  name = ''
  type = 0
  enemyhealth = 0
  enemyCurrentHealth = 0
  enemyguardHealth = 0
  enemyStrength = 0
  enemyInitiative = 0
  enemyConstitution = 0
  enemyIntelligence = 0 
  moveset = []
  movesetPatterns = []
  currentPattern = []
  currentMoveWithinPattern = 0
  nextMove = []
  guarded = False
  activeEffects = []
  physicalAttackX = 1
  physicalDefenseX = 1
  magicAttackX = 1
  magicDefenseX = 1
  stunned = False

  def enemyMagic(self, magicID):
    if magicID == 6:
      print('The ' + colorText('yellow', self.name) + ' enhances their weapon and psyches themself up!')
      self.activeEffects.append([])

  #It is the enemy's turn, so they will make and send their move back to the player.
  def makeMove(self):

      #Set your current move made to the move in the sequence you that are on.
      moveMade = moveDecoder(self.moveset[int(self.currentPattern[self.currentMoveWithinPattern])-1])

      #Move forward in the sequence. If you have finished it and go past, roll a new sequence and reset.
      self.currentMoveWithinPattern += 1
      if self.currentMoveWithinPattern + 1 > len(self.currentPattern):
        self.currentMoveWithinPattern = 0
        self.currentPattern = self.movesetPatterns[random.randint(0, len(self.movesetPatterns) - 1)]

      #Set your next move to the iterated move in the possibly new sequence.
      self.nextMove = moveDecoder(self.moveset[int(self.currentPattern[self.currentMoveWithinPattern])-1])

      #If you are guarding next turn, store the amount you will block for easy access.
      if self.nextMove == 'g':
        self.nextMove = moveDecoder(self.nextMove)

      #Determine what type of move you are making this turn.
      try:
        match moveMade[0]:
          case 'a':
            time.sleep(.5)
            moveMade[1] *= self.physicalAttackX
            print('The ' + self.name + ' attacks for ' + str(round(moveMade[1])) + ' points of damage!')
            return moveMade
          case 'g':
            time.sleep(.5)
            if not self.guarded:
              print('The ' + self.name + ' braces for an attack.')
            return ['g', 0]
          case 's':
            return ['s', 0]
          case 'n':
            return ['n', 0]
          case 'm':
            print('Something magic!')
            return moveMade
      except TypeError:
        return ['n', 0]
  
  #The player has moved, and we need to apply the damage and effects to ourself.
  def applyPlayerMove(self, moveInfo):
    moveAmp = 0

    #Check if you are set to guard as your next move. If so, apply the amount you block for to your guard health.
    try:
      if self.nextMove[0] == 'g':
        self.enemyguardHealth = self.nextMove[1] + (2 * self.enemyConstitution)

    #If a next move has not yet been calculated, do it now and then perform the same check as earlier.
    except IndexError:
      self.nextMove = moveDecoder(self.moveset[int(self.currentPattern[self.currentMoveWithinPattern])-1])
      if self.nextMove[0] == 'g':
        self.enemyguardHealth = moveDecoder(self.nextMove)[1] + (2 * self.enemyConstitution * self.physicalDefenseX)

    #Determine what type of move the player has just hit you with.
    match moveInfo[0]:

      #If it is an attack, perform appropriate measures.
      case 'a':
        moveAmp = moveInfo[1]

        #If the move info is longer than two items, that means it is elemental and cannot be physically blocked.
        if len(moveInfo) <= 2:
          if self.enemyguardHealth >= moveAmp:
            time.sleep(.25)
            print('But it was blocked fully!')
            self.enemyguardHealth = 0
            moveAmp = 0
            self.guarded = True
          if self.enemyguardHealth > 0:
            print('The ' + self.name + ' blocked part of your attack!')
            moveAmp -= self.enemyguardHealth
            self.guarded = True
        else:
          if self.nextMove[0] == 'g':
            printTypeDamageText(moveInfo[2])
            self.guarded = True
        
        #Damage taken is reduced by a factor of the enemy constitution and subtracted from health total.
        damageTaken = round(moveAmp * (1 - (self.enemyConstitution * 0.03))) / self.physicalDefenseX
        print(self.physicalDefenseX)
        time.sleep(.5)
        print('The ' + self.name +' takes ' + colorText('red',str(damageTaken)) + ' damage.\n')
        self.enemyCurrentHealth -= damageTaken
        self.enemyguardHealth = 0

  #Initialize enemy data and load all attributes from file.
  def loadEnemyData(self):

    #Store all data points within a list for later reference
    enemyAttrbList = []
    with open('gameTextAssets.txt', 'r'):
      for x in pullFromTextAssets('ID:  ' + str(self.type)):
        enemyAttrbList.append(x.strip('\n'))

      #Set all easy attributes like stats and health and name
      self.enemyStrength = int(enemyAttrbList[0][-2:])
      self.enemyInitiative = int(enemyAttrbList[1][-2:])
      self.enemyConstitution = int(enemyAttrbList[2][-2:])
      self.enemyIntelligence = int(enemyAttrbList[3][-2:])
      self.enemyhealth = int(enemyAttrbList[4][-3:])

      #Run through all move codes
      for x in range(1, int(enemyAttrbList[5][-2:]) + 1):
        self.moveset.append(enemyAttrbList[5 + x])

      #Find out how many move patterns there are, and list and store them appropriately.
      lineAfterMoves = 6 + len(self.moveset)
      rawList = []
      for x in range (0, int(enemyAttrbList[lineAfterMoves][-2:])):
        for move in enemyAttrbList[x + lineAfterMoves + 1]:
          if (move != ','):
            rawList.append(move)
        self.movesetPatterns.append(rawList)
        rawList = []
      
      #Initialize core variables like name, health, etc.
      self.name = enemyAttrbList[-1]
      self.enemyCurrentHealth = self.enemyhealth
      self.currentMoveWithinPattern = 0

      #Set the next move the enemy will take so that it can be interacted with on turn 1
      self.currentPattern = self.movesetPatterns[random.randint(0, len(self.movesetPatterns) - 1)]
      try:
        if self.nextMove[0] == 'g':
          self.enemyguardHealth = self.nextMove[1] + (2 * self.enemyConstitution)
      except IndexError:
        self.nextMove = moveDecoder(self.moveset[int(self.currentPattern[self.currentMoveWithinPattern])-1])

  #Upon creation of this entity, define name and type.
  def __init__(self, name, type):
    self.name = name
    self.type = type
    self.moveset = []

#Object for areas
class Area:
  name = ""
  number = 0

  cFEnemy = 0
  cFEnvironment = 0
  cFMerchant = 0
  cFNPC = 0
  cFDevilsWheel = 0
  cFHazard = 0
  cFChoice = 0
  cFShrine = 0
  cFBoss = 0
  chanceDistribution = []
  possibleEnemies = []
  currentAreaEffects = []

  #Roll a random encounter type from the list that was previously made and distrubuted using area data
  def rollRandomEncounter(self):
    encounter = random.randint(0, 99)
    returnList = ['n', 0]
    match self.chanceDistribution[encounter]:
      case 1:
        returnList = self.loadCombatEncounter()
    return returnList
  
  #If it is a combat encounter, roll a random enemy and return it with the encounter code
  def loadCombatEncounter(self):
    returnList = ['c']
    enemyRolled = random.randint(1, len(self.possibleEnemies))
    returnList.append(enemyRolled)
    return returnList
  
  #Initialize an area from file.
  def loadAreaFromFile(self, areaNumber):
    areaAttrbList = []
    for x in pullFromTextAssets('Area ' + str(areaNumber)):
      areaAttrbList.append(x[-4:])

    self.cFEnemy = areaAttrbList[0]
    self.cFEnvironment = areaAttrbList[1]
    self.cFMerchant = areaAttrbList[2]
    self.cFNPC = areaAttrbList[3]
    self.cFDevilsWheel = areaAttrbList[4]
    self.cFHazard = areaAttrbList[5]
    self.cFChoice = areaAttrbList[6]
    self.cFShrine = areaAttrbList[7]
    self.cFBoss = areaAttrbList[8]

    for currentEncter, eventChance in enumerate(areaAttrbList):
      for x in range(0, int(eventChance)):
        self.chanceDistribution.append(int(currentEncter) + 1)

    for x in range (0, int(areaAttrbList[9][-4:])):
      self.possibleEnemies.append(int(areaAttrbList[10 + x].strip('\n')))


  def __init__(self, name, number):
    self.name = name
    self.number = number
def printFromTextAssets(neededLine):
  for x in pullFromTextAssets(neededLine):
    print(x.strip('\n'))
def pullFromTextAssets(neededLine):

  #A MESS.
  firstLineToPull = ""
  lastLineToPull = ""
  returnList = []
  with open("gameTextAssets.txt") as file:

    #Run through file and find title needed, then pull the specified exerpt of text that comes after.
    for num, line in enumerate(file):
      if neededLine in line:
        linesToPull = line[-4:].strip("\n").strip(" ")
        firstLineToPull = num + 1
        lastLineToPull = num + int(linesToPull)
        
      #If the title has been found and the first and last lines have been found, pull the text from the file and add it to the return list.
      if firstLineToPull != "" and lastLineToPull != "":
        if num >= int(firstLineToPull) and num < int(lastLineToPull):
          returnList.append(line)
        elif num == int(lastLineToPull):
          returnList.append(line)
          break

  #Return the list that we created.
  return returnList
def searchForItemInFile(itemToSearchFor, fileToSearchIn):

  #Search file for a specific item, and store all lines of those items and return them.
  with open(fileToSearchIn, 'r') as file:
    instances = []
    for line in file.readlines():
      if itemToSearchFor in line:
        instances.append(line)
      else:
        pass
  return instances