import sys
import keys

mod = 2L ** 32

def decryptString(strIn, key=keys.key_in):
	dec = strIn.decode( "hex" )
	ret = []

#	print "Decoded:"
#	for s in dec:
#		sys.stdout.write( "%02x" %ord(s) )
#	sys.stdout.flush()
#	print

	for i in range( 0, len( dec ), 8 ):
		l =	ord(dec[ i + 0 ]) << 24 | \
			ord(dec[ i + 1 ]) << 16 | \
			ord(dec[ i + 2 ]) << 8  | \
			ord(dec[ i + 3 ])
		
		r =	ord(dec[ i + 4 ]) << 24 | \
			ord(dec[ i + 5 ]) << 16 | \
			ord(dec[ i + 6 ]) << 8  | \
			ord(dec[ i + 7 ])

		for j in range( key["n"] + 1, 1, -1 ):
			l = l ^ key["p"][j]

			a = ( l & 0xFF000000 ) >> 24
			b = ( l & 0x00FF0000 ) >> 16
			c = ( l & 0x0000FF00 ) >> 8
			d = ( l & 0x000000FF )
	
			f = (long(key["s"][0][a]) + long(key["s"][1][b])) % mod
			f = f ^ long(key["s"][2][c])
			f = f + long(key["s"][3][d])
			f = (f % mod) & 0xFFFFFFFF
	
			r ^= f
	
			l, r = r, l
	
		l, r = r, l
	
		r ^= key["p"][1]
		l ^= key["p"][0]

		ret.append(chr(( l >> 24 ) & 0xff ))
		ret.append(chr(( l >> 16 ) & 0xff ))
		ret.append(chr(( l >> 8 ) & 0xff ))
		ret.append(chr(l & 0xff ) )

		ret.append(chr(( r >> 24 ) & 0xff ))
		ret.append(chr(( r >> 16 ) & 0xff ))
		ret.append(chr(( r >> 8 ) & 0xff ))
		ret.append(chr(r & 0xff ))

	return "".join(ret)

def encryptString(inStr, key=keys.key_out):
	blocks = (len(inStr) / 8) + 1

	#Pad with \0  
	padStr = inStr + "\0\0\0\0\0\0\0\0"

	ret = []

	for h in range( 0, blocks ):
		i = h << 3 #h * 8

#		print len( padStr ), i, i+7

		l =	ord( padStr[ i + 0 ] ) << 24 | \
			ord( padStr[ i + 1 ] ) << 16 | \
			ord( padStr[ i + 2 ] ) << 8  | \
			ord( padStr[ i + 3 ] )

		r =	ord( padStr[ i + 4 ] ) << 24 | \
			ord( padStr[ i + 5 ] ) << 16 | \
			ord( padStr[ i + 6 ] ) << 8  | \
			ord( padStr[ i + 7 ] )

		for j in range( 0, key["n"] ):
			l ^= key["p"][j]

			a = ( l & 0xFF000000 ) >> 24
			b = ( l & 0x00FF0000 ) >> 16
			c = ( l & 0x0000FF00 ) >> 8
			d = ( l & 0x000000FF )

			f = ( long( key["s"][0][a] ) + \
				  long( key["s"][1][b] ) ) % mod
			f = f ^ long( key["s"][2][c] )
			f = f + long( key["s"][3][d] )
			f = ( f % mod ) & 0xFFFFFFFF

			r ^= f

			l, r = r, l

		l, r = r, l

		r ^= key["p"][ key["n"] ]
		l ^= key["p"][ key["n"] + 1 ]

		ret.append( chr( ( l >> 24 ) & 0xff ) )
		ret.append( chr( ( l >> 16 ) & 0xff ) )
		ret.append( chr( ( l >> 8 ) & 0xff ) )
		ret.append( chr( l & 0xff ) )

		ret.append( chr( ( r >> 24 ) & 0xff ) )
		ret.append( chr( ( r >> 16 ) & 0xff ) )
		ret.append( chr( ( r >> 8 ) & 0xff ) )
		ret.append( chr( r & 0xff ) )

	return "".join( ret ).encode( "hex" )



if __name__ == "__main__":
	print "In:",
	strIn = raw_input()

	print encryptString(strIn)
