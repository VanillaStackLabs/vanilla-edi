import pytest
from unittest.mock import AsyncMock
from parsers.stream import EDIStreamParser
from routers.parse import process_edi_stream
from fastapi import UploadFile
from io import BytesIO


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


@pytest.mark.asyncio
async def test_edi_stream_parser_error_branch():
    # Simulates stream encountering invalid segment processing or missing separators
    fake_file = UploadFile(filename="bad.edi", file=BytesIO(b"ST*850*0001~\nINVALID_SEGMENT_WITHOUT_SEP"))

    results = []
    async for line in process_edi_stream(fake_file):
        results.append(line)

    # Verify that the Exception handler was triggered and yielded an error JSON string
    assert any("error" in res for res in results)


@pytest.mark.asyncio
async def test_edi_stream_empty_file_branch():
    # Simulates an completely empty file upload
    mock_file = AsyncMock()
    mock_file.read.return_value = b""

    parser = EDIStreamParser(mock_file)
    results = [s async for s in parser.stream_segments()]

    assert results == []


@pytest.mark.asyncio
async def test_edi_stream_unterminated_buffer_branch():
    # Simulates a file that ends abruptly without a trailing segment terminator
    mock_file = AsyncMock()
    mock_file.read.side_effect = [
        b"ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *260929*1000*U*00401*000000001*0*P*>~",
        b"ST*850*0001~UNFINISHED_SEGMENT",
        b""
    ]

    parser = EDIStreamParser(mock_file)
    results = [s async for s in parser.stream_segments()]

    # Proves the final flush buffer branch yielded the leftover string
    assert results[-1] == "UNFINISHED_SEGMENT"

@pytest.mark.asyncio
async def test_edi_stream_empty_segment_branch():
    # Simulates double segment terminators ("~~") resulting in empty strings between splits
    mock_file = AsyncMock()
    mock_file.read.side_effect = [
        b"ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *260929*1000*U*00401*000000001*0*P*>~",
        b"ST*850*0001~~SE*2*0001~",
        b""
    ]

    parser = EDIStreamParser(mock_file)
    results = [s async for s in parser.stream_segments()]

    # Ensures clean segments were yielded while empty intermediate segments were skipped
    assert len(results) == 3
    assert results[1] == "ST*850*0001"
    assert results[2] == "SE*2*0001"