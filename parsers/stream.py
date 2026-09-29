from typing import AsyncGenerator
from fastapi import UploadFile


class EDIStreamParser:
    def __init__(self, upload_file: UploadFile):
        self.file = upload_file
        self.element_sep = "*"
        self.segment_term = "~"

    async def stream_segments(self, chunk_size: int = 4096) -> AsyncGenerator[str, None]:
        # Read the strict 106-character ISA segment first
        isa_chunk = await self.file.read(106)
        if not isa_chunk:
            return

        isa_text = isa_chunk.decode("utf-8", errors="ignore")

        if not isa_text.startswith("ISA") or len(isa_text) < 106:
            raise ValueError("Invalid EDI stream: Missing or malformed ISA segment.")

        self.element_sep = isa_text[3]
        self.segment_term = isa_text[105]

        # Yield the ISA segment immediately
        yield isa_text.strip('\r\n')

        buffer = ""
        # Read the rest of the massive file in tiny memory-safe chunks
        while chunk := await self.file.read(chunk_size):
            buffer += chunk.decode("utf-8", errors="ignore")

            # Yield segments as soon as a terminator is found
            while self.segment_term in buffer:
                segment, buffer = buffer.split(self.segment_term, 1)
                clean_segment = segment.strip('\r\n')
                if clean_segment:
                    yield clean_segment

        # Flush buffer
        if buffer.strip('\r\n'):
            yield buffer.strip('\r\n')