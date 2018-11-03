import random
import copy


noteNames = ['c', 'cis','d','dis','e','f','fis','g','gis','a','ais','b']
initialOctaveOffset = 2
durations = ['8','4','4.','2']
scale = [0,2,4,7,9] #pentatonicboiz

FAIL_ENDS = 'ends dont match'
FAIL_TRAN = 'wrong number of transposes'
FAIL_TRILL = 'has repeated notes'
FAIL_REP_SEGS = "has repeated segments"
FAIL_MOVE_OCT = "has octave moving notes too close"
FAIL_SEG_RANGE = "segment range is too big"
FAIL_WHOLE_RANGE = 'whole range is too big'
NEW_NOTE_BEGINING = 0
NEW_NOTE_END = 1
NEW_NOTE_MIDDLE = 2

REMOVE_NOTE_BEGINING = 3
REMOVE_NOTE_END = 4
REMOVE_MIDDLE = 5

OCTAVE_TRANSPOSE_WHOLE = 6
OCTAVE_OFFSET_SINGLE = 7
INTERVAL_TRANSPOSE_WHOLE = 8

SHRINK_NOTE = 9
EXPAND_NOTE = 10



def noteToMidiNote(note,transpose):
	twelveToneNoteValue = scale[(transpose + note['note'])%len(scale)]
	height = 72 + (12 * ((transpose + note['note']) / len(scale)))
	return twelveToneNoteValue+height

def noteToLilyNote(note,transpose):
	twelveToneNoteValue = scale[(transpose + note['note'])%len(scale)]
	noteName = noteNames[twelveToneNoteValue]
	height = (transpose + note['note']) / len(scale) # want math.floor
	numberOfUpsNeeded = height+initialOctaveOffset
	octaveChanger = ''
	if numberOfUpsNeeded > 0:
		octaveChanger = "'"*numberOfUpsNeeded
	else:
		octaveChanger = ","*numberOfUpsNeeded
	duration = durations[note['dur']]
	return noteName+octaveChanger+duration

def getHighest(segment):
	highest = -999999
	for n in segment['notes']:
		noteVal = n['note'] + segment['transpose']
		if noteVal>highest:
			highest = noteVal
	return highest


def getLowest(segment):
	lowest = 999999
	for n in segment['notes']:
		noteVal = n['note'] + segment['transpose']
		if noteVal<lowest:
			lowest = noteVal
	return lowest

def wholeRange(segments):
	lowest = 9999999
	highest = -99999999
	for s in segments:
		thisHighest = getHighest(s)
		thisLowest = getLowest(s)
		if thisHighest >  highest:
			highest = thisHighest
		if thisLowest < lowest:
			lowest = thisLowest
	return highest - lowest

def largestSegmentRange(segments):
	maxRange = 0
	for s in segments:
		highest = getHighest(s)
		lowest = getLowest(s)
		if highest - lowest > maxRange:
			maxRange = highest - lowest
	return maxRange

def hasRepeatedNotes(segments):
	for s in segments:
		for i in range(len(s['notes'])-4):
			if s['notes'][i]['note'] == s['notes'][i+2]['note'] and s['notes'][i]['note'] == s['notes'][i+4]['note']:
				return True
	return False

def hasOctaveMovingNotesTooClose(segments):
	for i in range(len(segments)-9):
		numbOctaveTrans = sum([segments[i+x]['option']==7 for x in range(4)])
		if numbOctaveTrans > 1:
			return True
	return False

def hasRepeatedSegments(segments):
	for i in range(len(segments)-2):
		if segments[i] == segments[i+1]:
			return True
	return False

def optionGivenList(probs):
	total = sum(probs)
	suedoIndex = random.random()*total
	sumSoFar = 0
	for i in range(len(probs)):
		sumSoFar += probs[i]
		if sumSoFar >= suedoIndex:
			return i

def downOrUp(a):
	ret = random.randint(-a,a-1)
	if ret >= 0:
		return ret+1
	return ret

def newNoteForSeg(segment,option):
	notes = segment['notes']
	newNoteData = {}
	if len(notes) == 1:
		newNoteData['index'] = 0
		newNoteData['note'] = 1
		return newNoteData
	if option == NEW_NOTE_BEGINING:
		newNoteData['index'] = 0
		newNoteData['note'] = notes[0]['note']+downOrUp(1)
	if option == NEW_NOTE_END:
		newNoteData['index'] = len(notes)
		newNoteData['note'] = notes[len(notes)-1]['note']+downOrUp(1)
	if option == NEW_NOTE_MIDDLE:
		i = random.randint(1,len(notes)-1)
		newNote = 0
		if notes[i-1]['note'] == notes[i]['note']:
			newNote = notes[i]['note']+downOrUp(1)
		elif notes[i-1]['note'] - notes[i]['note'] > 1:
			newNote = notes[i]['note']+1
		elif notes[i-1]['note'] - notes[i]['note'] < -1:
			newNote = notes[i-1]['note']+1
		elif random.random() > .5:
			newNote = max(notes[i-1]['note'],notes[i]['note'])+1
		else:
			newNote = min(notes[i-1]['note'],notes[i]['note'])-1
		newNoteData['index'] = i
		newNoteData['note'] = newNote
	return newNoteData

	#push away from middle, but if near edge, 50/50

def generateSegments(minimumLength):
	goodToGo = False
	segments = []
	failureReasons = {}
	minLength = minimumLength

	while not goodToGo:
		segments = []
		newSegment = {}
		newNote = {}
		newNote['note'] = 0
		newNote['dur'] = 1;
		newSegment['notes'] = [newNote]
		newSegment['option'] = -1
		newSegment['transpose'] = 0
		segments.append(newSegment)




		MUST_GROW = True
		MUST_SHRINK = False
		CAN_DUR_CHANGE = False

		CAN_OCTAVE_TRANSPOSE_WHOLE = False
		CAN_OCTAVE_OFFSET_SINGLE = False
		CAN_INTERVAL_TRANSPOSE_WHOLE = False

		NUMB_OCTAVE_TRANSPOSE_WHOLE = 0
		NUMB_OCTAVE_OFFSET_SINGLE = 0
		NUMB_INTERVAL_TRANSPOSE_WHOLE = 0

		LONGEST_BEFORE_SHRINK = 8
		SHORTEST_BEFORE_GROW = 3
		GO_BACK_UNTIL = 5

		probs = [1]*11
		probs[SHRINK_NOTE] = 3
		probs[EXPAND_NOTE] = 3
		probs[OCTAVE_TRANSPOSE_WHOLE] = 0


		keepGoing = True
		segmentNumber = 0
		while keepGoing:
			oldSeg = segments[len(segments)-1]
			newSeg = copy.deepcopy(oldSeg)

			if len(newSeg['notes']) > LONGEST_BEFORE_SHRINK:
				MUST_SHRINK = True
				MUST_GROW = False
			elif len(newSeg['notes']) < SHORTEST_BEFORE_GROW:
				MUST_SHRINK = False
				MUST_GROW = True
			elif len(newSeg['notes']) == GO_BACK_UNTIL:
				MUST_SHRINK = False
				MUST_GROW = False
			if len(newSeg['notes']) > 2 and len (newSeg['notes']) < LONGEST_BEFORE_SHRINK:
				CAN_DUR_CHANGE = True
			if segmentNumber < 20:
				CAN_OCTAVE_TRANSPOSE_WHOLE = False
				CAN_OCTAVE_OFFSET_SINGLE = False
				CAN_INTERVAL_TRANSPOSE_WHOLE = False
			else:
				CAN_OCTAVE_TRANSPOSE_WHOLE = True
				CAN_OCTAVE_OFFSET_SINGLE = True
				CAN_INTERVAL_TRANSPOSE_WHOLE = True
			if NUMB_OCTAVE_TRANSPOSE_WHOLE > 2:
				CAN_OCTAVE_TRANSPOSE_WHOLE = False
			if NUMB_INTERVAL_TRANSPOSE_WHOLE > 2 or OCTAVE_TRANSPOSE_WHOLE == 0:
				# wait till after we've done an octave transpose before we do
				# a single interval transpose
				CAN_INTERVAL_TRANSPOSE_WHOLE = False

			# deal with setting the correct probs given state
			if segmentNumber > minLength*.50 and segmentNumber < minLength*.80:
				probs[NEW_NOTE_BEGINING] = 5
				probs[NEW_NOTE_MIDDLE] = 5
				probs[NEW_NOTE_END] = 5
				LONGEST_BEFORE_SHRINK = 5+(int(segmentNumber/10))
				GO_BACK_UNTIL = (int(segmentNumber/10))
				if segmentNumber > minLength*.65:
					probs[SHRINK_NOTE] = 15
			elif segmentNumber >= minLength*.80:
				probs[NEW_NOTE_BEGINING] = 0
				probs[NEW_NOTE_MIDDLE] = 2
				probs[NEW_NOTE_END] = 0
				probs[REMOVE_NOTE_END] = 5
				probs[REMOVE_NOTE_BEGINING] = 5
				probs[REMOVE_MIDDLE] = 5
				probs[SHRINK_NOTE] = 1
				probs[EXPAND_NOTE] = 5

				SHORTEST_BEFORE_GROW = 3
				GO_BACK_UNTIL = 4
			if segmentNumber > minLength:
				SHORTEST_BEFORE_GROW = 0

			theseProbs = copy.deepcopy(probs)
			if MUST_GROW:
				theseProbs = [0] * len(theseProbs)
				theseProbs[NEW_NOTE_BEGINING] = 1
				theseProbs[NEW_NOTE_END] = 1
				theseProbs[NEW_NOTE_MIDDLE] = 1
			if MUST_SHRINK:
				theseProbs = [0] * len(theseProbs)
				theseProbs[REMOVE_NOTE_END] = 1
				theseProbs[REMOVE_NOTE_BEGINING] = 1
				theseProbs[REMOVE_MIDDLE] = 1
			if not CAN_OCTAVE_TRANSPOSE_WHOLE:
				theseProbs[OCTAVE_TRANSPOSE_WHOLE] = 0
			if not CAN_OCTAVE_OFFSET_SINGLE:
				theseProbs[OCTAVE_OFFSET_SINGLE] = 0
			if not CAN_INTERVAL_TRANSPOSE_WHOLE:
				theseProbs[INTERVAL_TRANSPOSE_WHOLE] = 0

			option = optionGivenList(theseProbs)
			newSeg['option'] = option

			if option == NEW_NOTE_BEGINING or option == NEW_NOTE_END or option == NEW_NOTE_MIDDLE: # ADD A NEW NOTE BABY!
				newNoteData = newNoteForSeg(oldSeg,option)
				newNote = {}
				newNote['note'] = newNoteData['note']
				newNote['dur'] = 1;
				newSeg['notes'].insert(newNoteData['index'],newNote)
			if option == REMOVE_NOTE_BEGINING:
				del newSeg['notes'][0]
			if option == REMOVE_NOTE_END:
				del newSeg['notes'][len(newSeg['notes'])-1]
			if option == REMOVE_MIDDLE:
				goodRemove = False
				while not goodRemove:
					deleteIndex = random.randint(0,len(newSeg['notes'])-1)
					if deleteIndex == 0 or deleteIndex == len(newSeg['notes'])-1:
						goodRemove = True
					else:
						if newSeg['notes'][deleteIndex-1] == newSeg['notes'][deleteIndex+1]:
							goodRemove = False
				del newSeg['notes'][deleteIndex]
			if option == SHRINK_NOTE:
				shrinkOptions = []
				for i in range(len(newSeg['notes'])):
					# bc dirs are 0,1,2 (representing 16,8,8.)
					# we can use this number directly as the probabiliy
					# such that 16ths will not be used, and 8.s are more likely
					if i==len(newSeg['notes'])-1:
						shrinkOptions.insert(i,0)
					else:
						shrinkOptions.insert(i,newSeg['notes'][i]['dur'])
				shrinkIndex = optionGivenList(shrinkOptions)
				newSeg['notes'][shrinkIndex]['dur'] = 0
			if option == EXPAND_NOTE:
				growOptions = []
				for i in range(len(newSeg['notes'])):
					if i==0 or i==len(newSeg['notes'])-1:
						growOptions.insert(i,0)
					growOptions.insert(i,2-newSeg['notes'][i]['dur'])
				growIndex = optionGivenList(growOptions)
				newSeg['notes'][growIndex]['dur'] = 2
			if option == OCTAVE_TRANSPOSE_WHOLE:
				newSeg['transpose'] = downOrUp(2)*len(scale)
				NUMB_OCTAVE_TRANSPOSE_WHOLE += 1
			if option == OCTAVE_OFFSET_SINGLE:
				newSeg['notes'][random.randint(0,len(newSeg['notes'])-1)]['note']+=len(scale)*downOrUp(1)
				NUMB_OCTAVE_OFFSET_SINGLE+=1
			if option == INTERVAL_TRANSPOSE_WHOLE:
				newSeg['transpose'] = downOrUp(len(scale)-1)
				NUMB_INTERVAL_TRANSPOSE_WHOLE+=1

			if segmentNumber > minLength-10:
				newSeg['transpose'] = 0

			segments.append(newSeg)
			segmentNumber +=1
			if len(newSeg['notes']) == 1 and segmentNumber > minLength:
				keepGoing = False
		goodToGo=True
		thisFail = []
		if segments[0]['notes'][0]!=segments[len(segments)-1]['notes'][0]:
			thisFail.append(FAIL_ENDS)
			goodToGo = False
		if NUMB_INTERVAL_TRANSPOSE_WHOLE < minLength* 0.02 or NUMB_OCTAVE_OFFSET_SINGLE <minLength* 0.03:
			thisFail.append(FAIL_TRAN)
			goodToGo = False
		if hasRepeatedNotes(segments):
			thisFail.append(FAIL_TRILL)
			goodToGo = False
		if hasRepeatedSegments(segments):
			thisFail.append(FAIL_REP_SEGS)
			goodToGo = False
		if hasOctaveMovingNotesTooClose(segments):
			thisFail.append(FAIL_MOVE_OCT)
			goodToGo = False
		if largestSegmentRange(segments) > len(scale)*2.5:
			thisFail.append(FAIL_SEG_RANGE)
			goodToGo = False
		if wholeRange(segments) > len(scale)*3.5:
			thisFail.append(FAIL_WHOLE_RANGE)
			goodToGo = False
		for fr in thisFail:
			if fr in failureReasons:
				failureReasons[fr] += 1
			else:
				failureReasons[fr] = 1
		if .98 < random.random():
			print "****"
			for f in failureReasons:
				print f, failureReasons[f]
	return segments
