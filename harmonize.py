import compose
import random

def idealToMidi(noteNumber):
	pitch = noteNumber%len(compose.scale)
	octave = noteNumber/len(compose.scale)
	return 72+octave*12+compose.scale[pitch]

def getMidiRange(segments,harmonyTranspose):
	lowest = 999999
	highest = -999999
	segmentToCheck = []
	for segment in segments:
		for n in segment['notes']:
			noteVal = n['note'] + segment['transpose']+harmonyTranspose
			if noteVal<lowest:
				lowest = noteVal
			if noteVal>highest:
				highest = noteVal
	return [idealToMidi(lowest),idealToMidi(highest)]

def isValidRange(insturment,segRange):
	if insturment[0] <= segRange[0] and insturment[1]>= segRange[1]:
		return True
	return False

def getPosssibleRanges(insturment,segRange):
	possibleRanges=[]
	for i in range(-12,12):
		thisSegRange = [segRange[0]+i*12, segRange[1]+i*12]
		if isValidRange(insturment,thisSegRange):
			possibleRanges.append(i)
	return possibleRanges

def getMiddleRange(insturment,segRange):
	possibleRanges = getPosssibleRanges(insturment,segRange)
	return possibleRanges[int((len(possibleRanges)-1)/2)]

def getCloseToActualRange(insturment,segRange):
	possibleRanges = getPosssibleRanges(insturment,segRange)
	if 0 in possibleRanges:
		return 0
	if max(possibleRanges) < 0:
		return max(possibleRanges)
	return  min(possibleRanges)

def getLowestRange(insturment,segRange):
	possibleRanges = getPosssibleRanges(insturment,segRange)
	return possibleRanges[0]

def getHighestRange(insturment,segRange):
	possibleRanges = getPosssibleRanges(insturment,segRange)
	return possibleRanges[len(possibleRanges)-1]

def newHarmony(otherHarmonies,segNumb):
	goodToGo = False
	while goodToGo == False:
		newHarmony = random.choice(range(len(compose.scale)))
		if newHarmony not in otherHarmonies:
			goodToGo = True
	return newHarmony

def extractPlayingSegment(segments,assignments,segNumb,insturment):
	retSegment = []
	adding=True
	for i in range(segNumb,len(segments)):
		if assignments[insturment][i] == 1:
			retSegment.append(segments[i])
	return retSegment

def genHarmonies(ranges, segments, assignments, key):
	transposition = []
	for i in range(len(ranges)):
		transposition.append([])
		for j in range(len(segments)):
			transposition[i].append(None)
	for segNumb in range(len(segments)):
		for insturment in range(len(ranges)):
			if assignments[insturment][segNumb] == 0:
				continue
			else:
				newTrans = None
				if segNumb == 0:
					playingSegments = extractPlayingSegment(segments,assignments,segNumb,insturment)
					midiRange = getMidiRange(playingSegments,0)
					newTrans = getCloseToActualRange(ranges[insturment],midiRange)*len(compose.scale)
				else:
					if assignments[insturment][segNumb-1] == 0:
						# first figure out what harmonies we want to play.
						harmonicTranspose = 0
						# first figure out what the other harmonies are
						otherHarmonies = []
						for i in range(len(ranges)):
							if transposition[i][segNumb] != None:
								otherHarmonies.append(transposition[i][segNumb]%len(compose.scale))
						otherHarmonies = list(set(otherHarmonies))
						if False:
							harmonicTranspose = 0
						else:
							harmonicTranspose = newHarmony(otherHarmonies,segNumb)
						#then figure out what range is best/most true
						# just random choose high or low
						playingSegments = extractPlayingSegment(segments,assignments,segNumb,insturment)
						midiRange = getMidiRange(playingSegments,harmonicTranspose)
						newTrans = getCloseToActualRange(ranges[insturment], midiRange)*len(compose.scale)+harmonicTranspose
						#set all the things here
						# we need to set this earlier
						if segNumb > 85 and insturment == 1:
							print 'HERE????'
							newTrans = 0
				if newTrans != None:
					transposition[insturment][segNumb] = newTrans
					# apply it to everything in the future that is similar to this one
					oldSegNumb = segNumb
					while segNumb+1<len(assignments[insturment]) and (assignments[insturment][segNumb+1] == 1):
						transposition[insturment][segNumb+1] = newTrans
						segNumb = segNumb+1
					segNumb = oldSegNumb
	return transposition