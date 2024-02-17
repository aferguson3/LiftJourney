*Goal* : scrape training data from connect.garmin and interact with stored stats w/ an interface
### Web Scraping
  * Authentication process? 
  * search for any X activity type from date X to the current day
  * be able to filter search based on Garmin activity types (Cardio, Strength Training, Swimming, etc)
  * group activities by the name (Legs X.X.X, Pickup)
  * rate limiting exists?
  * Server(?): 
    * update this search regularly to include future workouts
    * python frameworks: bs or selenium ()
### Frontend interface
  * want to view progress for exercise X, over time
  * shows all exercises performed for each major lifting category
  * charts progress from the first time exercise X is performed for lifting category Y
  * time intervals for chart  (W, M, 3M)
### DB for stats
  * store progress of each scrape
  * future scraps will use stored stats, when possible
### Scraping Info
* class name for each act: inline-edit target
* input class: search-field
* garth support MFA auth and make requests
* use garminconnect for the endpoints
### Garth Doc Structure
* GARTH 
  * ## Data
    * hrv --> HRVData
    * sleep --> SleepData
  * ## Stats
    * hrv --> DailyHRV
    * intensity_minutes --> DailyIntensityMinutes, WeeklyIntensityMinutes
    * sleep --> DailySleep
    * steps --> DailySteps, WeeklySteps
    * stress --> DailyStress, WeeklyStress
  * ## Users
    * profile --> UserProfile
    * settings --> UserSettings
  * http
    * client: (configure, connectapi, download, login, load, dump, upload)
      * connectapi(path, method=GET, **kwargs): sends reqs to Garmin endpoints (path)
  * exc (exceptions)
