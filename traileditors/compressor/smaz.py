import io

__all__ = [
    'decompress',
    'compress',
]

DECODE = [b" ", b"the", b"e", b"t", b"a", b"of", b"o", b"and", b"i", b"n", b"s", b"e ", b"r", b" th",
          b" t", b"in", b"he", b"th", b"h", b"he ", b"to", b"\r\n", b"l", b"s ", b"d", b" a", b"an",
          b"er", b"c", b" o", b"d ", b"on", b" of", b"re", b"of ", b"t ", b", b", b"is", b"u", b"at",
          b"   ", b"n ", b"or", b"which", b"f", b"m", b"as", b"it", b"that", b"\n", b"was", b"en",
          b"  ", b" w", b"es", b" an", b" i", b"\r", b"f ", b"g", b"p", b"nd", b" s", b"nd ", b"ed ",
          b"w", b"ed", b"http://", b"for", b"te", b"ing", b"y ", b"The", b" c", b"ti", b"r ", b"his",
          b"st", b" in", b"ar", b"nt", b",", b" to", b"y", b"ng", b" h", b"with", b"le", b"al", b"to ",
          b"b", b"ou", b"be", b"were", b" b", b"se", b"o ", b"ent", b"ha", b"ng ", b"their", b"\"",
          b"hi", b"from", b" f", b"in ", b"de", b"ion", b"me", b"v", b".", b"ve", b"all", b"re ",
          b"ri", b"ro", b"is ", b"co", b"f t", b"are", b"ea", b". ", b"her", b" m", b"er ", b" p",
          b"es ", b"by", b"they", b"di", b"ra", b"ic", b"not", b"s, b", b"d t", b"at ", b"ce", b"la",
          b"h ", b"ne", b"as ", b"tio", b"on ", b"n t", b"io", b"we", b" a ", b"om", b", a", b"s o",
          b"ur", b"li", b"ll", b"ch", b"had", b"this", b"e t", b"g ", b"e\r\n", b" wh", b"ere",
          b" co", b"e o", b"a ", b"us", b" d", b"ss", b"\n\r\n", b"\r\n\r", b"=\"", b" be", b" e",
          b"s a", b"ma", b"one", b"t t", b"or ", b"but", b"el", b"so", b"l ", b"e s", b"s,", b"no",
          b"ter", b" wa", b"iv", b"ho", b"e a", b" r", b"hat", b"s t", b"ns", b"ch ", b"wh", b"tr",
          b"ut", b"/", b"have", b"ly ", b"ta", b" ha", b" on", b"tha", b"-", b" l", b"ati", b"en ",
          b"pe", b" re", b"there", b"ass", b"si", b" fo", b"wa", b"ec", b"our", b"who", b"its", b"z",
          b"fo", b"rs", b">", b"ot", b"un", b"<", b"im", b"th ", b"nc", b"ate", b"><", b"ver", b"ad",
          b" we", b"ly", b"ee", b" n", b"id", b" cl", b"ac", b"il", b"</", b"rt", b" wi", b"div",
          b"e, b", b" it", b"whi", b" ma", b"ge", b"x", b"e c", b"men", b".com"]

LEN_DECODE = sorted(enumerate(DECODE), key=lambda x: len(x[1]), reverse=True)


def decompress(stream: io.IOBase):
    output = b""
    i = 0

    while nextbyte := stream.read(1):
        # Single byte
        if nextbyte[0] == 0xfe:
            output += stream.read(1)
            continue

        # Multiple bytes
        if nextbyte[0] == 0xff:
            length = stream.read(1)
            output += stream.read(length[0])
            continue

        # Dictionary word
        output += DECODE[nextbyte[0]]

    return output


def _compress_raw(data):
    return bytes([0xff, len(data)]) + data


def compress(data):
    chunks = []
    buf = b""

    while len(data) > 0:
        if len(buf) >= 255:
            chunks += [_compress_raw(buf)]
            buf = b""

        try:
            e = next(filter(lambda x: data.startswith(x[1]), LEN_DECODE))

            if len(buf) > 0:
                chunks += [_compress_raw(buf)]
                buf = b""

            chunks += [bytes([e[0]])]
            data = data[len(e[1]):]
        except StopIteration:
            buf += bytes([data[0]])
            data = data[1:]

    if len(buf) > 0:
        chunks += [_compress_raw(buf)]

    # Replace one-byte multibyte sequences
    chunks = [(b"\xfe" + ch[2:] if ch.startswith(b"\xff\x01") else ch) for ch in chunks]

    return b"".join(chunks)
