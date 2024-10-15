import math
import os
import random
import time
import methodDump as mD

foresightActive = False
menuLine = '--------------------------------------------------------------'
affirmitive = ["yes", "y"]
negative = ["no", "n"]
validActions = ['guard', 'attack', 'm1', 'm2', 'm3', 'm4', 'wait']
validSpellActions = ['m1', 'm2', 'm3', 'm4']
diedToYourOwnSpell = False

def printBattleUI():
  print(enemyEncountered.activeEffects)
  print(player.activeEffects)
  tempStringVar1 = ''
  tempStringVar2 = ''
  manaBankString = '     '
  overHealthString = '     '
  if player.manaBank > 0:
    manaBankString = mD.colorText('blue', ' (' + str(round(player.manaBank)) + ')+')
  if player.overHealth > 0:
    overHealthString = mD.colorText('red', ' (' + str(round(player.overHealth)) + ')+')

  print(menuLine)
  print('PLAYER:           \\    /  _______              ' + enemyEncountered.name + ':')

  tempStringVar1 = str(round(player.currentHealth)) + '/' + str(player.maxHealth) + ' HP' + overHealthString
  tempStringVar2 = str(round(enemyEncountered.enemyCurrentHealth)) + '/' + str(enemyEncountered.enemyhealth) + ' HP'
  print(tempStringVar1 + '      \\  /  |______             ' + tempStringVar2)
  tempStringVar1 = str(round(player.currentMana)) + '/' + str(player.maxMana) + ' MP' + manaBankString
  tempStringVar2 = str(0) + '/' + str(0) + ' MP'
  print(tempStringVar1 + '       \\/.   ______|.           ' + tempStringVar2)
  print(menuLine)
  print('[attack]: Physical Attack                [guard]: Put up guard \n[stat]: View character info              [info]: Examine enemy\n[spell]: View known spells               [wait]: Skip one turn\n[item]: View usable items                [log]: View enemy log')
def printSpellUI():

  print(menuLine)

  print('Currently learned spells: \n')
  for num, x in enumerate(playerLearnedSpells, 1):
    if x != 0:
      print('[m{enum}]'.format(enum=num) + mD.colorText('yellow',x.name.strip('\n')) + '       -->        Cost: ' + mD.colorText('blue', str(x.manaCost)))
    else:
      print('[Empty]')

  print(menuLine)
  input()
def magicActionsBeforeEnemyMove():
  if player.actionCode[0] != 'm':
    return
  effectID = player.actionCode[1]
  if effectID == 4:
    print('You throw up a field of protection, hoping to turn your enemy\'s attack right back at it.')
    time.sleep(0.5)
    if (enemyEncountered.nextMove[0] == 'a'):
      player.guardHealth = 10 * (1 + (playerIntelligence * 0.14))
      player.manaBankAge = 1
    else:
      print('Having no attack to absorb, it sucks energy from you instead.')
      player.currentMana -= 15
      player.currentHealth-= 5
      if player.currentHealth <= 0:
        global diedToYourOwnSpell 
        diedToYourOwnSpell = True
      time.sleep(0.2)
      print('You lose {hpLost} health and {manaLost} mana.'.format(manaLost=mD.colorText('blue', '15'), hpLost=mD.colorText('red', '5')))
      time.sleep(0.4)
  if effectID == 5:
    print('The ground becomes unstable, lowering everyone\'s physical attack for the next three turns')
    mD.applyEffect([enemyEncountered, player], ['weakness', 4, 50])
  if effectID == 6:
    print('You magically enhance your weapon, making its attacks more potent.')
    mD.applyEffect([player], ['strength', 4, 45])
  if effectID == 7:
    print('You guard, waiting for the perfect moment for a counterattack.')
  if effectID == 8:
    print('You taunt your enemy! Accepting the challenge, its defense lowers and its physical attack increases.')
    mD.applyEffect([enemyEncountered], ['strength', 5, 50])
    mD.applyEffect([enemyEncountered], ['exposed', 5, 50])
  if effectID == 9:
    if player.manaBank > 0:
      print('You take a deep breath, letting the energy in your mana bank patch your wounds and clear your mind.')
      player.currentHealth += player.manaBank
      print('You restore ' + mD.colorText('green', str(player.manaBank)) + ' health.')
      player.manaBank = 0
      player.manaBankAge = 0
      if player.currentHealth > player.maxHealth:
        player.overHealth += player.currentHealth - player.maxHealth
        player.currentHealth = player.maxHealth
    else:
      print('You take a deep breath... and realize that you have no mana bank to restore your wounds! Nothing happens.')
  if effectID == 10:
    print('In an extremely painful process, you convert some of your blood into mana!')
    player.currentMana += player.currentHealth * 0.6
    print('You gain ' + mD.colorText('blue', player.currentHealth * 0.6) + ' mana, losing ' + mD.colorText('red', player.currentHealth * 0.6) + ' health.')
    player.currentHealth *= 0.4
  print('')
def checksAfterEnemyMove():
  if player.manaBankAge == 2:
    player.manaBankAge = 0
    if round(player.manaBank) > 0:
      damageTaken = round(player.manaBank *  (1 - (playerIntelligence * 0.05)))
      print('You cannot hold onto the energy you captured any longer, and it explodes in your face! \nYou take ' + mD.colorText('red', str(damageTaken)) + ' damage.')
      player.currentHealth -= damageTaken
    player.manaBank = 0
  if player.manaBankAge == 1:
    player.manaBankAge = 2

  if player.currentHealth < player.maxHealth and player.overHealth > 0:
    player.currentHealth += player.overHealth
    if player.maxHealth - player.currentHealth < 0:
      player.overHealth = 0 - (player.maxHealth - player.currentHealth)
    else:
      player.overHealth = 0
  
  calibrateEffectsAtRoundEnd(player)
  calibrateEffectsAtRoundEnd(enemyEncountered)
def calibrateEffectsAtRoundEnd(entity):
  entity.physicalAttackX = 1
  entity.physicalDefenseX = 1
  entity.magicAttackX = 1
  entity.magicDefenseX = 1
  deleteList = []
  for effects in entity.activeEffects:
    effects[1] -= 1
    if effects[1] == 0:
      deleteList.append(entity.activeEffects.index(effects))
    else:
      match effects[0]:
        case 'strength':
          entity.physicalAttackX += effects[2] / 100
        case 'weakness':
          entity.physicalAttackX -= effects[2] / 100
        case 'fortified':
          entity.physicalDefenseX += effects[2] / 100
        case 'exposed':
          entity.physicalDefenseX -= effects[2] / 100
        case 'arcane boost':
          entity.magicAttackX += effects[2] / 100
        case 'drained':
          entity.magicAttackX -= effects[2] / 100
  for x in deleteList:
    del(entity.activeEffects[x])

#Player specific variables, if is to condense
if (True):
  playerName = ""
  playerStrength = 0
  playerInitiative = 0
  playerConstitution = 0
  playerIntelligence = 0
  playerLevel = 0
  playerExperience = 0
  playerHealth = 0
  playerMana = 0
  #Hand 1, Hand 2, Armor, Trinkets 1-3
  playerEquipment = [0, 0, 0, 0, 0, 0]
  playerLearnedSpells = [0, 0, 0, 0]
  playerInventory = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  playerArea = 0


class playerEntity():

  strength = 0
  initiative = 0
  constitution = 0
  intelligence = 0
  maxHealth = 0
  currentHealth = 0
  guardHealth = 0
  currentMana = 0
  maxMana = 0
  actionCode = ''
  manaBank = 0
  manaBankAge = 0
  overHealth = 0
  activeEffects = []
  physicalAttackX = 1
  physicalDefenseX = 1
  magicAttackX = 1
  magicDefenseX = 1
  stunned = False

  def takeAction(self, enemyAppliedTo):
    actionTaken = ''
    self.actionCode = ''

    while actionTaken not in validActions:
      if foresightActive:
        print(enemyEncountered.nextMove)
      printBattleUI()
      actionTaken = input('Your move: ')
      match actionTaken:
        case 'stat':
          pass
        case 'spell':
          time.sleep(0.2)
          os.system('cls')
          printSpellUI()
        case 'item':
          pass
        case 'info':
          pass
        case 'log':
          pass
        case 'wait':
          self.actionCode = ['n', 0]
      
      if actionTaken in validSpellActions:
        spellUsed = playerLearnedSpells[int(actionTaken[-1])-1]
        if (spellUsed != 0):
          usedSpellCost = spellUsed.manaCost
          if player.manaBankAge == 2:
            if player.manaBank >= usedSpellCost:
              usedSpellCost = 0
            else:
              usedSpellCost -= player.manaBank
          if player.currentMana >= usedSpellCost:
            player.currentMana -= usedSpellCost
            self.actionCode = mD.moveDecoder(spellUsed.spellCode)
            if self.actionCode[0] == 'a':
              self.actionCode[1] *= (1 + (playerIntelligence * 0.07))
              if player.manaBank > 0:
                if player.manaBank < spellUsed.manaCost:
                  addedDamage = 1 + ((spellUsed.manaCost / player.manaBank) / 2)
                  player.manaBank = 0
                else:
                  addedDamage = 1.5
                  player.manaBank -= spellUsed.manaCost
                self.actionCode[1] *= addedDamage
            if self.actionCode[0] == 'm':
              if player.manaBank > 0:
                player.manaBank -= spellUsed.manaCost
              if player.manaBank < 0:
                player.manaBank = 0
            self.actionCode.append(spellUsed.spellElement)
          else:
            print('Mana is too low.')
            actionTaken = ''
            time.sleep(0.5)
            os.system('cls')
        else:
          print('You cannot use an empty spell!')
          actionTaken = ''
          time.sleep(0.5)
          os.system('cls')
      os.system('cls')
    match actionTaken:
      case 'attack':
        self.actionCode = ['a', (1 + (playerStrength * 0.07)) * self.rollPlayerAttack(2 + playerStrength, 2, 3)]
      case 'guard':
        self.actionCode = ['g', (2 * player.constitution + random.randint(0, 4))]
    
    match self.actionCode[0]:
      case 'a':
        damageDealt = self.actionCode[1]
        if len(self.actionCode) == 2:
          damageDealt *= player.physicalAttackX
        else:
          damageDealt *= player.magicAttackX
        self.actionCode[1] = damageDealt
        print('You attack for ' + str(damageDealt) + ' damage.')
        enemyEncountered.applyPlayerMove(self.actionCode)
      case 'g':
        print('You defend as best you can.')
        player.guardHealth += self.actionCode[1]

  def rollPlayerAttack(self, baseDmg, numOfRolls, rollNum):
    damageTotal = baseDmg
    for x in range(0, numOfRolls):
      damageTotal += random.randint(0, rollNum)
    return damageTotal

  def applyEnemyMove(self, moveGiven):
    if moveGiven[0] != 'n':
      moveType = moveGiven[0]
      moveAmp = 0
      match moveType:
        case 'a':
          moveAmp = moveGiven[1]

          if player.manaBankAge == 1:
            player.manaBank += round(moveAmp)
            print('The ' + enemyEncountered.name + '\'s attack is caught and transferred to your mana bank!')

          if self.guardHealth >= moveAmp:
            time.sleep(.3)
            print('And you blocked it fully!')
            self.guardHealth = 0
            moveAmp = 0
          else:
            moveAmp -= self.guardHealth
          time.sleep(.3)
          print('You take ' + mD.colorText('red', str(round(moveAmp * (1 - (playerConstitution * player.physicalDefenseX * 0.035))))) + ' damage.')
          self.currentHealth -= round(moveAmp * (1 - (playerConstitution * player.physicalDefenseX * 0.035)))
          self.guardHealth = 0
        case 'g':
          pass


  def __init__(self):
    self.strength = playerStrength
    self.initiative = playerInitiative
    self.constitution = playerConstitution
    self.intelligence = playerIntelligence
    self.maxHealth = playerHealth
    self.currentHealth = playerHealth
    self.maxMana = playerMana
    self.currentMana = self.maxMana

#While a character is not yet loaded:
charLoaded = False
while not charLoaded:

  def characterCreation():

    #Loop until the user is happy with character
    done = ""
    newCharacterInfo = []
    characterPool = ["Warrior", "Mage", "Rogue"]
    characterStatPool = [[5, 3, 4, 3], [2, 4, 2, 6], [3, 6, 3, 4]]
    characterSpellPool = [[8, 6, 7, 0], [4, 3, 10, 9], [0, 0, 0, 0]]

    while done not in affirmitive:
      os.system("cls")
      newCharacterInfo = []

      #Get the character's name
      print("What is your first party member's name?")
      newCharacterInfo.append(input("Name: "))
      os.system('cls')

      #Character selection screen
      characterChoice = '?'

      #Screen loops until valid character choice is entered
      while characterChoice != "1" and characterChoice != "2" and characterChoice != "3":
        mD.printFromTextAssets('Character Select Screen')
        characterChoice = input("")

        #If the user enters a question mark, show the stat inforomation
        if characterChoice == "?":
          os.system('cls')
          mD.printFromTextAssets("Stat Information")
          input("\n\nEnter to continue.")
        os.system('cls')

        #If the user enters a number, add the character to the new character info
        if characterChoice == "1" or characterChoice == "2" or characterChoice == "3":
          newCharacterInfo.append(int(characterChoice))

      #Verify that all information is correct
      print("Is this information correct?")
      print((newCharacterInfo[0]) + " the " +
            (characterPool[int(newCharacterInfo[1]) - 1]))
      done = (input("Y/N: ")).lower()

    #When done with information gathering, create character in file
    os.system('cls')
    print("Creating character...")
    with open("characterinfo.txt", 'a') as file:

      #Add all character information to the file in order
      file.write("!" + newCharacterInfo[0] + " the " +
                 characterPool[int(newCharacterInfo[1]) - 1] + "\n")

      #Writing Stats
      charStatList = characterStatPool[int(newCharacterInfo[1]) - 1]
      for x in charStatList:
        file.write(str(x) + "\n")

      #Level and Experience
      file.write("-\n")
      file.write('1\n0\n')

      #Vitals (Health and Mana)
      file.write("-\n")
      file.write(str(int(charStatList[2]) * 5 + 10) + '\n')
      file.write(str(int(charStatList[3]) * 8 + 20) + '\n')

      #Class specific equipment (coming later once IDs work)
      file.write("-\n")
      file.write('0\n0\n0\n0\n0\n0\n')

      #Spells known, also class specific (coming later once spell IDs work)
      file.write("-\n")
      for x in characterSpellPool[int(newCharacterInfo[1]) - 1]:
        file.write(str(x) + '\n')

      #Inventory creation
      file.write("-\n")
      for x in range(0, 10):
        file.write("0\n")

      #Area of the character
      file.write("-\n")
      file.write("0\n")

    print('Character created! Returning to home screen.')
  def loadCharacterFile():

    global playerName
    global playerStrength
    global playerInitiative
    global playerConstitution
    global playerIntelligence 
    global playerLevel
    global playerExperience
    global playerHealth
    global playerMana
    #Hand 1, Hand 2, Armor, Trinkets 1-3
    global playerEquipment
    global playerLearnedSpells
    global playerInventory
    global playerArea

    #Load character file and apply information to appropriate variables (will encrypt before release)
    infoToAdd = []
    with open("characterinfo.txt", 'r') as charInfo:
      for line in charInfo:
        if line.strip('\n') != '-':
          infoToAdd.append(line.strip('\n'))

    #Add information to appropriate variables
    playerName = infoToAdd[0].strip("!\n")
    playerStrength = int(infoToAdd[1])
    playerInitiative = int(infoToAdd[2])
    playerConstitution = int(infoToAdd[3])
    playerIntelligence = int(infoToAdd[4])
    playerLevel = int(infoToAdd[5])
    playerExperience = int(infoToAdd[6])
    playerHealth = int(infoToAdd[7])
    playerMana = int(infoToAdd[8])
    for num in range(0, 6):
      playerEquipment[num] = int(infoToAdd[9 + num])
    for num in range(0, 4):
      if int(infoToAdd[15 + num]) != 0:
        playerLearnedSpells[num] = mD.Spell(int(infoToAdd[15 + num]))
      else:
        playerLearnedSpells[num] = 0

    for num in range(0, 10):
      playerInventory[num] = int(infoToAdd[19 + num])
    playerArea = int(infoToAdd[29])

    print("Character loaded!")

  #Game Start
  print("Welcome to the SigmaSlicer.")

  #Check if needed game files are present. If not, force quit.
  try:
    with open("gameTextAssets.txt"):
      pass
  except FileNotFoundError:
    print(
        "Files critical to the function of this game are missing. Please redownload or fix the issue."
    )
    time.sleep(7)
    exit()

  #Check if the player has a save file. If not, create one.
  try:
    with open("characterinfo.txt", "r"):
      pass
  except FileNotFoundError:
    #No character files found, creating a new file
    print("You do not have a character. Would you like to create one?")
    create = (input("Y/N: ")).lower()
    if create in affirmitive:
      characterCreation()
    elif create in negative:
      print("Quitting game.")
      exit()
  os.system('cls')

  #If the player has a character, ask if they want to load it. Loop until either quit or character loaded.
  #If there is a character info file but no character, or incompete info, reset it.
  if len(mD.searchForItemInFile('!', 'characterinfo.txt')) == 0:
    print(
        "Either your character is corrupted, or there is some error on our end. Delete stored information?"
    )
    delete = (input("Y/N: ")).lower()

    #If the user wants to delete the character info, delete it. Otherwise, close.
    if delete in affirmitive:
      os.remove("characterinfo.txt")
      print("Character deleted. Restarting program.")
      time.sleep(1.5)
      exit()
    elif delete in negative:
      print("Quitting game.")
      time.sleep(1.5)
      exit()

  #If a character exists in the file, ask if they want to load it. Otherwise, create new
  else:
    with open("characterinfo.txt", "r") as charInfo:
      print("Welcome adventurer! I remember you as being: " +
            str(charInfo.readlines(1)[0]).strip('!'))
      print(
          "Use this character? (Y/N), N will delete the character and begin a new character creation."
      )
      create = (input('')).lower()

      #Old file is decided not to be used, delete and create new
      if create in negative:
        charInfo.close()
        os.remove("characterinfo.txt")
        print("Character deleted. Creating new character.")
        time.sleep(1.5)
        characterCreation()

      #With player consent, load selected character file.
      elif create in affirmitive:
        print("Loading character...")
        loadCharacterFile()
        charLoaded = True

#Entering Gameplay Loop
currentArea = mD.Area("Meadows", 1)
currentArea.loadAreaFromFile(1)
activelyPlaying = True
print('Welcome to the SigmaSlicer! You are in area one. Press enter to begin your journey.')
input('')
os.system('cls')

#Initialize player and begin gameplay loop
player = playerEntity()
while activelyPlaying:
    currentEncounter = currentArea.rollRandomEncounter()
    inEncounter = True

    #Determine what kind of encounter it is and handle it properly
    match currentEncounter[0]:

      #If the event is a combat event, load the enemy you face and begin the encounter
      case 'c':
        enemyEncountered = mD.Enemy('', currentEncounter[1])
        enemyEncountered.loadEnemyData()
        print('You have encountered a ' + mD.colorText('yellow', enemyEncountered.name) + '!')
        time.sleep(.5)

        #Until one combatant is dead, loop through the turn based combat.
        while inEncounter:
          #The player takes their action, goes through menus, etc.
          player.takeAction(enemyEncountered)

          #The magic checks that occur after the player move but before the enemy now occur.
          magicActionsBeforeEnemyMove()

          #If the enemy is dead upon attack impact, end the encounter.
          if enemyEncountered.enemyCurrentHealth <= 0:
            inEncounter = False
            print(enemyEncountered.name + ' defeated!')
            break

          #If we have not ended the encounter, apply the enemy move after a short delay.
          if inEncounter:
            time.sleep(.3)
            player.applyEnemyMove(enemyEncountered.makeMove())
            player.guardHealth = 0

          #Magic checks at the end of the turn will now occur.
          checksAfterEnemyMove()

          #Should the player die, end the entire sequence.
          if player.currentHealth <= 0:
            activelyPlaying = False
            inEncounter = False
          
          #Still in combat encounter, but all checks and moves are done. Awaiting player action.
          time.sleep(.5)
          input('Enter to continue. ')
          os.system('cls')
        
        #The encounter has ended and the enemy is dead. Delete it.
        time.sleep(.75)
        del(enemyEncountered)
        time.sleep(1)
        player.manaBankAge = 0
        player.manaBank = 0
        player.guardHealth = 0
        player.activeEffects = []

        #Allow the player to prepare before moving on to the next encounter.
        input('\nYou ready yourself, then continue your journey.')
        os.system('cls')

print('L you lost')
if diedToYourOwnSpell:
  print('Aint no way you really died to your own spell, you might as well quit :(')