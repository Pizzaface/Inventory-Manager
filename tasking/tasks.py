from huey import crontab, RedisHuey
import json
import requests
# from services.interactionModel import InteractionModel
# from tasking.config import huey

huey = RedisHuey()

@huey.task()
def callCodeChef(templateJSON, skill_id, headers):
	print(json.dumps(templateJSON))
	r = requests.post("https://th32bfoel0.execute-api.us-east-1.amazonaws.com/development", json=templateJSON)
	if r.status_code == 200:
		r = requests.put("https://api.amazonalexa.com/v1/skills/%s/stages/development/enablement" % (skill_id), headers=headers)

		print(r.text)
		if r.status_code == 204:
			return True
		else:
			return False

# @huey.task()
# def uploadFile(filename)

# from models.node import Node