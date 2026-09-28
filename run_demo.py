import json
from edi_parser import parse_x12_to_dict

sample_850 = """
ST*997*0001~AK1*PO*11~AK9*X*3*3*0~SE*4*0001~
"""

if __name__ == "__main__":
    result = parse_x12_to_dict(sample_850)
    print(json.dumps(result, indent=2))