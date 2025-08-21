#!/usr/bin/env python3
"""
Add all 40 Dream11 teams using the edit team API
"""

from dream11_api_client import edit_dream11_team
import time

# Configuration
MATCH_ID = "108984"
AUTH_TOKEN = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IlRqb0FsLVdyZWN3Z3MtZVVvcm5xWWE5Y2x4dyJ9.eyJhdWQiOlsiYXBpLmRyZWFtMTEuY29tIiwiZ3VhcmRpYW4iXSwiZXhwIjoxNzcxMzE5OTg3LCJpYXQiOjE3NTU3Njc5ODcsImlzcyI6ImRyZWFtMTEuY29tIiwic3ViIjoiNDY4MTYxIiwiYXpwIjoiMiIsInJmdCI6IjEifQ.KvlKZ8fzvkikfKmzW02iaqDRUkcmdyaCFy33SnFBJBfqQBrU0uZjmK6hSYQ1yhJMceIuKpbP51yU_KFC-DB2Ftkrhpt3DeTq-06G-JRoTFAGphCFyQe7UseMs5V_RHRCAuyPP1etLlYPJEFp5jxbutwAI_-ayrSUq8B31buVl9d5L1dcK1cmorY5-10D6kTjmSVS_eKc79WExcdo1MMScJP60V82TypdVUbrtjfnx-9U6HbH6f1OcGam8zIk4lHEZgRLg_HDiJgHKlNXZedBSdkYgoxpvFV8dH8o8Xq6CKeRzotrzJGbn2lZ8EZVfw_noSN-hh8Z9ISlA7GG7sm3Ow"
# Teams data
teams_data = [
    {
      "id": 1,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 12712,
      "players": [
        46614,
        10853,
        10686,
        10920,
        10855,
        11381,
        46558,
        11395,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 2,
      "name": "4-7",
      "captain": 11395,
      "vice_captain": 46558,
      "players": [
        10686,
        46614,
        10920,
        11395,
        11381,
        46558,
        10855,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 3,
      "name": "4-7",
      "captain": 46558,
      "vice_captain": 10855,
      "players": [
        10686,
        46614,
        10920,
        46558,
        11381,
        10855,
        11395,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 4,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 46558,
      "players": [
        10853,
        46614,
        10920,
        46558,
        11381,
        10855,
        11395,
        48465,
        12712,
        11396,
        11306
      ]
    },
    {
      "id": 5,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 48465,
      "players": [
        46614,
        10853,
        10920,
        11395,
        11381,
        11396,
        46558,
        12712,
        48465,
        10855,
        11306
      ]
    },
    {
      "id": 6,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 11395,
      "players": [
        46614,
        10853,
        10686,
        10920,
        11395,
        17489,
        10855,
        46558,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 7,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 17489,
      "players": [
        10686,
        10853,
        46614,
        10920,
        11395,
        17489,
        10855,
        46558,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 8,
      "name": "4-7",
      "captain": 46558,
      "vice_captain": 48465,
      "players": [
        10686,
        46614,
        10920,
        46558,
        17489,
        11395,
        11396,
        48465,
        12712,
        10855,
        11306
      ]
    },
    {
      "id": 9,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 11395,
      "players": [
        46614,
        10686,
        10920,
        10855,
        17489,
        11395,
        46558,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 10,
      "name": "4-7",
      "captain": 11381,
      "vice_captain": 12712,
      "players": [
        46614,
        10686,
        10920,
        10855,
        11381,
        46558,
        11395,
        12712,
        48465,
        11396,
        97321
      ]
    },
    {
      "id": 11,
      "name": "4-7",
      "captain": 11381,
      "vice_captain": 48465,
      "players": [
        46614,
        10686,
        12696,
        10920,
        10855,
        11381,
        11395,
        46558,
        48465,
        12712,
        11396
      ]
    },
    {
      "id": 12,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 48465,
      "players": [
        46614,
        10686,
        12696,
        10920,
        10855,
        11381,
        11395,
        46558,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 13,
      "name": "4-7",
      "captain": 11395,
      "vice_captain": 11396,
      "players": [
        46614,
        10686,
        12696,
        10920,
        11395,
        11381,
        11396,
        46558,
        12712,
        48465,
        10855
      ]
    },
    {
      "id": 14,
      "name": "4-7",
      "captain": 46558,
      "vice_captain": 11396,
      "players": [
        46614,
        10686,
        10920,
        12696,
        46558,
        11381,
        11396,
        11395,
        48465,
        12712,
        10855
      ]
    },
    {
      "id": 15,
      "name": "4-7",
      "captain": 11381,
      "vice_captain": 12712,
      "players": [
        10686,
        46614,
        12696,
        10920,
        11395,
        11381,
        11396,
        46558,
        12712,
        48465,
        10855
      ]
    },
    {
      "id": 16,
      "name": "4-7",
      "captain": 46558,
      "vice_captain": 11395,
      "players": [
        46614,
        10686,
        12696,
        46558,
        11381,
        11395,
        11396,
        12712,
        48465,
        10855,
        10920
      ]
    },
    {
      "id": 17,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 12712,
      "players": [
        10686,
        46614,
        12696,
        10855,
        11381,
        46558,
        11395,
        12712,
        48465,
        11396,
        10920
      ]
    },
    {
      "id": 18,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 48465,
      "players": [
        10686,
        46614,
        10920,
        12696,
        11395,
        11381,
        10855,
        46558,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 19,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 48465,
      "players": [
        46614,
        10686,
        10920,
        12696,
        11395,
        11381,
        46558,
        10855,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 20,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 48465,
      "players": [
        46614,
        10853,
        10920,
        10855,
        11381,
        11395,
        46558,
        48465,
        12712,
        11396,
        97321
      ]
    },
    {
      "id": 21,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 46558,
      "players": [
        10686,
        46614,
        10920,
        46558,
        11381,
        10855,
        11395,
        12712,
        48465,
        11396,
        68521
      ]
    },
    {
      "id": 22,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 11395,
      "players": [
        10686,
        10853,
        12696,
        10855,
        11381,
        11395,
        46558,
        12712,
        48465,
        11396,
        10920
      ]
    },
    {
      "id": 23,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 11395,
      "players": [
        10853,
        10686,
        12696,
        10920,
        10855,
        11381,
        11395,
        46558,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 24,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 11395,
      "players": [
        10853,
        10686,
        12696,
        10920,
        11395,
        11381,
        46558,
        10855,
        48465,
        12712,
        11396
      ]
    },
    {
      "id": 25,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 46558,
      "players": [
        10686,
        10853,
        12696,
        10920,
        46558,
        11381,
        11395,
        10855,
        48465,
        12712,
        11396
      ]
    },
    {
      "id": 26,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 11395,
      "players": [
        10853,
        46614,
        10920,
        12696,
        10855,
        11381,
        11395,
        46558,
        48465,
        12712,
        11396
      ]
    },
    {
      "id": 27,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 11395,
      "players": [
        10853,
        10920,
        46614,
        12696,
        10855,
        11381,
        11395,
        46558,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 28,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 12712,
      "players": [
        10853,
        46614,
        10920,
        12696,
        46558,
        11381,
        11395,
        11396,
        48465,
        12712,
        10855
      ]
    },
    {
      "id": 29,
      "name": "4-7",
      "captain": 46558,
      "vice_captain": 11395,
      "players": [
        46614,
        10853,
        10920,
        12696,
        46558,
        11381,
        11395,
        11396,
        48465,
        12712,
        10855
      ]
    },
    {
      "id": 30,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 11381,
      "players": [
        10686,
        10920,
        12696,
        46558,
        11381,
        11396,
        11395,
        12712,
        48465,
        10855,
        11306
      ]
    },
    {
      "id": 31,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 46558,
      "players": [
        10686,
        10920,
        12696,
        46558,
        11381,
        11395,
        11396,
        48465,
        12712,
        10855,
        11306
      ]
    },
    {
      "id": 32,
      "name": "4-7",
      "captain": 46558,
      "vice_captain": 11396,
      "players": [
        10686,
        10920,
        12696,
        46558,
        11381,
        11396,
        11395,
        48465,
        12712,
        10855,
        11306
      ]
    },
    {
      "id": 33,
      "name": "4-7",
      "captain": 11395,
      "vice_captain": 46558,
      "players": [
        46614,
        10920,
        12696,
        11395,
        11381,
        46558,
        10855,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 34,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 12712,
      "players": [
        46614,
        10920,
        12696,
        46558,
        11381,
        10855,
        11395,
        48465,
        12712,
        11396,
        11306
      ]
    },
    {
      "id": 35,
      "name": "4-7",
      "captain": 11381,
      "vice_captain": 12712,
      "players": [
        46614,
        10920,
        12696,
        46558,
        11381,
        11396,
        11395,
        12712,
        48465,
        10855,
        11306
      ]
    },
    {
      "id": 36,
      "name": "4-7",
      "captain": 11395,
      "vice_captain": 12712,
      "players": [
        46614,
        10686,
        10853,
        12696,
        11395,
        11381,
        46558,
        11396,
        12712,
        48465,
        10855
      ]
    },
    {
      "id": 37,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 11381,
      "players": [
        10686,
        46614,
        10853,
        12696,
        11395,
        11381,
        11396,
        46558,
        12712,
        48465,
        10855
      ]
    },
    {
      "id": 38,
      "name": "4-7",
      "captain": 11395,
      "vice_captain": 12712,
      "players": [
        46614,
        10853,
        10920,
        11395,
        11381,
        46558,
        10855,
        12712,
        48465,
        11396,
        68521
      ]
    },
    {
      "id": 39,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 46558,
      "players": [
        46614,
        10686,
        12696,
        10855,
        11381,
        46558,
        11395,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 40,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 11381,
      "players": [
        10686,
        46614,
        12696,
        10855,
        11381,
        46558,
        11395,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 41,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 48465,
      "players": [
        46614,
        10686,
        10920,
        12696,
        10855,
        17489,
        11395,
        46558,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 42,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 11395,
      "players": [
        10686,
        46614,
        10920,
        12696,
        11395,
        17489,
        11396,
        46558,
        48465,
        12712,
        10855
      ]
    },
    {
      "id": 43,
      "name": "4-7",
      "captain": 17489,
      "vice_captain": 48465,
      "players": [
        10686,
        46614,
        12696,
        10920,
        46558,
        17489,
        11396,
        11395,
        48465,
        12712,
        10855
      ]
    },
    {
      "id": 44,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 11395,
      "players": [
        10686,
        46614,
        10920,
        10855,
        17489,
        11395,
        46558,
        48465,
        12712,
        11396,
        68521
      ]
    },
    {
      "id": 45,
      "name": "4-7",
      "captain": 11395,
      "vice_captain": 48465,
      "players": [
        10853,
        10920,
        12696,
        11395,
        11381,
        46558,
        10855,
        48465,
        12712,
        11396,
        11306
      ]
    },
    {
      "id": 46,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 11395,
      "players": [
        10853,
        10920,
        12696,
        11395,
        11381,
        46558,
        10855,
        48465,
        12712,
        11396,
        11306
      ]
    },
    {
      "id": 47,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 10855,
      "players": [
        10686,
        10853,
        12696,
        10855,
        11381,
        46558,
        11395,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 48,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 11381,
      "players": [
        10686,
        10853,
        12696,
        11395,
        11381,
        46558,
        10855,
        48465,
        12712,
        11396,
        11306
      ]
    },
    {
      "id": 49,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 11395,
      "players": [
        10853,
        46614,
        12696,
        11395,
        11381,
        46558,
        11396,
        12712,
        48465,
        10855,
        11306
      ]
    },
    {
      "id": 50,
      "name": "4-7",
      "captain": 46558,
      "vice_captain": 12712,
      "players": [
        10686,
        10853,
        10920,
        12696,
        46558,
        17489,
        10855,
        11395,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 51,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 11395,
      "players": [
        10686,
        10853,
        12696,
        10855,
        17489,
        11395,
        46558,
        12712,
        48465,
        11396,
        10920
      ]
    },
    {
      "id": 52,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 17489,
      "players": [
        10686,
        10853,
        10920,
        12696,
        46558,
        17489,
        11395,
        10855,
        48465,
        12712,
        11396
      ]
    },
    {
      "id": 53,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 11395,
      "players": [
        10686,
        10853,
        12696,
        10920,
        10855,
        17489,
        11395,
        46558,
        48465,
        12712,
        11396
      ]
    },
    {
      "id": 54,
      "name": "4-7",
      "captain": 17489,
      "vice_captain": 12712,
      "players": [
        10686,
        10853,
        10920,
        12696,
        46558,
        17489,
        11396,
        11395,
        12712,
        48465,
        10855
      ]
    },
    {
      "id": 55,
      "name": "4-7",
      "captain": 10855,
      "vice_captain": 12712,
      "players": [
        10853,
        46614,
        12696,
        10920,
        10855,
        17489,
        46558,
        11395,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 56,
      "name": "4-7",
      "captain": 17489,
      "vice_captain": 48465,
      "players": [
        10853,
        46614,
        10920,
        12696,
        46558,
        17489,
        11395,
        11396,
        48465,
        12712,
        10855
      ]
    },
    {
      "id": 57,
      "name": "4-7",
      "captain": 17489,
      "vice_captain": 12712,
      "players": [
        46614,
        10853,
        12696,
        46558,
        17489,
        11395,
        10855,
        12712,
        48465,
        11396,
        10920
      ]
    },
    {
      "id": 58,
      "name": "4-7",
      "captain": 17489,
      "vice_captain": 48465,
      "players": [
        46614,
        10853,
        10920,
        12696,
        11395,
        17489,
        46558,
        11396,
        48465,
        12712,
        10855
      ]
    },
    {
      "id": 59,
      "name": "4-7",
      "captain": 17489,
      "vice_captain": 48465,
      "players": [
        46614,
        10853,
        10920,
        12696,
        46558,
        17489,
        11395,
        10855,
        48465,
        12712,
        11396
      ]
    },
    {
      "id": 60,
      "name": "4-7",
      "captain": 17489,
      "vice_captain": 48465,
      "players": [
        46614,
        10920,
        12696,
        11395,
        17489,
        10855,
        46558,
        48465,
        12712,
        11396,
        11306
      ]
    },
    {
      "id": 61,
      "name": "4-7",
      "captain": 46558,
      "vice_captain": 12712,
      "players": [
        46614,
        10920,
        12696,
        46558,
        17489,
        11396,
        11395,
        12712,
        48465,
        10855,
        11306
      ]
    },
    {
      "id": 62,
      "name": "4-7",
      "captain": 46558,
      "vice_captain": 12712,
      "players": [
        10853,
        46614,
        10686,
        12696,
        46558,
        17489,
        10855,
        11395,
        12712,
        48465,
        11396
      ]
    },
    {
      "id": 63,
      "name": "4-7",
      "captain": 11395,
      "vice_captain": 12712,
      "players": [
        10853,
        10920,
        12696,
        11395,
        17489,
        10855,
        46558,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 64,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 11395,
      "players": [
        10853,
        10920,
        12696,
        11395,
        17489,
        10855,
        46558,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 65,
      "name": "4-7",
      "captain": 11395,
      "vice_captain": 48465,
      "players": [
        10853,
        10686,
        12696,
        11395,
        17489,
        10855,
        46558,
        48465,
        12712,
        11396,
        11306
      ]
    },
    {
      "id": 66,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 17489,
      "players": [
        10686,
        10853,
        12696,
        10855,
        17489,
        11395,
        46558,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 67,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 46558,
      "players": [
        10853,
        10686,
        12696,
        46558,
        17489,
        11395,
        10855,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 68,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 11395,
      "players": [
        10686,
        10853,
        12696,
        11395,
        17489,
        46558,
        10855,
        12712,
        48465,
        11396,
        11306
      ]
    },
    {
      "id": 69,
      "name": "4-7",
      "captain": 46558,
      "vice_captain": 48465,
      "players": [
        10853,
        10686,
        12696,
        46558,
        17489,
        11395,
        11396,
        48465,
        12712,
        10855,
        11306
      ]
    },
    {
      "id": 70,
      "name": "4-7",
      "captain": 17489,
      "vice_captain": 48465,
      "players": [
        46614,
        10853,
        12696,
        10855,
        17489,
        46558,
        11395,
        48465,
        12712,
        11396,
        11306
      ]
    },
    {
      "id": 71,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 48465,
      "players": [
        10686,
        10853,
        12696,
        46558,
        11381,
        11395,
        10855,
        12712,
        48465,
        11396,
        12830
      ]
    },
    {
      "id": 72,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 12712,
      "players": [
        10853,
        10686,
        12696,
        10855,
        11381,
        11395,
        46558,
        48465,
        12712,
        11396,
        12830
      ]
    },
    {
      "id": 73,
      "name": "4-7",
      "captain": 46558,
      "vice_captain": 11396,
      "players": [
        10853,
        46614,
        12696,
        46558,
        11381,
        11396,
        11395,
        48465,
        12712,
        10855,
        97321
      ]
    },
    {
      "id": 74,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 11395,
      "players": [
        46614,
        10853,
        12696,
        11395,
        11381,
        11396,
        46558,
        48465,
        12712,
        10855,
        97321
      ]
    },
    {
      "id": 75,
      "name": "4-7",
      "captain": 48465,
      "vice_captain": 17489,
      "players": [
        10853,
        10920,
        12696,
        46558,
        17489,
        11395,
        11396,
        48465,
        12712,
        10855,
        12830
      ]
    },
    {
      "id": 76,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 10855,
      "players": [
        46614,
        10920,
        12696,
        10855,
        17489,
        11395,
        46558,
        12712,
        48465,
        11396,
        68521
      ]
    },
    {
      "id": 77,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 48465,
      "players": [
        10853,
        10686,
        12696,
        46558,
        17489,
        11395,
        11396,
        12712,
        48465,
        10855,
        97321
      ]
    },
    {
      "id": 78,
      "name": "4-7",
      "captain": 12712,
      "vice_captain": 48465,
      "players": [
        10853,
        46614,
        12696,
        46558,
        17489,
        11395,
        10855,
        12712,
        48465,
        11396,
        12830
      ]
    },
    {
      "id": 79,
      "name": "4-7",
      "captain": 17489,
      "vice_captain": 12712,
      "players": [
        46614,
        10853,
        12696,
        10855,
        17489,
        11395,
        46558,
        12712,
        48465,
        11396,
        12830
      ]
    }
  ]
def add_all_teams(num_teams=None):
    """Add teams to Dream11 using edit team API
    
    Args:
        num_teams (int, optional): Number of teams to add. If None, adds all teams.
    """
    success_count = 0
    failed_teams = []
    
    # Determine how many teams to process
    if num_teams is None:
        teams_to_process = teams_data
        total_teams = len(teams_data)
    else:
        teams_to_process = teams_data[:num_teams]
        total_teams = min(num_teams, len(teams_data))
    
    print(f"🏏 Adding Dream11 Teams")
    print("=" * 60)
    print(f"📊 Teams to add: {total_teams} out of {len(teams_data)} available")
    print(f"🎯 Match ID: {MATCH_ID}")
    print(f"🔑 Auth Token: {AUTH_TOKEN[:50]}...")
    print()
    
    # Start with team ID 1 and increment only on success
    current_team_id = 1
    
    for i, team_data in enumerate(teams_to_process, 1):
        print(f"\n📤 Adding team {i}/{total_teams}: {team_data['name']} (ID: {current_team_id})")
        print(f"   👑 Captain: {team_data['captain']}")
        print(f"   🥈 Vice-Captain: {team_data['vice_captain']}")
        print(f"   👥 Players: {len(team_data['players'])} players")
        
        result = edit_dream11_team(
            MATCH_ID,
            current_team_id,  # Use current_team_id instead of team_data['id']
            team_data['captain'],
            team_data['vice_captain'],
            team_data['players'],
            AUTH_TOKEN
        )
        
        if result:
            if isinstance(result, dict) and result.get('status') == 'success':
                print(f"   ✅ Team {i} added successfully with ID {current_team_id}!")
                if result.get('status_code') == 200:
                    print("   📦 Received 200 OK (Success)")
                elif result.get('status_code') == 204:
                    print("   📦 Received 204 No Content (Success)")
                success_count += 1
                current_team_id += 1  # Only increment ID on success
            else:
                print(f"   ⚠️ Team {i} - Unexpected response: {result}")
                failed_teams.append({"team": i, "name": team_data['name'], "id": current_team_id})
                # Don't increment current_team_id on failure
        else:
            print(f"   ❌ Failed to add team {i}")
            failed_teams.append({"team": i, "name": team_data['name'], "id": current_team_id})
            # Don't increment current_team_id on failure
        
        # Small delay between requests to avoid rate limiting
        if i < total_teams:  # Don't delay after the last team
            print("   ⏳ Waiting 1 second...")
            time.sleep(1)
    
    # Final summary
    print("\n" + "="*60)
    print("🏁 FINAL SUMMARY")
    print("="*60)
    print(f"✅ Successfully added: {success_count}/{total_teams} teams")
    print(f"❌ Failed: {len(failed_teams)} teams")
    print(f"📊 Success rate: {(success_count/total_teams)*100:.1f}%")
    
    if failed_teams:
        print(f"\n❌ Failed teams:")
        for failed in failed_teams:
            print(f"   - Team {failed['team']}: {failed['name']} (ID: {failed['id']})")
        
        print(f"\n🔄 To retry failed teams, run:")
        print(f"   python add_all_40_teams.py --retry")
        
        # Save failed team IDs to a file for easy retry
        failed_ids = [str(failed['id']) for failed in failed_teams]
        with open('failed_teams.txt', 'w') as f:
            f.write(','.join(failed_ids))
        print(f"💾 Failed team IDs saved to 'failed_teams.txt'")
    else:
        print(f"\n🎉 All teams added successfully!")
        # Clean up failed teams file if it exists
        if os.path.exists('failed_teams.txt'):
            os.remove('failed_teams.txt')
            print("🧹 Cleaned up previous failed teams file")
    
    return success_count, failed_teams

def retry_failed_teams(failed_team_ids=None):
    """Retry adding specific teams"""
    print("🔄 Retrying failed teams...")
    
    if failed_team_ids is None:
        # Try to load from file
        if os.path.exists('failed_teams.txt'):
            with open('failed_teams.txt', 'r') as f:
                failed_team_ids = [int(id.strip()) for id in f.read().split(',') if id.strip().isdigit()]
            print(f"📂 Loaded {len(failed_team_ids)} failed team IDs from file")
        else:
            print("❌ No failed teams file found and no IDs provided")
            return
    
    retry_teams = [team for team in teams_data if team['id'] in failed_team_ids]
    
    if not retry_teams:
        print("❌ No matching teams found to retry")
        return
    
    print(f"🎯 Found {len(retry_teams)} teams to retry")
    
    success_count = 0
    current_retry_id = 1  # Start retry IDs from 1
    
    for team_data in retry_teams:
        print(f"\n🔄 Retrying team: {team_data['name']} (New ID: {current_retry_id})")
        
        result = edit_dream11_team(
            MATCH_ID,
            current_retry_id,  # Use sequential ID for retry
            team_data['captain'],
            team_data['vice_captain'],
            team_data['players'],
            AUTH_TOKEN
        )
        
        if result and isinstance(result, dict) and result.get('status') == 'success':
            print(f"   ✅ Retry successful with ID {current_retry_id}!")
            success_count += 1
            current_retry_id += 1  # Only increment on success
        else:
            print(f"   ❌ Retry failed for ID {current_retry_id}")
            # Don't increment current_retry_id on failure
        
        time.sleep(1)
    
    print(f"\n🏁 Retry Summary: {success_count}/{len(retry_teams)} teams successful")

def get_user_input():
    """Get user input for number of teams to update"""
    print("🏏 Dream11 Team Updater")
    print("=" * 40)
    print(f"📊 Available teams: {len(teams_data)}")
    
    # Show first few teams as preview
    print("\n📋 Team Preview (first 5 teams):")
    for i, team in enumerate(teams_data[:5], 1):
        print(f"   {i}. {team['name']} (ID: {team['id']}) - Captain: {team['captain']}")
    
    if len(teams_data) > 5:
        print(f"   ... and {len(teams_data) - 5} more teams")
    
    print("\n💡 Options:")
    print("   • Enter a number (1-{}) to update that many teams".format(len(teams_data)))
    print("   • Enter 'all' to update all teams")
    print("   • Enter 'preview' to see all team details")
    print("   • Press Ctrl+C to exit")
    print()
    
    while True:
        try:
            user_input = input(f"How many teams do you want to update? ").strip().lower()
            
            if user_input == 'all':
                return None  # None means all teams
            elif user_input == 'preview':
                print("\n📋 All Available Teams:")
                print("-" * 60)
                for i, team in enumerate(teams_data, 1):
                    print(f"   {i:2d}. {team['name']} (ID: {team['id']})")
                    print(f"       👑 Captain: {team['captain']} | 🥈 VC: {team['vice_captain']}")
                    print(f"       👥 Players: {team['players']}")
                    print()
                print("-" * 60)
                continue  # Ask again after showing preview
            elif user_input.isdigit():
                num_teams = int(user_input)
                if 1 <= num_teams <= len(teams_data):
                    # Confirm selection
                    print(f"\n✅ You selected to update {num_teams} team(s)")
                    print("📋 Teams that will be updated:")
                    for i, team in enumerate(teams_data[:num_teams], 1):
                        print(f"   {i}. {team['name']} (ID: {team['id']})")
                    
                    confirm = input(f"\nProceed with updating {num_teams} team(s)? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        return num_teams
                    else:
                        print("❌ Operation cancelled. Please select again.")
                        continue
                else:
                    print(f"❌ Please enter a number between 1 and {len(teams_data)}")
            else:
                print("❌ Please enter a valid number, 'all', or 'preview'")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            exit(0)
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    import os
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--retry":
            # Retry mode - can use saved file or manual input
            if os.path.exists('failed_teams.txt'):
                print("📂 Found failed teams file")
                use_file = input("Use saved failed teams? (y/n): ").strip().lower()
                if use_file in ['y', 'yes']:
                    retry_failed_teams()  # Will load from file
                else:
                    retry_ids = input("Enter team IDs to retry (comma-separated): ").split(",")
                    retry_ids = [int(id.strip()) for id in retry_ids if id.strip().isdigit()]
                    retry_failed_teams(retry_ids)
            else:
                retry_ids = input("Enter team IDs to retry (comma-separated): ").split(",")
                retry_ids = [int(id.strip()) for id in retry_ids if id.strip().isdigit()]
                retry_failed_teams(retry_ids)
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("🏏 Dream11 Team Updater - Usage:")
            print("  python add_all_40_teams.py                    # Interactive mode")
            print("  python add_all_40_teams.py --retry            # Retry failed teams")
            print("  python add_all_40_teams.py --num 10           # Update specific number of teams")
            print("  python add_all_40_teams.py --all              # Update all teams")
            print("  python add_all_40_teams.py --help             # Show this help")
        elif sys.argv[1] == "--num" and len(sys.argv) > 2:
            # Command line mode with specific number
            try:
                num_teams = int(sys.argv[2])
                if 1 <= num_teams <= len(teams_data):
                    success_count, failed_teams = add_all_teams(num_teams)
                else:
                    print(f"❌ Number must be between 1 and {len(teams_data)}")
            except ValueError:
                print("❌ Please provide a valid number after --num")
        elif sys.argv[1] == "--all":
            # Command line mode for all teams
            success_count, failed_teams = add_all_teams()
        else:
            print("❌ Unknown option. Use --help for usage information.")
    else:
        # Interactive mode - ask user for input
        num_teams = get_user_input()
        success_count, failed_teams = add_all_teams(num_teams)