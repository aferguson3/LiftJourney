from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoints:
    garmin_all_day_stress_url = "/wellness-service/wellness/dailyStress"
    # Activities
    garmin_connect_activities = "/activitylist-service/activities/search/activities"
    garmin_connect_activity = "/activity-service/activity"
    garmin_connect_activity_fordate = "/mobile-gateway/heartRate/forDate"
    garmin_connect_activity_types = "/activity-service/activity/activityTypes"
    # /activity-service/activity/{activityID}/{path} Endpoints
    # path =
    #   "": gives health stats (cals, hr, sets, activityName, etc) from the activity
    #   "exerciseSets": recorded sets from the workout session
    #   "workouts": provides the workout name and planned exercises
    #   "typedsplits", "split_summaries", "details", "connectIQDisplayInfo", "jumpDetails", "powerTimeInZones",
    #   "hrTimeInZones", "laps",
    # Badges
    garmin_connect_adhoc_challenges_url = "/adhocchallenge-service/adHocChallenge/historical"
    garmin_connect_available_badge_challenges_url = "/badgechallenge-service/badgeChallenge/available"
    garmin_connect_badge_challenges_url = "/badgechallenge-service/badgeChallenge/completed"
    garmin_connect_earned_badges_url = "/badge-service/badge/earned"
    garmin_connect_inprogress_virtual_challenges_url = "/badgechallenge-service/virtualChallenge/inProgress"
    garmin_connect_non_completed_badge_challenges_url = "/badgechallenge-service/badgeChallenge/non-completed"
    garmin_connect_goals_url = "/goal-service/goal/goals"
    # BP
    garmin_connect_blood_pressure_endpoint = "/bloodpressure-service/bloodpressure/range"
    garmin_connect_set_blood_pressure_endpoint = "/bloodpressure-service/bloodpressure"
    garmin_connect_hrv_url = "/hrv-service/hrv"
    # Daily Stats
    garmin_connect_daily_body_battery_url = "/wellness-service/wellness/bodyBattery/reports/daily"
    garmin_connect_daily_hydration_url = "/usersummary-service/usersummary/hydration/daily"
    garmin_connect_daily_respiration_url = "/wellness-service/wellness/daily/respiration"
    garmin_connect_daily_sleep_url = "/wellness-service/wellness/dailySleepData"
    garmin_connect_daily_spo2_url = "/wellness-service/wellness/daily/spo2"
    garmin_connect_daily_stats_steps_url = "/usersummary-service/stats/steps/daily"
    garmin_connect_daily_stress_url = "/wellness-service/wellness/dailyStress"
    garmin_connect_daily_summary_url = "/usersummary-service/usersummary/daily"
    garmin_connect_floors_chart_daily_url = "/wellness-service/wellness/floorsChartData/daily"
    garmin_connect_heartrates_daily_url = "/wellness-service/wellness/dailyHeartRate"
    garmin_connect_rhr_url = "/userstats-service/wellness/daily"
    garmin_connect_metrics_url = "/metrics-service/metrics/maxmet/daily"
    garmin_connect_user_summary_chart = "/wellness-service/wellness/dailySummaryChart"
    # Device Info
    garmin_connect_device_url = "/device-service/deviceservice"
    garmin_connect_devices_url = "/device-service/deviceregistration/devices"
    # Download/Upload
    garmin_connect_csv_download = "/download-service/export/csv/activity"
    garmin_connect_endurance_score_url = "/metrics-service/metrics/endurancescore"
    garmin_connect_fit_download = "/download-service/files/activity"
    garmin_connect_gpx_download = "/download-service/export/gpx/activity"
    garmin_connect_kml_download = "/download-service/export/kml/activity"
    garmin_connect_tcx_download = "/download-service/export/tcx/activity"
    garmin_connect_upload = "/upload-service/upload"
    # Gear
    garmin_connect_gear = "/gear-service/gear/filterGear"
    garmin_connect_gear_baseurl = "/gear-service/gear/"
    # Misc
    garmin_connect_fitnessstats = "/fitnessstats-service/activity"
    garmin_connect_hill_score_url = "/metrics-service/metrics/hillscore"
    garmin_connect_personal_record_url = "/personalrecord-service/personalrecord/prs"
    garmin_connect_race_predictor_url = "/metrics-service/metrics/racepredictions"
    garmin_connect_weight_url = "/weight-service"
    garmin_request_reload_url = "/wellness-service/wellness/epoch/request"
    garmin_workouts = "/workout-service"
    garmin_connect_training_readiness_url = "/metrics-service/metrics/trainingreadiness"
    garmin_connect_training_status_url = "/metrics-service/metrics/trainingstatus/aggregated"
    garmin_connect_user_settings_url = "/userprofile-service/userprofile/user-settings"
