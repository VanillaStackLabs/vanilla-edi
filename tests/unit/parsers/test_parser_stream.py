import pytest
from unittest.mock import AsyncMock
from parsers.stream import EDIStreamParser


@pytest.mark.asyncio
async def test_edi_stream_buffer_logic():
    edi_data = (
        b"ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *260929*1000*U*00401*000000001*0*P*>~"
        b"ST*850*0001~"
        b"SE*2*0001~"
    )

    # Dynamic mock reader that honors whatever chunk size the parser requests
    cursor = 0
    async def mock_read(size=-1):
        nonlocal cursor
        if cursor >= len(edi_data):
            return b""
        # If size isn't specified or is negative, read all
        read_size = len(edi_data) if size is None or size < 0 else size
        chunk = edi_data[cursor : cursor + read_size]
        cursor += read_size
        return chunk

    mock_file = AsyncMock()
    mock_file.read.side_effect = mock_read

    parser = EDIStreamParser(mock_file)
    segments = [s async for s in parser.stream_segments(chunk_size=5)]

    assert len(segments) == 3
    assert segments[0].startswith("ISA")
    assert segments[1] == "ST*850*0001"
    assert segments[2] == "SE*2*0001"