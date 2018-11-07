from random import randint
import random
import sys

_totalInsturments = 0
_totalLength = 0

def alwaysSomeonePlaying(parts):
	totalLength = len(parts[0])
	totalInsturments = len(parts)
	for i in range(totalLength):
		someoneIsPlaying = False
		for p in range(totalInsturments):
			if parts[p][i] == 1:
				someoneIsPlaying = True
		if someoneIsPlaying == False:
			return False
	return True

def printParts(parts):
	totalLength = len(parts[0])
	totalInsturments = len(parts)
	for i in range(totalLength):
		partToPrint = str(i)+":"
		amountShort = 5-len(partToPrint)
		partToPrint = partToPrint+ " "*amountShort
		sys.stdout.write(partToPrint)
		for p in range(totalInsturments):
			partToPrint = str(parts[p][i])
			amountShort = 4-len(partToPrint)
			partToPrint = partToPrint+ " "*amountShort
			sys.stdout.write(partToPrint+' ')
			sys.stdout.flush()
		sys.stdout.write('\n')
		sys.stdout.flush()


def getAssignments(totalInsturments,totalLength,soloist):
	failureReasons = {}
	_totalInsturments = totalInsturments
	_totalLength = totalLength

	generalStart = 5
	generalEnd = totalLength-5
	longestLength = 20
	shortestLength = 6
	manditorySilenceLength = 3
	shortestOverlap = 3

	goodToGo = False
	while not goodToGo:
		parts = []
		for i in range(totalInsturments):
			parts.append([])
			for h in range(totalLength):
				parts[i].append(0)

		# add soloist starting and ending
		for i in range(randint(int(totalLength/10),int(totalLength/5))):
			parts[soloist][i] = 1
		for i in range(randint(int(totalLength/10),int(totalLength/5))):
			parts[soloist][totalLength-i-1] = 1

		#add everyone generally
		# do it about ~six~ XXX 6*1.3 times for 100 and 20,5.
		for m in range(int( 1.3* (generalEnd-generalStart) / (longestLength-shortestLength))):
			for p in range(totalInsturments):
				startPoint = randint(generalStart,generalEnd-shortestLength)
				length = randint(shortestLength,longestLength)
				if length + startPoint > generalEnd:
					continue
				for i in range(length):
					parts[p][startPoint+i] = 1
				for i in range(3):
					parts[p][startPoint+length+i] = 0

			# make sure there is always someone playing
			thisFail = []
			goodToGo = alwaysSomeonePlaying(parts)
			if not goodToGo:
				thisFail.append('some spots dont have playing')
			# figure out where we have full tuti
			tutiMap = []
			for i in range(totalLength):
				someoneIsNotPlaying = False
				for p in range(totalInsturments):
					if parts[p][i] == 0:
						someoneIsNotPlaying = True
				if someoneIsNotPlaying:
					tutiMap.append(0)
				else:
					tutiMap.append(1)
			# too much tuti
			if sum(tutiMap) > totalLength*.3:
				goodToGo = False
				thisFail.append('too much tuti')
			# too little tuti
			if sum(tutiMap) < totalLength*.1:
				goodToGo = False
				thisFail.append('to little tuti')
			# tuti all in one group
			tutiGroups = 0
			isInTuti = False
			for i in range(len(tutiMap)):
				if tutiMap[i] == 0:
					if isInTuti:
						tutiGroups += 1
						isInTuti = False
				if tutiMap[i] == 1:
					isInTuti = True
			if tutiGroups < 2:
				thisFail.append('all tuti is in one group')
				goodToGo = False
				continue

			#intensity mapping (how many people are playing when)
			intensityMap = []
			for i in range(totalLength):
				peoplePlaying = 0
				for p in range(totalInsturments):
					peoplePlaying+=parts[p][i]
				intensityMap.append(peoplePlaying)
			# print intensityMap

			# make sure everyone plays before we have a big tuti

			peopleWhoHavePlayed = [0]*totalInsturments
			for i in range(totalLength):
				if intensityMap[i] >= totalInsturments-1 and sum(peopleWhoHavePlayed) != totalInsturments:
						if totalInsturments < 7:
							thisFail.append('tuti before everyone played before')
							goodToGo = False
				for p in range(totalInsturments):
					if parts[p][i] == 1:
						peopleWhoHavePlayed[p] = 1
			
			#make sure no one plays solo for more than a short bit
			soloInfo = [0]
			for i in range(totalLength):
				if intensityMap[i] == 1:
					soloInfo[len(soloInfo)-1] += 1
				if intensityMap[i] != 1:
					if soloInfo[len(soloInfo)-1] != 0:
						soloInfo.append(0)
			if len(soloInfo) > max(12-totalInsturments, 3):
				goodToGo = False
				thisFail.append('more than six solos')
			if sum(soloInfo) > totalLength * .3:
				thisFail.append('solos are more than a third')
				goodToGo = False

			# make sure no one is playing a bit for less than .5 of shortest playing:
			for p in range(totalInsturments):
				partInfo = [0]
				for i in range(totalLength):
					if parts[p][i] == 1:
						partInfo[len(partInfo)-1] += 1
					else:
						if partInfo[len(partInfo)-1] != 0:
							partInfo.append(0) 
				if partInfo[len(partInfo)-1] == 0:
					partInfo.remove(0)  
				# print partInfo
				if max(partInfo) > totalLength*.35:
					goodToGo = False
					thisFail.append('someone plays for more than .35 of the piece straight')
				if min(partInfo) < shortestLength:
					goodToGo = False
					thisFail.append('people play for less than shortest length')

			#make sure there are no places where we have very little overlap
			overlapVersionParts = []
			for p in range(totalInsturments):
				overlapVersionParts.append([])
				for i in range(totalLength):
					overlapVersionParts[p].append(parts[p][i])
				for i in range(totalLength-shortestOverlap):
					if overlapVersionParts[p][i+shortestOverlap] == 0:
						for z in range(shortestOverlap):
							overlapVersionParts[p][i+z] = 0
			# printParts(overlapVersionParts)
			if not alwaysSomeonePlaying(overlapVersionParts):
				goodToGo = False
				thisFail.append('shit dont overlap well')

			for fr in thisFail:
				if fr in failureReasons:
					failureReasons[fr] += 1
				else:
					failureReasons[fr] = 1
			if .996 < random.random():
				print "****"
				for f in failureReasons:
					print f, failureReasons[f]

			if goodToGo:
				return parts
	return parts
