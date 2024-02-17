import logging
from dataclasses import dataclass
from datetime import date

import garth

from src.Endpoints import Endpoints
from src.auth import client_auth

logging.basicConfig(level=logging.DEBUG)


@dataclass
class ExerciseSet:
    exerciseName: str
    numReps: int
    weight_grams: float
    duration_secs: float
    stepIndex: int
    startTime: str


def main():
    client_auth()
    startDate = '2023-11-01'
    endDate = date.today().isoformat()
    limit = 999

    params = {
        "startDate": str(startDate),
        "endDate": str(endDate),
        "start": 0,
        "limit": str(limit),
        "activityType": "fitness_equipment"
    }
    # Gathers all fitness activities by date
    activity_data = garth.connectapi(f"{Endpoints.garmin_connect_activities}", params=params)

    activityIds, removedIds = list(), list()
    # Gathers collected activityIDs but excludes the basketball events
    for activity in activity_data:
        if (activity["activityName"] == "Pickup" or activity["activityName"] == "Basketball Workout" or
                activity["activityName"] == "Basketball"):
            removedIds.append(activity["activityId"])
            continue
        activityIds.append(activity["activityId"])

    logging.debug(f"Max limit for Ids: {limit}")
    logging.debug(f"Number of Ids: {len(activityIds)}\n{activityIds}")
    logging.debug(f"Number of Removed Ids: {len(removedIds)}\n{removedIds}")

    a_set = ExerciseSet
    allSets = list()
    for Id in activityIds:
        data = garth.connectapi(f"{Endpoints.garmin_connect_activity}/{Id}/exerciseSets")
        for currSet in data["exerciseSets"]:
            if currSet["setType"] == "REST" or currSet["exercises"]["category"] == "INDOOR_BIKE":
                continue
            a_set.exerciseName = currSet["exercises"]["name"]
            a_set.duration_secs = currSet["duration"]
            a_set.numReps = currSet["repetitionCount"]
            a_set.weight_grams = currSet["weight"]
            a_set.startTime = currSet["startTime"]
            a_set.stepIndex = currSet["wktStepIndex"]
            allSets.append(a_set)

    # Result: {"activityId": 13975059216, "exerciseSets": [{"exercises": [{"category": "INDOOR_BIKE", "name": false, "probability": 100.0}], "duration": 173.84, "repetitionCount": false, "weight": 0.0, "setType": "ACTIVE", "startTime": "2024-02-15T13:31:41.0", "wktStepIndex": 0, "messageIndex": 0}, {"exercises": [], "duration": 528.186, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T13:34:35.0", "wktStepIndex": 1, "messageIndex": 1}, {"exercises": [{"category": "DEADLIFT", "name": "BARBELL_DEADLIFT", "probability": 100.0}], "duration": 310.434, "repetitionCount": 9, "weight": 61234.0, "setType": "ACTIVE", "startTime": "2024-02-15T13:43:23.0", "wktStepIndex": 2, "messageIndex": 2}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T13:48:33.0", "wktStepIndex": 3, "messageIndex": 3}, {"exercises": [{"category": "DEADLIFT", "name": "BARBELL_DEADLIFT", "probability": 100.0}], "duration": 422.378, "repetitionCount": 4, "weight": 93000.0, "setType": "ACTIVE", "startTime": "2024-02-15T13:50:03.0", "wktStepIndex": 4, "messageIndex": 4}, {"exercises": [], "duration": 150.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T13:57:06.0", "wktStepIndex": 5, "messageIndex": 5}, {"exercises": [{"category": "DEADLIFT", "name": "BARBELL_DEADLIFT", "probability": 100.0}], "duration": 474.054, "repetitionCount": 10, "weight": 93000.0, "setType": "ACTIVE", "startTime": "2024-02-15T13:59:36.0", "wktStepIndex": 4, "messageIndex": 6}, {"exercises": [], "duration": 150.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:07:30.0", "wktStepIndex": 5, "messageIndex": 7}, {"exercises": [{"category": "DEADLIFT", "name": "BARBELL_DEADLIFT", "probability": 100.0}], "duration": 371.585, "repetitionCount": 1, "weight": 124750.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:10:00.0", "wktStepIndex": 4, "messageIndex": 8}, {"exercises": [], "duration": 150.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:16:11.0", "wktStepIndex": 5, "messageIndex": 9}, {"exercises": [{"category": "PULL_UP", "name": false, "probability": 100.0}], "duration": 115.384, "repetitionCount": 6, "weight": false, "setType": "ACTIVE", "startTime": "2024-02-15T14:18:41.0", "wktStepIndex": 7, "messageIndex": 10}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:20:37.0", "wktStepIndex": 8, "messageIndex": 11}, {"exercises": [{"category": "PULL_UP", "name": false, "probability": 100.0}], "duration": 134.868, "repetitionCount": 5, "weight": false, "setType": "ACTIVE", "startTime": "2024-02-15T14:22:07.0", "wktStepIndex": 7, "messageIndex": 12}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:24:22.0", "wktStepIndex": 8, "messageIndex": 13}, {"exercises": [{"category": "PULL_UP", "name": false, "probability": 100.0}], "duration": 220.124, "repetitionCount": 4, "weight": false, "setType": "ACTIVE", "startTime": "2024-02-15T14:25:52.0", "wktStepIndex": 7, "messageIndex": 14}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:29:32.0", "wktStepIndex": 8, "messageIndex": 15}, {"exercises": [{"category": "SHRUG", "name": "BARBELL_SHRUG", "probability": 100.0}], "duration": 335.055, "repetitionCount": 10, "weight": 124750.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:31:02.0", "wktStepIndex": 10, "messageIndex": 16}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:36:37.0", "wktStepIndex": 11, "messageIndex": 17}, {"exercises": [{"category": "SHRUG", "name": "BARBELL_SHRUG", "probability": 100.0}], "duration": 112.418, "repetitionCount": 2, "weight": 124750.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:38:07.0", "wktStepIndex": 10, "messageIndex": 18}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:39:59.0", "wktStepIndex": 11, "messageIndex": 19}, {"exercises": [{"category": "SHRUG", "name": "BARBELL_SHRUG", "probability": 100.0}], "duration": 137.247, "repetitionCount": 3, "weight": 124750.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:41:29.0", "wktStepIndex": 10, "messageIndex": 20}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:43:46.0", "wktStepIndex": 11, "messageIndex": 21}, {"exercises": [{"category": "FLYE", "name": "DUMBBELL_FLYE", "probability": 100.0}], "duration": 304.408, "repetitionCount": 7, "weight": 15875.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:45:16.0", "wktStepIndex": 13, "messageIndex": 22}, {"exercises": [], "duration": 60.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:50:21.0", "wktStepIndex": 14, "messageIndex": 23}, {"exercises": [{"category": "FLYE", "name": "DUMBBELL_FLYE", "probability": 100.0}], "duration": 188.738, "repetitionCount": 4, "weight": 15875.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:51:21.0", "wktStepIndex": 13, "messageIndex": 24}, {"exercises": [], "duration": 10.381, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:54:29.0", "wktStepIndex": 14, "messageIndex": 25}, {"exercises": [{"category": "FLYE", "name": "DUMBBELL_FLYE", "probability": 100.0}], "duration": 142.55, "repetitionCount": 4, "weight": 15875.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:54:40.0", "wktStepIndex": 13, "messageIndex": 26}, {"exercises": [], "duration": 60.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T14:57:02.0", "wktStepIndex": 14, "messageIndex": 27}, {"exercises": [{"category": "CURL", "name": "DUMBBELL_BICEPS_CURL", "probability": 100.0}], "duration": 233.782, "repetitionCount": 5, "weight": 18125.0, "setType": "ACTIVE", "startTime": "2024-02-15T14:58:03.0", "wktStepIndex": 16, "messageIndex": 28}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:01:56.0", "wktStepIndex": 17, "messageIndex": 29}, {"exercises": [{"category": "CURL", "name": "DUMBBELL_BICEPS_CURL", "probability": 100.0}], "duration": 168.787, "repetitionCount": 7, "weight": 18125.0, "setType": "ACTIVE", "startTime": "2024-02-15T15:03:26.0", "wktStepIndex": 16, "messageIndex": 30}, {"exercises": [], "duration": 90.0, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:06:15.0", "wktStepIndex": 17, "messageIndex": 31}, {"exercises": [{"category": "CURL", "name": "DUMBBELL_BICEPS_CURL", "probability": 100.0}], "duration": 80.746, "repetitionCount": 3, "weight": 18125.0, "setType": "ACTIVE", "startTime": "2024-02-15T15:07:45.0", "wktStepIndex": 16, "messageIndex": 32}, {"exercises": [], "duration": 137.668, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:09:06.0", "wktStepIndex": 17, "messageIndex": 33}, {"exercises": [{"category": "ROW", "name": "BENT_OVER_ROW_WITH_BARBELL", "probability": 100.0}], "duration": 138.44, "repetitionCount": 2, "weight": 83937.0, "setType": "ACTIVE", "startTime": "2024-02-15T15:11:23.0", "wktStepIndex": false, "messageIndex": 35}, {"exercises": [], "duration": 216.267, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:13:42.0", "wktStepIndex": false, "messageIndex": 36}, {"exercises": [{"category": "ROW", "name": "BENT_OVER_ROW_WITH_BARBELL", "probability": 100.0}], "duration": 128.323, "repetitionCount": 6, "weight": 61250.0, "setType": "ACTIVE", "startTime": "2024-02-15T15:17:18.0", "wktStepIndex": false, "messageIndex": 37}, {"exercises": [], "duration": 163.336, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:19:27.0", "wktStepIndex": false, "messageIndex": 38}, {"exercises": [{"category": "ROW", "name": "BENT_OVER_ROW_WITH_BARBELL", "probability": 100.0}], "duration": 61.06, "repetitionCount": 6, "weight": 61250.0, "setType": "ACTIVE", "startTime": "2024-02-15T15:22:10.0", "wktStepIndex": false, "messageIndex": 39}, {"exercises": [], "duration": 15.818, "repetitionCount": false, "weight": false, "setType": "REST", "startTime": "2024-02-15T15:23:11.0", "wktStepIndex": false, "messageIndex": 40}]}


if __name__ == "__main__":
    main()
