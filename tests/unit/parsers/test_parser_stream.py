import pytest
from unittest.mock import AsyncMock
from parsers.stream import EDIStreamParser


@pytest.mark.asyncio
async def test_edi_stream_buffer_logic():
    """Forces the parser to read in tiny 5-byte chunks to prove memory safety."""

    # A standard 3-segment EDI payload
    edi_data = (
        b"ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *260929*1000*U*00401*000000001*0*P*>~"
        b"ST*850*0001~"
        b"SE*2*0001~"
    )

    mock_file = AsyncMock()

    # Simulate an UploadFile: return the mandatory 106-byte ISA, then trickle the rest in 5-byte chunks
    mock_file.read.side_effect = [
        edi_data[:106],
        edi_data[106:111],
        edi_data[111:116],
        edi_data[116:121],
        edi_data[121:],
        b""
    ]

    parser = EDIStreamParser(mock_file)
    segments = []

    # Consume the stream
    async for segment in parser.stream_segments(chunk_size=5):
        segments.append(segment)

    # Verify the logic successfully glued the tiny chunks back together
    # and split correctly on the segment terminator.
    assert len(segments) == 3
    assert segments[0].startswith("ISA")
    assert segments[1] == "ST*850*0001"
    assert segments[2] == "SE*2*0001"