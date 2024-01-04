import vertexai
from vertexai.language_models import TextGenerationModel
import re
import requests
import json
import random

STORY3_STORY_DRAFT_API_ENDPOINT = "https://story3.com/api/v2/stories"
STORY3_TWIST_DRAFT_API_ENDPOINT = "https://story3.com/api/v2/twists"
STORY3_TWIST_PUBLISH_API_ENDPOINT = "https://story3.com/api/v2/twists/"

storyHeaderList = list()

# API calls to gen ai APIs

def get_completion(query):
    query = query["content"]
    print(query)
    vertexai.init(project="<GCP_PROJECT>", location="us-central1")
    parameters = {
        "candidate_count": 1,
        "max_output_tokens": 2048,
        "temperature": 0.8,
        "top_p": 1
    }
    model = TextGenerationModel.from_pretrained("text-bison")
    response = model.predict(query, **parameters)
    return response.text

# API calls to Story 3 for Stories

def storyDraftAPIcall(storyHeader, storyRootText):
   payload = {
        "title": storyHeader,
        "body": storyRootText
    }
   headers = {
        "x-auth-token": "<API_TOKEN_STORY3>"
    }
   response = requests.post(STORY3_STORY_DRAFT_API_ENDPOINT, json=payload, headers=headers)    
   response = response.json()
   print(response)
   return response

def publishStory(hashId):
   headers = {
        "x-auth-token": "<API_TOKEN_STORY3>"
    }
   response = requests.post(STORY3_TWIST_PUBLISH_API_ENDPOINT + hashId + "/publish", headers=headers)    
   response = response.json()
   print(response)
   return response

# API calls to Story 3 for Twists

def twistDraftAPIcall(draftStoryHashId, twistHeader, twist):
   payload = {
        "hashParentId": draftStoryHashId,
        "title": twistHeader,
        "body": twist,
        "isExtraTwist": True
    }
   headers = {
        "x-auth-token": "<API_TOKEN_STORY3>"
    }
   response = requests.post(STORY3_TWIST_DRAFT_API_ENDPOINT, json=payload, headers=headers)    
   response = response.json()
   print(response)
   return response

def publishTwist(hashId):
   headers = {
        "x-auth-token": "<API_TOKEN_STORY3>"
    }
   response = requests.post(STORY3_TWIST_PUBLISH_API_ENDPOINT + hashId + "/publish", headers=headers)    
   response = response.json()
   print(response)
   return response

# Domains
# Fiction
# Non-fiction
# Education
# Blogs
# mystrey
# thriller
# romance
# advneture

mainDomain = "magical realism"

def getDomainForStory():
    query = "Give a random domain or category to write a story on. Only output the domain and no other extra text is required. Domain can be anything from " + mainDomain
    query = query + mainDomain
    user_message = {"role": "user", "content": query}
    response = get_completion(user_message)        
    return response;

def getStoryHeader(domain):
    query = "Generate a random heading of atmost 10 words to write a story on in the domain of " + domain + ". "
    query = query + "The story header should be unique and never used in any online content. "
    query = query + "The story header should not be similar to anything in the list : " + str(storyHeaderList) + ". "
    query = query + "Only output the story heading without quotes or double quotes and no other extra text is required."
    user_message = {"role": "user", "content": query}
    response = get_completion(user_message)        
    return response;

def getStoryRootText(storyHeader):
    query = "Generate a unique story with huge optimism and positive outlook the heading as " + storyHeader + ". "
    query = query + "Keep the story interesting and fresh, do not copy from anywhere and make it an own creation. "
    query = query + "Limit the word limit strictly to 80 words. Do not output anything else and just the content of the story. "
    query = query + "The story should not be disrepecting any community or gender or identitiy. It should also not contain any vulgar stuff and should not a copy of an existing content. "
    # query = query + "Mandatorily introduce proper line endings and replace them with \\n whereever required."
    user_message = {"role": "user", "content": query}
    response = get_completion(user_message)        
    return response;

def getTwistHeader(storyRootText, twistHeaderList):
    query = "Generate a heading of atmost 10 words for the story : " + storyRootText + ". "
    query = query + "The story header should not be similar to anything in the list : " + str(twistHeaderList) + ". "
    query = query + "Only output the twist heading without quotes or double quotes and no other extra text is required."
    user_message = {"role": "user", "content": query}
    response = get_completion(user_message)        
    return response;

def getTwist(twistHeader, storyRootText, endingTwist):
    query = "Generate a unique and interesting twist with huge optimism and positive outlook for this story with the twist header as : " + twistHeader + " and story text : " + storyRootText + ". "
    query = query + "Keep the twist interesting and fresh, do not copy from anywhere and make it an own creation. "
    if (endingTwist):
        query = query + "Also provide a suitable and happy ending to the story within this twist"
    query = query + "Limit the word limit strictly to 80 words. Do not output anything else and just the content of the story. "
    query = query + "The story should not be disrepecting any community or gender or identitiy. It should also not contain any vulgar stuff and should not a copy of an existing content. "
    # query = query + "Mandatorily introduce proper line endings and replace them with \\n whereever required."
    user_message = {"role": "user", "content": query}
    response = get_completion(user_message)        
    return response;

if __name__ == "__main__":
    for i in range(80):
        print("\n----------------------------------------")
        print("Story Line : START : " + str(i+1))
        print("----------------------------------------\n")

        responseDomain = getDomainForStory()
        # domain = responseDomain["choices"][0]["message"]["content"]
        domain = responseDomain
        print("Story Domain : " + domain)

        responseForStoryHeader = getStoryHeader(domain)
        # storyHeader = responseForStoryHeader["choices"][0]["message"]["content"]
        storyHeader = responseForStoryHeader
        if (storyHeader[0] == "\"" and storyHeader[-1] == "\""):
            storyHeader = storyHeader[1:-1]
        storyHeaderList.append(storyHeader)
        print("\nStory Title : " + storyHeader)

        responseStoryRootText = getStoryRootText(storyHeader)
        # storyRootText = responseStoryRootText["choices"][0]["message"]["content"]
        storyRootText = responseStoryRootText
        print("\nStory Line : " + storyRootText)

        # Draft the story to Story 3 
        # Jump out of the loop if there is any error 
        responseStoryDraft = storyDraftAPIcall(storyHeader, storyRootText)
        draftStoryHashId = responseStoryDraft["hashId"]
        print("\nDrafted Story With Hash Id : " + draftStoryHashId)

        # Publish the story to Story3
        responseStoryPublish = publishStory(draftStoryHashId)
        print("\nPublished Story With Hash Id : " + draftStoryHashId)

        twistCount = random.randint(2,3)
        print("\nNumber of twists in story : " + str(twistCount))
        twistHeaderList = list()
        for j in range(twistCount):
            print("\n----------------------------------------")        
            responseTwistHeader = getTwistHeader(storyRootText, twistHeaderList)
            # twistHeader = responseTwistHeader["choices"][0]["message"]["content"]
            twistHeader = responseTwistHeader
            if (twistHeader[0] == "\"" and twistHeader[-1] == "\""):
                twistHeader = twistHeader[1:-1]
            twistHeaderList.append(twistHeader)
            print("Twist Header : " + str(j+1) + " : " + twistHeader)
            responseTwist = getTwist(twistHeader, storyRootText, False)
            # twist = responseTwist["choices"][0]["message"]["content"]
            twist = responseTwist
            print("\nTwist : " + str(j+1) + " : " + twist)
            print("----------------------------------------\n")

            # Draft the twist to Story 3 
            # Jump out of the loop if there is any error 
            responseTwistDraft = twistDraftAPIcall(draftStoryHashId, twistHeader, twist)
            draftTwistHashId = responseTwistDraft["hashId"]
            print("\nDrafted Twist With Hash Id : " + draftTwistHashId)

            # Publish the twist to Story3
            responseTwistPublish = publishTwist(draftTwistHashId)
            print("\nPublished Twist With Hash Id : " + draftTwistHashId)

            # Level Two
            twistCountLevelTwo = random.randint(0,1)
            print("\nNumber of level 2 twists in story : " + str(twistCountLevelTwo))
            for k in range(twistCountLevelTwo):
                print("\n----------------------------------------")        
                responseTwistHeaderLevelTwo = getTwistHeader(storyRootText + " " + twist, twistHeaderList)
                # twistHeaderLevelTwo = responseTwistHeaderLevelTwo["choices"][0]["message"]["content"]
                twistHeaderLevelTwo = responseTwistHeaderLevelTwo
                if (twistHeaderLevelTwo[0] == "\"" and twistHeaderLevelTwo[-1] == "\""):
                    twistHeaderLevelTwo = twistHeaderLevelTwo[1:-1]
                twistHeaderList.append(twistHeaderLevelTwo)
                print("Twist Header Level Two: " + str(k+1) + " : " + twistHeaderLevelTwo)
                responseTwistLevelTwo = getTwist(twistHeaderLevelTwo, storyRootText + " " + twist, True)
                # twistLevelTwo = responseTwistLevelTwo["choices"][0]["message"]["content"]
                twistLevelTwo = responseTwistLevelTwo
                print("\nTwist Level Two: " + str(k+1) + " : " + twistLevelTwo)
                print("----------------------------------------\n")

                # Draft the twist to Story 3 
                # Jump out of the loop if there is any error 
                responseTwistDraftLevelTwo = twistDraftAPIcall(draftTwistHashId, twistHeaderLevelTwo, twistLevelTwo)
                draftTwistHashIdLevelTwo = responseTwistDraftLevelTwo["hashId"]
                print("\nDrafted Twist Level Two With Hash Id : " + draftTwistHashIdLevelTwo)

                # Publish the twist to Story3
                responseTwistPublishLevelTwo = publishTwist(draftTwistHashIdLevelTwo)
                print("\nPublished Twist Level Two With Hash Id : " + draftTwistHashIdLevelTwo)

            print("\n\n\n")

        print("\nTwist Header List : ", twistHeaderList)

        print("\n----------------------------------------")
        print("Story Line : END : " + str(i+1))
        print("----------------------------------------\n")

        print("\n\n\n")      

    print("\nStory Header List : ", storyHeaderList)


