# flake8: noqa

from pydantic import BaseModel, Field
from typing import List


####################
# Metadata Prompts
####################
class Metadata(BaseModel):
    title: str = Field(description="The title of the interview")
    interviewer_names: List[str] = Field(
        description="List of the names of the interviewers")
    interviewee_names: List[str] = Field(
        description="List of the names of the interviewees")


METADATA_SCHEMA = Metadata.schema_json()

METADATA_PROMPT_TEMPLATE = """The following are summaries of various sections of an interview. Please fill out the Interview Title, Interviewee Names and Interviewer Names. Title should contain the Interviewee Name. The output should be formatted as a JSON instance that conforms to the JSON schema below.

Output JSON Schema: ###
{schema}
###

Summaries: ###
{summaries}
###
"""

####################
# Summary Prompts
####################
SUMMARY_CHUNK_PROMPT_TEMPLATE = """The following is a section of an interview transcript. Please provide a summary. For each phrase in the output, also specify in parenthesis the exact index of where that information comes from in the source. When listing indexes in parentheses, mention all the locations the info is mentioned, even if repeated. Only answer truthfully and don't include anything not in the original input:

INPUT 1: ###
[0] Ben: Can you tell us your living situation?
[1] Wil: Yeah I'm married with two kids. 8 years old girl.
[2] Wil: Five-year- old boy. We own our house. Recently paid off the mortgage in full.
[3] Wil: I had an inheritance lately. So we took all that money and paid off the mortgage.
[4] Wil: Yeah. So we own our single family home. Here in the Denver area, we have quite a few assets.
[5] Wil: But yeah two kids.
###
OUTPUT 1: ###
Wil is married with two kids - an 8-year-old girl and a 5-year-old boy (1,2,5). They own a single-family home in the Denver area (4), and recently paid off the mortgage in full using an inheritance (2,3). They have several other assets as well (4).
###

INPUT 2: ###
{text}
###
OUTPUT 2: ###

###
"""

SUMMARY_PROMPT_TEMPLATE = """Write a detailed synopsis based on the following notes. Each sentence should be short and contain only one piece of data. For each phrase in the output, also specify in parenthesis the exact index of where that information comes from in the source. When listing indexes in parentheses, mention all the locations the info is mentioned, even if repeated. Only answer truthfully and don't include anything not in the original input:

INPUT 1: ###
[0] Ben: Can you tell us your living situation?
[1] Wil: Yeah I'm married with two kids. 8 years old girl.
[2] Wil: Five-year- old boy. We own our house. Recently paid off the mortgage in full.
[3] Wil: I had an inheritance lately. So we took all that money and paid off the mortgage.
[4] Wil: Yeah. So we own our single family home. Here in the Denver area, we have quite a few assets.
[5] Wil: But yeah two kids.
###
OUTPUT 1: ###
Wil is married with two kids - an 8-year-old girl and a 5-year-old boy (1,2,5). They own a single-family home in the Denver area (4), and recently paid off the mortgage in full using an inheritance (2,3). They have several other assets as well (4).
###

INPUT 2: ###
{text}
###
OUTPUT 2: ###

###
"""

####################
# Concise Prompts
####################
CONCISE_PROMPT_TEMPLATE = """The following is a section of an interview transcript. Please clean it up but still in dialogue form. The speaker name should always be preserved. Do not add any details not present in the original transcript. For each phrase in the output, also specify in parenthesis the exact index of where that information comes from in the source. When listing indexes in parentheses, mention all the locations the info is mentioned, even if repeated. Only answer truthfully and don't include anything not in the original input:

INPUT 1: ###
[0] Drew: Hey, I just I'm from Denver Colorado. What? Part of the world are you and Wilbert from so?
[1] Saswat: Well actually all three of us grew up in Mumbai. India. Sure. Right.
[2] Saswat: But Robin and I are moving. We're all based in the u.s. now and I'm actually in Dallas right now and I'm moving to San Francisco in in about two weeks.
[3] Drew: I was born and raised in San Francisco, man. You're going to have a nice night out of the country.
[4] Drew: Yeah. Arkansas is a very, very beautiful state. Not talk, not talked about very much.
[5] Wilbert: It is it is.
[6] Drew: All right. So do you see? You guys know that's that's why and Wilbur Wright. I talk a lot.
[7] Saswat: I see that.
[8] Drew: So I know we have 30 minutes. If you guys need to go over 30 minutes, I got time for you.
[9] Saswat: We appreciate it.
[10] Drew: No problem. And if I talk too much, just tell me. Stop awesome. What would you really do?
[11] Saswat: Well, it really appreciate you being candid with us there. Oh yeah, um yes, it would love to understand first a little bit about your background.
[12] Saswat: Can you tell us more about your living situation and you have any dependents?
###
OUTPUT 1: ###
Drew: I'm from Denver Colorado. Where you from? (0)
Saswat: All 3 of us grew up in Mumbai, India. We're based in the US, I'm in Dallas and moving to San Francisco in two weeks. (1,2)
Drew: I was born & raised in San Francisco. You'll have a nice time. Arkansas is a very beautiful state. Not talked about much. I talk a lot, tell me if I talk too much. We have 30 minutes. If you guys need to go over, I have time. (3-10)
Saswat: I really appreciate you being candid. I'd love to understand about your background. Can you tell us about your living situation and do you have any dependents? (11,12)
###

INPUT 2: ###
{text}
###
OUTPUT 2: ###

###
"""

####################
# Query Prompts
####################
QUERY_MESSAGE_SYSTEM = """You are a helpful assistant that provides detailed answers to user queries using the provided context, which consists of excerpts from interviews. For each phrase in the output, also specify in parenthesis the exact index of where that information comes from in the source. When listing indexes in parentheses, mention all the locations the info is mentioned, even if repeated. Only answer truthfully and don't include anything not in the original input."""

QUERY_MESSAGE_USER_EXAMPLE = """CONTEXT:
----
[5] Ben: Can you tell us your living situation?
[6] Wil: Yeah I'm married with two kids.
[6] Wil: 8 years old girl for one.
----
[14] Wil: I had an inheritance lately. So we took all that money and paid off the mortgage.
[15] Wil: Didn't mention my son - five-year- old boy.
[16] Wil: But yeah two kids.
----
QUERY: Tell me about Wil's family.
ANSWER: """

QUERY_MESSAGE_ASSISTANT_EXAMPLE = """Wil is married (6) with two children - an 8-year-old girl, and a 5-year-old boy (7,15-17)"""

QUERY_PROMPT_TEMPLATE = """CONTEXT: {context}
QUERY: {query}
ANSWER: """

QUERY_MESSAGE_TEMPLATE = \
    [
        {
            "role": "system",
            "content": QUERY_MESSAGE_SYSTEM
        },
        {
            "role": "user",
            "content": QUERY_MESSAGE_USER_EXAMPLE
        },
        {
            "role": "assistant",
            "content": QUERY_MESSAGE_ASSISTANT_EXAMPLE
        },
        {
            "role": "user",
            "content": QUERY_PROMPT_TEMPLATE
        }
    ]
